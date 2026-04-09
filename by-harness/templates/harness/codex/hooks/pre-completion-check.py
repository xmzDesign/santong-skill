#!/usr/bin/env python3
"""
Codex Stop hook: inject completion checklist before finalizing.
"""

import json
import sys
from pathlib import Path

CHECKLIST = [
    "1. Code compiles/builds without errors?",
    "2. All tests pass (existing and new)?",
    "3. Acceptance criteria are verified one-by-one?",
    "4. No debug artifacts left (console.log/TODO/temp code)?",
    "5. Docs updated if behavior changed?",
]

TASK_HARNESS_CHECKLIST = [
    "6. If this sprint maps to feature_list.json, qa score is >= 80/100 before passes=true?",
    "7. If feature status changed, feature_list.json and progress.txt are both updated?",
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

    checklist = list(CHECKLIST)
    cwd = Path.cwd()
    if (cwd / "feature_list.json").exists():
        checklist.extend(TASK_HARNESS_CHECKLIST)

    message = (
        "Pre-completion checklist:\n"
        + "\n".join(checklist)
        + "\n\nIf any item fails, fix before claiming completion."
    )

    emit(
        {
            "hookSpecificOutput": {
                "hookEventName": "Stop",
                "additionalContext": message,
            }
        }
    )


if __name__ == "__main__":
    main()
