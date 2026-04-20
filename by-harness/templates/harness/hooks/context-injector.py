#!/usr/bin/env python3
"""
Context Injector Hook for Harness Engineering Framework.

UserPromptSubmit hook that injects project state context at the start of each session.

This implements the "Context Budget" and "Environment Context Injection" principles
from LangChain's research: agents perform better when they know about their environment,
current state, and active tasks.

Hook output format:
- {"systemMessage": "..."} to inject context without blocking
"""

import json
import subprocess
import sys
from pathlib import Path

HARNESS_DIR_NAME = ".harness"


def get_git_info():
    """Get current git branch and recent commits."""
    info = {}
    try:
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stderr=subprocess.DEVNULL, timeout=5
        ).decode().strip()
        info['branch'] = branch
    except (subprocess.CalledProcessError, FileNotFoundError):
        info['branch'] = 'unknown (not a git repo)'

    try:
        recent = subprocess.check_output(
            ['git', 'log', '--oneline', '-5'],
            stderr=subprocess.DEVNULL, timeout=5
        ).decode().strip()
        info['recent_commits'] = recent
    except (subprocess.CalledProcessError, FileNotFoundError):
        info['recent_commits'] = ''

    return info


def collect_keyed_strings(obj, target_keys):
    found = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.lower() in target_keys and isinstance(value, str) and value.strip():
                found.append(value.strip())
            found.extend(collect_keyed_strings(value, target_keys))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(collect_keyed_strings(item, target_keys))
    return found


def extract_prompt_text(hook_input):
    target_keys = {"prompt", "user_prompt", "message", "text", "content", "input"}
    candidates = collect_keyed_strings(hook_input, target_keys)
    if not candidates:
        return ""
    return sorted(candidates, key=len, reverse=True)[0]


