#!/usr/bin/env python3
"""
Codex UserPromptSubmit hook: inject concise project context.
"""

import json
import subprocess
from pathlib import Path


def emit(payload):
    print(json.dumps(payload, ensure_ascii=False))


def get_git_info():
    info = {}
    try:
        info["branch"] = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
            timeout=5,
        ).decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        info["branch"] = "unknown (not a git repo)"

    try:
        info["recent_commits"] = subprocess.check_output(
            ["git", "log", "--oneline", "-5"],
            stderr=subprocess.DEVNULL,
            timeout=5,
        ).decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        info["recent_commits"] = ""

    return info


def get_project_state():
    state = {}
    cwd = Path.cwd()

    specs_dir = cwd / "docs" / "specs"
    if specs_dir.exists():
        specs = list(specs_dir.glob("*.md"))
        if specs:
            state["active_specs"] = [
                p.name for p in sorted(specs, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            ]

    contracts_dir = cwd / "docs" / "contracts"
    if contracts_dir.exists():
        contracts = [p for p in contracts_dir.glob("*.md") if p.name != "TEMPLATE.md"]
        if contracts:
            state["active_contracts"] = [
                p.name for p in sorted(contracts, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            ]

    plans_dir = cwd / "docs" / "plans"
    if plans_dir.exists():
        plans = list(plans_dir.glob("*.md"))
        if plans:
            state["active_plans"] = [
                p.name for p in sorted(plans, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            ]

    return state


def get_task_harness_state():
    state = {}
    cwd = Path.cwd()
    feature_list_path = cwd / "feature_list.json"

    if not feature_list_path.exists():
        return state

    try:
        data = json.loads(feature_list_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, ValueError):
        return state

    features = data.get("features", [])
    if not isinstance(features, list):
        return state

    total = len(features)
    passed = sum(1 for feat in features if bool(feat.get("passes")))
    pending = [feat for feat in features if not bool(feat.get("passes"))]

    pending_sorted = sorted(
        pending,
        key=lambda feat: (
            int(feat.get("priority", 10**9)) if str(feat.get("priority", "")).isdigit() else 10**9,
            feat.get("id", ""),
        ),
    )

    state["total_features"] = total
    state["passed_features"] = passed
    state["pending_features"] = max(total - passed, 0)

    if pending_sorted:
        next_feat = pending_sorted[0]
        state["next_feature"] = {
            "id": next_feat.get("id", "unknown"),
            "priority": next_feat.get("priority", "?"),
            "description": next_feat.get("description", ""),
        }

    state["has_task_contract"] = (cwd / "TASK-HARNESS.md").exists()
    state["has_progress_log"] = (cwd / "progress.txt").exists()
    return state


def main():
    parts = []

    git_info = get_git_info()
    if git_info.get("branch"):
        parts.append(f"Git branch: {git_info['branch']}")
    if git_info.get("recent_commits"):
        parts.append(f"Recent commits:\n{git_info['recent_commits']}")

    state = get_project_state()
    if state.get("active_specs"):
        parts.append(f"Active specs: {', '.join(state['active_specs'])}")
    if state.get("active_contracts"):
        parts.append(f"Active contracts: {', '.join(state['active_contracts'])}")
    if state.get("active_plans"):
        parts.append(f"Active plans: {', '.join(state['active_plans'])}")

    task_state = get_task_harness_state()
    if task_state:
        parts.append(
            "Task harness progress: "
            f"{task_state.get('passed_features', 0)}/{task_state.get('total_features', 0)} passed, "
            f"{task_state.get('pending_features', 0)} pending"
        )
        if task_state.get("next_feature"):
            next_feat = task_state["next_feature"]
            parts.append(
                "Next feature: "
                f"[{next_feat.get('id')}] P{next_feat.get('priority')} {next_feat.get('description')}"
            )
        if not task_state.get("has_task_contract"):
            parts.append("Warning: feature_list.json exists but TASK-HARNESS.md is missing.")
        if not task_state.get("has_progress_log"):
            parts.append("Warning: feature_list.json exists but progress.txt is missing.")

    if not parts:
        emit({})
        return

    message = (
        "Project context:\n"
        + "\n".join(parts)
        + "\n\nUse this context to understand project state. "
        + "Read only relevant specs/contracts/plans/task files."
    )

    emit(
        {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": message,
            }
        }
    )


if __name__ == "__main__":
    main()
