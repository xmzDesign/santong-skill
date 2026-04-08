#!/usr/bin/env python3
"""
Codex Stop hook: inject completion checklist before finalizing.
"""

import json
import sys

CHECKLIST = [
    "1. Code compiles/builds without errors?",
    "2. All tests pass (existing and new)?",
    "3. Acceptance criteria are verified one-by-one?",
    "4. No debug artifacts left (console.log/TODO/temp code)?",
    "5. Docs updated if behavior changed?",
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

    message = (
        "Pre-completion checklist:\n"
        + "\n".join(CHECKLIST)
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
