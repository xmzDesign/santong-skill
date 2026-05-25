#!/usr/bin/env python3
"""
Loop Detection Hook for Harness Engineering Framework.

PreToolUse hook that tracks per-file edit counts.
Blocks edits to the same file after N attempts (default: 5).

This implements the "Loop Awareness" golden principle from LangChain's research:
models can enter "doom loops" — making small variations to the same broken approach.
Tracking edit counts per file prevents this waste.

Hook output format:
- {} to allow the tool call
- {"decision": "block", "reason": "..."} to block
"""

import json
import sys
import time
import tempfile
import hashlib
from pathlib import Path

MAX_EDITS = 5
STATE_KIND = 'claude'


def find_repo_root(start):
    """Find the repository root for state scoping."""
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / '.git').exists():
            return candidate
    return current


def resolve_git_dir(repo_root):
    """Resolve .git for normal repos and git worktrees."""
    dot_git = repo_root / '.git'
    if dot_git.is_dir():
        return dot_git
    if dot_git.is_file():
        try:
            content = dot_git.read_text(encoding='utf-8').strip()
        except OSError:
            return None
        if content.startswith('gitdir:'):
            git_dir = Path(content.split(':', 1)[1].strip())
            if not git_dir.is_absolute():
                git_dir = (repo_root / git_dir).resolve()
            return git_dir
    return None


def get_state_path():
    """Get the path to the local edit counts state file."""
    repo_root = find_repo_root(Path.cwd())
    git_dir = resolve_git_dir(repo_root)
    if git_dir is not None:
        return git_dir / 'by-harness' / f'edit-counts-{STATE_KIND}.json'

    key = str(repo_root).encode('utf-8')
    digest = hashlib.sha256(key).hexdigest()[:16]
    return Path(tempfile.gettempdir()) / 'by-harness' / digest / f'edit-counts-{STATE_KIND}.json'


def load_state(state_path):
    """Load edit counts from state file."""
    if state_path.exists():
        try:
            return json.loads(state_path.read_text())
        except (json.JSONDecodeError, ValueError):
            return {}
    return {}


def save_state(state_path, state):
    """Save edit counts to state file."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2))


def is_stale(state):
    """Check if the state is from a previous session (>24h old)."""
    if '_timestamp' not in state:
        return True
    age = time.time() - state.get('_timestamp', 0)
    return age > 86400  # 24 hours


def main():
    # Read hook input from stdin
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        # If we can't parse input, allow the edit
        print(json.dumps({}))
        return

    # Extract file path from tool input
    tool_input = input_data.get('tool_input', {})
    file_path = tool_input.get('file_path', '') or tool_input.get('path', '')

    if not file_path:
        # No file path detected, allow
        print(json.dumps({}))
        return

    state_path = get_state_path()
    state = load_state(state_path)

    # Reset if state is stale (new session)
    if is_stale(state):
        state = {'_timestamp': time.time()}

    # Normalize file path
    try:
        normalized = str(Path(file_path).resolve().relative_to(Path.cwd()))
    except ValueError:
        normalized = file_path

    # Increment edit count
    current_count = state.get(normalized, 0) + 1
    state[normalized] = current_count

    if current_count >= MAX_EDITS:
        save_state(state_path, state)
        reason = (
            f"Loop detected: {normalized} has been edited {current_count} times. "
            f"This likely indicates a doom loop. "
            f"Consider: (1) Reassessing your approach entirely, "
            f"(2) Breaking the problem into smaller steps, "
            f"(3) Asking the user for guidance."
        )
        print(json.dumps({"decision": "block", "reason": reason}))
    else:
        save_state(state_path, state)
        # Add a gentle reminder when approaching the limit
        if current_count >= MAX_EDITS - 2:
            remaining = MAX_EDITS - current_count
            print(json.dumps({
                "systemMessage": (
                    f"Warning: {normalized} has been edited {current_count} times. "
                    f"{remaining} edits remaining before loop detection triggers. "
                    f"Consider whether your current approach is working."
                )
            }))
        else:
            print(json.dumps({}))


if __name__ == '__main__':
    main()