def find_branch_script(repo: Path):
    candidates = [
        repo / HARNESS_DIR_NAME / "scripts" / "ensure_task_branch.py",
        repo / "scripts" / "ensure_task_branch.py",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def run_auto_branch(prompt_text):
    repo = Path.cwd()
    script_path = find_branch_script(repo)
    if script_path is None:
        return "Branch sync: ensure_task_branch.py not found (skip)."

    cmd = ["python3", str(script_path), "--target-dir", str(repo)]
    if prompt_text:
        cmd.extend(["--prompt", prompt_text])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return "Branch sync warning: failed to execute ensure_task_branch.py."

    output = (result.stdout or "").strip()
    if not output:
        output = (result.stderr or "").strip()
    output = output.replace("\r", "")
    if output:
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        output = " | ".join(lines[:4])

    branch_now = "unknown"
    try:
        branch_now = (
            subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
            .decode()
            .strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass

    if result.returncode == 0:
        return f"Branch sync: {output or f'now on {branch_now}'}"
    return f"Branch sync warning: {output or f'failed, current={branch_now}'}"


def get_project_state():
    """Scan for project state indicators."""
    state = {}
    cwd = Path.cwd()
    workspace = cwd / HARNESS_DIR_NAME if (cwd / HARNESS_DIR_NAME).exists() else cwd

    # Check for active specs
    specs_dir = workspace / 'docs' / 'specs'
    if specs_dir.exists():
        specs = list(specs_dir.glob('*.md'))
        if specs:
            state['active_specs'] = [s.name for s in sorted(specs, key=lambda x: x.stat().st_mtime, reverse=True)[:5]]

    # Check for active contracts
    contracts_dir = workspace / 'docs' / 'contracts'
    if contracts_dir.exists():
        contracts = [c for c in contracts_dir.glob('*.md') if c.name != 'TEMPLATE.md']
        if contracts:
            state['active_contracts'] = [c.name for c in sorted(contracts, key=lambda x: x.stat().st_mtime, reverse=True)[:5]]

    # Check for active plans
    plans_dir = workspace / 'docs' / 'plans'
    if plans_dir.exists():
        plans = list(plans_dir.glob('*.md'))
        if plans:
            state['active_plans'] = [p.name for p in sorted(plans, key=lambda x: x.stat().st_mtime, reverse=True)[:5]]

    return state


def get_task_harness_state():
    """Scan task-harness state when feature_list.json exists."""
    state = {}
    cwd = Path.cwd()
    workspace = cwd / HARNESS_DIR_NAME if (cwd / HARNESS_DIR_NAME).exists() else cwd
    workspace_label = f"{HARNESS_DIR_NAME}/" if workspace != cwd else ""
    feature_list_path = workspace / 'feature_list.json'

    if not feature_list_path.exists():
        return state

    try:
        data = json.loads(feature_list_path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError, ValueError):
        return state

    features = data.get('features', [])
    if not isinstance(features, list):
        return state

    total = len(features)
    passed = sum(1 for feat in features if bool(feat.get('passes')))
    pending = [feat for feat in features if not bool(feat.get('passes'))]
    pending_sorted = sorted(
        pending,
        key=lambda feat: (
            int(feat.get('priority', 10**9)) if str(feat.get('priority', '')).isdigit() else 10**9,
            feat.get('id', ''),
        ),
    )

    state['total_features'] = total
    state['passed_features'] = passed
    state['pending_features'] = max(total - passed, 0)
    state['has_task_contract'] = (workspace / 'TASK-HARNESS.md').exists()
    state['has_progress_log'] = (workspace / 'progress.txt').exists()
    state['workspace_label'] = workspace_label

    if pending_sorted:
        next_feat = pending_sorted[0]
        state['next_feature'] = {
            'id': next_feat.get('id', 'unknown'),
            'priority': next_feat.get('priority', '?'),
            'description': next_feat.get('description', ''),
        }

    return state


def main():
    try:
        hook_input = json.loads(sys.stdin.read() or "{}")
    except (json.JSONDecodeError, ValueError):
        hook_input = {}
    prompt_text = extract_prompt_text(hook_input)

    parts = []
    parts.append(run_auto_branch(prompt_text))

    # Git info
    git_info = get_git_info()
    if git_info.get('branch'):
        parts.append(f"Git branch: {git_info['branch']}")
    if git_info.get('recent_commits'):
        parts.append(f"Recent commits:\n{git_info['recent_commits']}")

    # Project state
    state = get_project_state()
    if state.get('active_specs'):
        parts.append(f"Active specs: {', '.join(state['active_specs'])}")
    if state.get('active_contracts'):
        parts.append(f"Active contracts: {', '.join(state['active_contracts'])}")
    if state.get('active_plans'):
        parts.append(f"Active plans: {', '.join(state['active_plans'])}")

    task_state = get_task_harness_state()
    if task_state:
        parts.append(
            "Task harness progress: "
            f"{task_state.get('passed_features', 0)}/{task_state.get('total_features', 0)} passed, "
            f"{task_state.get('pending_features', 0)} pending"
        )
        if task_state.get('next_feature'):
            next_feat = task_state['next_feature']
            parts.append(
                "Next feature: "
                f"[{next_feat.get('id')}] P{next_feat.get('priority')} {next_feat.get('description')}"
            )
        if not task_state.get('has_task_contract'):
            parts.append(
                'Warning: feature_list.json exists but '
                f"{task_state.get('workspace_label', '')}TASK-HARNESS.md is missing."
            )
        if not task_state.get('has_progress_log'):
            parts.append(
                'Warning: feature_list.json exists but '
                f"{task_state.get('workspace_label', '')}progress.txt is missing."
            )
    parts.append(
        "Commit policy reminder: commit/push only on explicit user instruction; "
        "use task-branch by default, and keep commit subject concise."
    )

    if not parts:
        print(json.dumps({}))
        return

    message = (
        "Project context:\n"
        + "\n".join(parts)
        + "\n\nUse this context to understand the current state. "
        + "Read relevant specs/contracts/plans/task files as needed "
        + "(context budget: only read what you need)."
    )

    print(json.dumps({"systemMessage": message}))


if __name__ == '__main__':
    main()
