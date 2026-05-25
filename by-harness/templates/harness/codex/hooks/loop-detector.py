#!/usr/bin/env python3
"""
Codex PreToolUse hook: detect repeated edits on the same file and block on threshold.
"""

import json
import sys
import time
import tempfile
import hashlib
from pathlib import Path

MAX_EDITS = 5
STATE_KIND = "codex"


def emit(payload):
    print(json.dumps(payload, ensure_ascii=False))


def find_repo_root(start):
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def resolve_git_dir(repo_root):
    dot_git = repo_root / ".git"
    if dot_git.is_dir():
        return dot_git
    if dot_git.is_file():
        try:
            content = dot_git.read_text(encoding="utf-8").strip()
        except OSError:
            return None
        if content.startswith("gitdir:"):
            git_dir = Path(content.split(":", 1)[1].strip())
            if not git_dir.is_absolute():
                git_dir = (repo_root / git_dir).resolve()
            return git_dir
    return None


def get_state_path():
    repo_root = find_repo_root(Path.cwd())
    git_dir = resolve_git_dir(repo_root)
    if git_dir is not None:
        return git_dir / "by-harness" / f"edit-counts-{STATE_KIND}.json"

    key = str(repo_root).encode("utf-8")
    digest = hashlib.sha256(key).hexdigest()[:16]
    return Path(tempfile.gettempdir()) / "by-harness" / digest / f"edit-counts-{STATE_KIND}.json"


def load_state(state_path):
    if state_path.exists():
        try:
            return json.loads(state_path.read_text())
        except (json.JSONDecodeError, ValueError):
            return {}
    return {}


def save_state(state_path, state):
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def is_stale(state):
    if "_timestamp" not in state:
        return True
    age = time.time() - state.get("_timestamp", 0)
    return age > 86400


def extract_file_path(tool_input):
    return (
        tool_input.get("file_path")
        or tool_input.get("path")
        or tool_input.get("target_file")
        or ""
    )


def main():
    try:
        input_data = json.loads(sys.stdin.read() or "{}")
    except (json.JSONDecodeError, ValueError):
        emit({})
        return

    tool_name = input_data.get("tool_name", "")
    if tool_name not in {"Edit", "Write", "MultiEdit"}:
        emit({})
        return

    tool_input = input_data.get("tool_input", {}) or {}
    file_path = extract_file_path(tool_input)
    if not file_path:
        emit({})
        return

    state_path = get_state_path()
    state = load_state(state_path)
    if is_stale(state):
        state = {"_timestamp": time.time()}

    try:
        normalized = str(Path(file_path).resolve().relative_to(Path.cwd()))
    except ValueError:
        normalized = file_path

    current_count = state.get(normalized, 0) + 1
    state[normalized] = current_count
    save_state(state_path, state)

    if current_count >= MAX_EDITS:
        reason = (
            f"Loop detected: {normalized} has been edited {current_count} times. "
            "Reassess the approach before continuing edits."
        )
        emit(
            {
                "decision": "block",
                "reason": reason,
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                },
            }
        )
        return

    if current_count >= MAX_EDITS - 2:
        remaining = MAX_EDITS - current_count
        emit(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": (
                        f"Warning: {normalized} edited {current_count} times. "
                        f"{remaining} edits before loop block."
                    ),
                }
            }
        )
        return

    emit({})


if __name__ == "__main__":
    main()
