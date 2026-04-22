#!/usr/bin/env python3
"""One-command continue helper (same-branch execution, no branch switching)."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

HARNESS_DIR_NAME = ".harness"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Continue with next task on current branch.")
    parser.add_argument("action", choices=["continue"], help="continue to next task")
    parser.add_argument("--target-dir", default=".", help="repository root")
    parser.add_argument("--prompt", default="", help="optional prompt hint for task matching")
    return parser.parse_args()


def detect_workspace_dir(repo: Path) -> Path:
    harness = repo / HARNESS_DIR_NAME
    if harness.exists():
        return harness
    return repo


def clear_session_markers(workspace: Path) -> None:
    context_path = workspace / "session-context.json"
    if not context_path.exists():
        return
    try:
        data = json.loads(context_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, ValueError):
        return
    if not isinstance(data, dict):
        return

    changed = False
    for key in ("reset_required", "review_pending"):
        if bool(data.get(key)):
            data[key] = False
            changed = True
    if changed:
        context_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_script_path(repo: Path, workspace: Path) -> Path | None:
    candidates = [
        workspace / "scripts" / "ensure_task_branch.py",
        repo / "scripts" / "ensure_task_branch.py",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def update_script_path(repo: Path, workspace: Path) -> Path | None:
    candidates = [
        workspace / "scripts" / "update_runtime.py",
        repo / "scripts" / "update_runtime.py",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def invoke_runtime_check(repo: Path, workspace: Path) -> tuple[int, str]:
    script = update_script_path(repo, workspace)
    if script is None:
        return 0, "update_runtime.py not found (skip remote check)"
    cmd = ["python3", str(script), "--target-dir", str(repo), "--check-remote"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    out = (result.stdout or "").strip()
    err = (result.stderr or "").strip()
    detail = out if out else err
    if result.returncode != 0:
        return result.returncode, detail
    return 0, detail


def invoke_task_sync(repo: Path, workspace: Path, prompt: str) -> tuple[int, str]:
    script = ensure_script_path(repo, workspace)
    if script is None:
        return 1, "ensure_task_branch.py not found"

    cmd = ["python3", str(script), "--target-dir", str(repo), "--sync-state"]
    if prompt.strip():
        cmd.extend(["--prompt", prompt.strip()])
    result = subprocess.run(cmd, capture_output=True, text=True)
    out = (result.stdout or "").strip()
    err = (result.stderr or "").strip()
    detail = out if out else err
    return result.returncode, detail


def main() -> int:
    args = parse_args()
    repo = Path(args.target_dir).resolve()
    workspace = detect_workspace_dir(repo)

    rc_update, update_detail = invoke_runtime_check(repo, workspace)
    if update_detail:
        print(f"[switch] runtime-check: {update_detail}")
    if rc_update != 0:
        print("[switch] runtime-check failed; continue with current local runtime.")

    clear_session_markers(workspace)
    rc, detail = invoke_task_sync(repo, workspace, args.prompt)
    if detail:
        print(detail)
    if rc != 0:
        return rc

    print("[switch] continue done on current branch (branch switching disabled).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
