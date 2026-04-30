#!/usr/bin/env python3
"""
Codex UserPromptSubmit hook: inject concise project context.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

HARNESS_DIR_NAME = ".harness"
SESSION_MODE_SOFT = "soft_reset"
SESSION_MODE_HARD = "hard_new_session"
SQL_ORM_SPECIFIC_RE = re.compile(r"(mapper|mybatis|sql|dao|repository|分页|更新|查询)", re.IGNORECASE)
CODE_TRIGGER_RE = re.compile(r"(build|implement|code|编码|实现)", re.IGNORECASE)
SQL_ORM_RULE_CARD = "\n".join(
    [
        "本轮 SQL/ORM 门禁：",
        "- Java/Spring/MyBatis 改动前先读取 .harness/docs/java-dev-conventions.md。",
        "- SQL 必须写在 XML Mapper，禁止 @Select/@Update/@Insert/@Delete 注解 SQL。",
        "- 查询列必须显式列出，禁止 select *。",
        "- XML 参数必须使用 #{}，禁止 ${}。",
        "- 必须使用 resultMap，禁止 resultClass。",
        "- 行数统计必须使用 count(*)；sum() 必须用 IFNULL/COALESCE 兜底 NULL。",
        "- 更新记录必须维护 update_time。",
        "- 禁止外键、级联和存储过程承载业务逻辑。",
        "- 声称完成前运行 .codex/hooks/convention-check.py --changed-only。",
    ]
)


def emit(payload):
    print(json.dumps(payload, ensure_ascii=False))


def read_hook_input():
    try:
        return json.loads(sys.stdin.read() or "{}")
    except (json.JSONDecodeError, ValueError):
        return {}


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


def should_inject_sql_orm_rules(prompt_text: str) -> bool:
    cwd = Path.cwd()
    workspace = cwd / HARNESS_DIR_NAME if (cwd / HARNESS_DIR_NAME).exists() else cwd
    is_java_project = (workspace / "docs" / "java-dev-conventions.md").exists() and any(
        candidate.exists()
        for candidate in [
            cwd / "pom.xml",
            cwd / "build.gradle",
            cwd / "src" / "main" / "resources",
        ]
    )
    if SQL_ORM_SPECIFIC_RE.search(prompt_text or ""):
        return True
    return is_java_project and bool(CODE_TRIGGER_RE.search(prompt_text or ""))


def _find_branch_script(repo: Path):
    candidates = [
        repo / HARNESS_DIR_NAME / "scripts" / "ensure_task_branch.py",
        repo / "scripts" / "ensure_task_branch.py",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def run_auto_branch(prompt_text: str) -> str:
    repo = Path.cwd()
    script_path = _find_branch_script(repo)
    if script_path is None:
        return "Task sync: ensure_task_branch.py not found (skip)."

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
        return "Task sync warning: failed to execute ensure_task_branch.py."

    output = (result.stdout or "").strip()
    if not output:
        output = (result.stderr or "").strip()
    output = output.replace("\r", "")
    if output:
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        output = " | ".join(lines[:4])

    if result.returncode == 0:
        return f"Task sync: {output or 'ok'}"
    return f"Task sync warning: {output or 'failed'}"


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
    workspace = cwd / HARNESS_DIR_NAME if (cwd / HARNESS_DIR_NAME).exists() else cwd

    specs_dir = workspace / "docs" / "specs"
    if specs_dir.exists():
        specs = list(specs_dir.glob("*.md"))
        if specs:
            state["active_specs"] = [
                p.name for p in sorted(specs, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            ]

    contracts_dir = workspace / "docs" / "contracts"
    if contracts_dir.exists():
        contracts = [p for p in contracts_dir.glob("*.md") if p.name != "TEMPLATE.md"]
        if contracts:
            state["active_contracts"] = [
                p.name for p in sorted(contracts, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            ]

    plans_dir = workspace / "docs" / "plans"
    if plans_dir.exists():
        plans = list(plans_dir.glob("*.md"))
        if plans:
            state["active_plans"] = [
                p.name for p in sorted(plans, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
            ]

    return state


def resolve_task_feature_file(workspace: Path):
    legacy = workspace / "feature_list.json"
    index_path = workspace / "task-harness" / "index.json"
    default_path = workspace / "task-harness" / "features" / "backlog-core.json"

    if not index_path.exists():
        if legacy.exists():
            return legacy, "legacy_feature_list"
        return default_path, "active_bucket"

    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, ValueError):
        if legacy.exists():
            return legacy, "legacy_feature_list"
        return default_path, "active_bucket"

    buckets = index.get("buckets", [])
    active = str(index.get("active_bucket", "") or "")
    rel_path = ""
    if isinstance(buckets, list):
        for bucket in buckets:
            if str(bucket.get("id", "") or "") == active:
                rel_path = str(bucket.get("path", "") or "")
                break
        if not rel_path and buckets:
            rel_path = str((buckets[0] or {}).get("path", "") or "")
    if not rel_path:
        rel_path = "task-harness/features/backlog-core.json"

    candidate = workspace / rel_path
    if candidate.exists():
        return candidate, "active_bucket"
    if rel_path.startswith(f"{HARNESS_DIR_NAME}/"):
        alt = workspace / rel_path[len(HARNESS_DIR_NAME) + 1 :]
        if alt.exists():
            return alt, "active_bucket"

    if legacy.exists():
        return legacy, "legacy_feature_list"
    return default_path, "active_bucket"


def get_task_harness_state():
    state = {}
    cwd = Path.cwd()
    workspace = cwd / HARNESS_DIR_NAME if (cwd / HARNESS_DIR_NAME).exists() else cwd
    workspace_label = f"{HARNESS_DIR_NAME}/" if workspace != cwd else ""
    feature_path, source = resolve_task_feature_file(workspace)

    if not feature_path.exists():
        return state

    try:
        data = json.loads(feature_path.read_text(encoding="utf-8"))
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

    state["has_task_contract"] = (workspace / "docs" / "TASK-HARNESS.md").exists() or (workspace / "TASK-HARNESS.md").exists()
    state["has_progress_log"] = (workspace / "task-harness" / "progress" / "latest.txt").exists() or (workspace / "progress.txt").exists()
    state["workspace_label"] = workspace_label
    state["task_source"] = source
    return state


def normalize_session_mode(raw: str) -> str:
    value = str(raw or "").strip().lower()
    if value in {"hard_new_session", "hard", "new_session"}:
        return SESSION_MODE_HARD
    if value in {"soft_reset", "soft", "reset"}:
        return SESSION_MODE_SOFT
    return SESSION_MODE_SOFT


def get_session_mode(workspace: Path) -> str:
    task_path = workspace / "config" / "task.json"
    if not task_path.exists():
        task_path = workspace / "task.json"
    if not task_path.exists():
        return SESSION_MODE_SOFT
    try:
        data = json.loads(task_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, ValueError):
        return SESSION_MODE_SOFT
    harness = data.get("harness", {})
    if not isinstance(harness, dict):
        return SESSION_MODE_SOFT
    session_control = harness.get("session_control", {})
    if isinstance(session_control, dict):
        mode = session_control.get("mode", "")
        if mode:
            return normalize_session_mode(mode)
    return normalize_session_mode(harness.get("session_mode", ""))


def get_session_context_notice() -> str:
    cwd = Path.cwd()
    workspace = cwd / HARNESS_DIR_NAME if (cwd / HARNESS_DIR_NAME).exists() else cwd
    mode = get_session_mode(workspace)
    context_path = workspace / "config" / "session-context.json"
    if not context_path.exists():
        context_path = workspace / "session-context.json"
    boundary_path = workspace / "config" / "session-boundary.json"
    if not boundary_path.exists():
        boundary_path = workspace / "session-boundary.json"

    if mode == SESSION_MODE_HARD and boundary_path.exists():
        try:
            data = json.loads(boundary_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, ValueError):
            data = {}
        closed_id = str(data.get("closed_feature_id", "n/a"))
        next_id = str(data.get("next_feature_id", "") or "n/a")
        return (
            "Session mode: hard_new_session. "
            f"Boundary active (closed={closed_id}, next={next_id}). "
            "Do not start next feature in this chat."
        )

    if mode == SESSION_MODE_SOFT and context_path.exists():
        try:
            data = json.loads(context_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, ValueError):
            return "Session mode: soft_reset. Session context file exists but parse failed."
        epoch = data.get("epoch", "n/a")
        reset_required = bool(data.get("reset_required"))
        closed_id = str(data.get("closed_feature_id", "n/a"))
        next_id = str(data.get("next_feature_id", "") or "n/a")
        if reset_required:
            return (
                "Session mode: soft_reset. "
                f"Context epoch switched to {epoch} after feature {closed_id}. "
                f"Next feature hint: {next_id}. Ignore stale context from older feature turns."
            )
        return f"Session mode: soft_reset. Current context epoch={epoch}."

    return f"Session mode: {mode}."


def main():
    hook_input = read_hook_input()
    prompt_text = extract_prompt_text(hook_input)

    parts = []
    parts.append(run_auto_branch(prompt_text))
    parts.append(get_session_context_notice())

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
            parts.append(
                "Warning: task harness state exists but "
                f"{task_state.get('workspace_label', '')}docs/TASK-HARNESS.md is missing."
            )
        if not task_state.get("has_progress_log"):
            parts.append(
                "Warning: task harness state exists but "
                f"{task_state.get('workspace_label', '')}task-harness/progress/latest.txt is missing."
            )
    if should_inject_sql_orm_rules(prompt_text):
        parts.append(SQL_ORM_RULE_CARD)
    parts.append(
        "Commit policy reminder: commit/push only on explicit user instruction; "
        "develop on current branch by default, and keep commit subject concise."
    )

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
