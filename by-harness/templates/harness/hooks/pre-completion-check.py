#!/usr/bin/env python3
"""
Pre-Completion Checklist Hook for Harness Engineering Framework.

PostToolUse hook that injects a verification reminder when a task is marked complete.

This implements the "Self-Verify First" golden principle from LangChain's research:
models are biased toward their first plausible solution. Forcing a verification
checklist before marking work done catches issues that would otherwise slip through.

Hook output format:
- {"systemMessage": "..."} to inject context without blocking
"""

import json
import sys
from pathlib import Path


CHECKLIST = [
    "1. Code compiles/builds without errors?",
    "2. All tests pass (both existing and new)?",
    "3. All acceptance criteria from the contract are met?",
    "4. No debug artifacts left (console.log, TODO, temporary code)?",
    "5. Documentation updated if behavior changed?",
]

TASK_HARNESS_CHECKLIST = [
    "6. If this sprint maps to feature_list.json, qa score is >= 80/100 before passes=true?",
    "7. If feature status changed, feature_list.json and progress.txt are both updated?",
]


def main():
    # Read hook input from stdin
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        print(json.dumps({}))
        return

    # Check if this is a TaskUpdate with status=completed
    tool_name = input_data.get('tool_name', '')
    tool_input = input_data.get('tool_input', {})

    if tool_name != 'TaskUpdate':
        print(json.dumps({}))
        return

    status = tool_input.get('status', '')
    if status != 'completed':
        print(json.dumps({}))
        return

    checklist = list(CHECKLIST)
    if (Path.cwd() / 'feature_list.json').exists():
        checklist.extend(TASK_HARNESS_CHECKLIST)

    # Inject pre-completion checklist
    message = (
        "Pre-completion checklist — verify ALL items before confirming done:\n"
        + "\n".join(checklist)
        + "\n\nIf any item fails, fix it before marking the task complete."
    )

    print(json.dumps({"systemMessage": message}))


if __name__ == '__main__':
    main()
