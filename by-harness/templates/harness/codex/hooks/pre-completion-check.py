#!/usr/bin/env python3
"""
Codex Stop hook: enforce one continuation pass with a completion checklist.
"""

import json
import sys
from pathlib import Path

HARNESS_DIR_NAME = ".harness"

CHECKLIST = [
    "1. Code compiles/builds without errors?",
    "2. All tests pass (existing and new)?",
    "3. Acceptance criteria are verified one-by-one?",
    "4. No debug artifacts left (console.log/TODO/temp code)?",
    "5. Docs updated if behavior changed?",
    "6. Do all newly added/modified functions and methods include clear Chinese comments?",
    "7. If Java changed, Java Gate was checked: Service interface/impl, entry dependency direction, MapStruct ERROR, money, PageHelper ordering, Redis TTL, logging/config/secrets?",
    "8. If Java/MyBatis/SQL changed, convention-check.py --changed-only has no FAIL and WARN is fixed or explained?",
    "9. If frontend/UI changed, frontend-dev-conventions + frontend three-layer rules were read and applied?",
    "10. If frontend/UI changed, no hardcoded colors, unexplained inline style, naked global overrides, missing loading/empty/error/disabled/focus-visible states?",
]

TASK_HARNESS_CHECKLIST = [
    "11. If this sprint maps to active bucket task file, unit tests passed before passes=true?",
    "12. QA report is recorded (non-blocking), and progress logs are updated?",
]


def emit(payload):
    print(json.dumps(payload, ensure_ascii=False))


def main():
    try:
        input_data = json.loads(sys.stdin.read() or "{}")
    except (json.JSONDecodeError, ValueError):
        emit({})
        return

    if input_data.get("hook_event_name") != "Stop":
        emit({})
        return

    # Avoid re-blocking when Codex re-enters Stop after a continuation pass.
    if bool(input_data.get("stop_hook_active")):
        emit({})
        return

    checklist = list(CHECKLIST)
    cwd = Path.cwd()
    workspace = cwd / HARNESS_DIR_NAME if (cwd / HARNESS_DIR_NAME).exists() else cwd
    has_task_harness = (workspace / "task-harness" / "index.json").exists() or (workspace / "feature_list.json").exists()
    if has_task_harness:
        checklist.extend(TASK_HARNESS_CHECKLIST)

    emit(
        {
            "decision": "block",
            "reason": (
                "Pre-completion checklist:\n"
                + "\n".join(checklist)
                + "\n\nIf any item fails, fix before claiming completion."
                + "\nCommit/push must be triggered by explicit user instruction."
            ),
        }
    )


if __name__ == "__main__":
    main()
