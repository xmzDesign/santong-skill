#!/usr/bin/env python3
"""
Pre-Completion Checklist Hook for Harness Engineering Framework.

PostToolUse hook that injects a verification reminder when a task is marked complete.

This implements the "Self-Verify First" golden principle from LangChain's research:
models are biased toward their first plausible solution. Forcing a verification
checklist before marking work done catches issues that would otherwise slip through.

Hook output format:
- {"systemMessage": "..."} to inject context without blocking
- {"decision": "block", "reason": "..."} to block completion when passed features miss required artifacts
"""

import json
import sys
from pathlib import Path

HARNESS_DIR_NAME = ".harness"


CHECKLIST = [
    "1. Code compiles/builds without errors?",
    "2. All tests pass (both existing and new)?",
    "3. All acceptance criteria from the contract are met?",
    "4. If this sprint maps to a feature, spec_path and contract_path both exist before passes=true?",
    "5. No debug artifacts left (console.log, TODO, temporary code)?",
    "6. Documentation updated if behavior changed?",
    "7. Do all newly added/modified functions and methods include clear Chinese comments?",
    "8. If Java changed, Java Gate was checked: Service interface/impl, entry dependency direction, MapStruct ERROR, money, PageHelper ordering, Redis TTL, logging/config/secrets?",
    "9. If Java changed, Distributed Java Gate was declared and checked: not triggered with reason, or chapter 14 clauses verified?",
    "10. If Java/MyBatis/SQL changed, convention-check.py --changed-only has no FAIL and WARN is fixed or explained?",
    "11. If frontend/UI changed, frontend-dev-conventions + frontend three-layer rules were read and applied?",
    "12. If frontend/UI changed, no hardcoded colors, unexplained inline style, naked global overrides, missing loading/empty/error/disabled/focus-visible states?",
]

TASK_HARNESS_CHECKLIST = [
    "13. If this sprint maps to active bucket task file, unit tests passed before passes=true?",
    "14. QA report is recorded (non-blocking), and progress logs are updated?",
]


def emit(payload):
    print(json.dumps(payload, ensure_ascii=False))


def find_workspace(cwd: Path) -> Path:
    for current in (cwd, *cwd.parents):
        if current.name == HARNESS_DIR_NAME:
            return current
        harness = current / HARNESS_DIR_NAME
        if harness.exists():
            return harness
    return cwd


def repo_root(workspace: Path) -> Path:
    return workspace.parent if workspace.name == HARNESS_DIR_NAME else workspace


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def resolve_path(workspace: Path, raw_path: str) -> Path:
    raw = str(raw_path or "").strip()
    root = repo_root(workspace)
    if not raw:
        return root / "__missing_artifact_path__"

    path = Path(raw)
    if path.is_absolute():
        return path

    candidates = [root / raw, workspace / raw]
    if raw.startswith(f"{HARNESS_DIR_NAME}/"):
        stripped = raw[len(HARNESS_DIR_NAME) + 1 :]
        candidates.append(workspace / stripped)
        candidates.append(root / stripped)

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def bucket_paths(workspace: Path) -> list[Path]:
    index_path = workspace / "task-harness" / "index.json"
    index = load_json(index_path)
    paths: list[Path] = []
    if isinstance(index, dict):
        for bucket in index.get("buckets", []):
            if not isinstance(bucket, dict):
                continue
            raw_path = str(bucket.get("path", "")).strip()
            if raw_path:
                paths.append(resolve_path(workspace, raw_path))

    paths.extend(
        [
            workspace / "feature_list.json",
            workspace / "task-harness" / "features" / "backlog-core.json",
        ]
    )
    deduped = []
    seen = set()
    for path in paths:
        key = str(path)
        if key not in seen:
            seen.add(key)
            deduped.append(path)
    return deduped


def passed_feature_artifact_errors(workspace: Path) -> list[str]:
    errors = []
    seen = set()
    for bucket_path in bucket_paths(workspace):
        if not bucket_path.exists():
            continue
        data = load_json(bucket_path)
        if not isinstance(data, dict):
            continue
        features = data.get("features", [])
        if not isinstance(features, list):
            continue
        for feature in features:
            if not isinstance(feature, dict) or not bool(feature.get("passes")):
                continue
            feature_id = str(feature.get("id", "unknown")).strip() or "unknown"
            dedupe_key = (feature_id, str(bucket_path))
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            for field_name in ("spec_path", "contract_path"):
                raw_path = str(feature.get(field_name, "")).strip()
                artifact_path = resolve_path(workspace, raw_path)
                if not raw_path or not artifact_path.exists() or not artifact_path.is_file():
                    errors.append(
                        f"- {feature_id}: {field_name} missing -> {raw_path or '(empty)'} "
                        f"(bucket: {bucket_path})"
                    )
    return errors


def main():
    # Read hook input from stdin
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        emit({})
        return

    # Check if this is a TaskUpdate with status=completed
    tool_name = input_data.get('tool_name', '')
    tool_input = input_data.get('tool_input', {})

    if tool_name != 'TaskUpdate':
        emit({})
        return

    status = tool_input.get('status', '')
    if status != 'completed':
        emit({})
        return

    checklist = list(CHECKLIST)
    cwd = Path.cwd()
    workspace = find_workspace(cwd)
    has_task_harness = (workspace / 'task-harness' / 'index.json').exists() or (workspace / 'feature_list.json').exists()
    if has_task_harness:
        checklist.extend(TASK_HARNESS_CHECKLIST)

    artifact_errors = passed_feature_artifact_errors(workspace) if has_task_harness else []
    if artifact_errors:
        message = (
            "Artifact gate failed: features marked passes=true must have real spec and contract files.\n"
            + "\n".join(artifact_errors[:20])
            + ("\n- ... more missing artifacts omitted." if len(artifact_errors) > 20 else "")
            + "\n\nFix by creating/updating the missing spec/contract files, or set passes=false until they exist."
        )
        emit({"decision": "block", "reason": message})
        return

    # Inject pre-completion checklist
    message = (
        "Pre-completion checklist — verify ALL items before confirming done:\n"
        + "\n".join(checklist)
        + "\n\nIf any item fails, fix it before marking the task complete."
    )

    emit({"systemMessage": message})


if __name__ == '__main__':
    main()
