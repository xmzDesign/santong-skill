#!/usr/bin/env python3
"""One-command task switch helper for continuous harness workflow.

Actions:
1) Auto-box uncommitted changes (stash / wip commit / block)
2) Consume session review/reset markers
3) Invoke ensure_task_branch.py to switch next task branch
4) Track completed task branches for rollup
5) Auto-merge multiple task branches into one rollup branch when all tasks are done
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

HARNESS_DIR_NAME = ".harness"
SESSION_MODE_SOFT = "soft_reset"
SESSION_MODE_HARD = "hard_new_session"
FLOW_MODE_REVIEW_FIRST = "review_first"
FLOW_MODE_CONTINUOUS = "continuous"
DIRTY_STRATEGY_BLOCK = "block"
DIRTY_STRATEGY_STASH = "stash_then_switch"
DIRTY_STRATEGY_WIP = "wip_commit_then_switch"
DEFAULT_ROLLUP_TARGET = "feat/{repo}/integration"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Auto-box, switch task branch, and rollup merge.")
    parser.add_argument("action", choices=["continue"], help="switch to next task in one command")
    parser.add_argument("--target-dir", default=".", help="repository root")
    parser.add_argument("--prompt", default="", help="optional prompt hint for task matching")
    parser.add_argument(
        "--finalize-merge",
        action="store_true",
        help="force rollup merge even when pending tasks exist",
    )
    return parser.parse_args()


def run_git_cmd(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def run_git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def detect_workspace_dir(repo: Path) -> Path:
    harness = repo / HARNESS_DIR_NAME
    if harness.exists():
        return harness
    return repo


def normalize_session_mode(raw: str) -> str:
    value = str(raw or "").strip().lower()
    if value in {"hard_new_session", "hard", "new_session"}:
        return SESSION_MODE_HARD
    if value in {"soft_reset", "soft", "reset"}:
        return SESSION_MODE_SOFT
    return SESSION_MODE_SOFT


def normalize_flow_mode(raw: str) -> str:
    value = str(raw or "").strip().lower()
    if value in {"continuous", "continue"}:
        return FLOW_MODE_CONTINUOUS
    if value in {"review_first", "review"}:
        return FLOW_MODE_REVIEW_FIRST
    return FLOW_MODE_REVIEW_FIRST


def normalize_dirty_strategy(raw: str) -> str:
    value = str(raw or "").strip().lower()
    if value in {"stash_then_switch", "stash"}:
        return DIRTY_STRATEGY_STASH
    if value in {"wip_commit_then_switch", "wip_commit", "wip"}:
        return DIRTY_STRATEGY_WIP
    if value in {"block", "stop"}:
        return DIRTY_STRATEGY_BLOCK
    return DIRTY_STRATEGY_BLOCK


def load_session_control(workspace: Path) -> dict[str, Any]:
    control: dict[str, Any] = {
        "context_mode": SESSION_MODE_SOFT,
        "flow_mode": FLOW_MODE_REVIEW_FIRST,
        "dirty_strategy": DIRTY_STRATEGY_STASH,
        "auto_merge_on_all_done": True,
        "rollup_target": DEFAULT_ROLLUP_TARGET,
    }
    path = workspace / "task.json"
    if not path.exists():
        return control
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, ValueError):
        return control
    harness = data.get("harness", {})
    if not isinstance(harness, dict):
        return control
    session_control = harness.get("session_control", {})
    if isinstance(session_control, dict):
        control["context_mode"] = normalize_session_mode(session_control.get("mode", control["context_mode"]))
        control["flow_mode"] = normalize_flow_mode(session_control.get("flow_mode", control["flow_mode"]))
        control["dirty_strategy"] = normalize_dirty_strategy(
            session_control.get("dirty_strategy", control["dirty_strategy"])
        )
        if "auto_merge_on_all_done" in session_control:
            control["auto_merge_on_all_done"] = bool(session_control.get("auto_merge_on_all_done"))
        if session_control.get("rollup_target"):
            control["rollup_target"] = str(session_control.get("rollup_target"))
    return control


def is_worktree_dirty(repo: Path) -> bool:
    status = run_git_cmd(repo, "status", "--porcelain")
    if status.returncode != 0:
        return False
    return bool((status.stdout or "").strip())


def dirty_paths(repo: Path) -> set[str]:
    paths: set[str] = set()
    for args in (
        ("diff", "--name-only"),
        ("diff", "--name-only", "--cached"),
        ("ls-files", "--others", "--exclude-standard"),
    ):
        result = run_git_cmd(repo, *args)
        if result.returncode != 0:
            continue
        for line in (result.stdout or "").splitlines():
            text = line.strip()
            if text:
                paths.add(text)
    return paths


def split_dirty_paths(repo: Path) -> tuple[list[str], list[str]]:
    all_paths = sorted(dirty_paths(repo))
    harness: list[str] = []
    non_harness: list[str] = []
    for p in all_paths:
        if p == HARNESS_DIR_NAME or p.startswith(f"{HARNESS_DIR_NAME}/"):
            harness.append(p)
        else:
            non_harness.append(p)
    return harness, non_harness


def auto_box_dirty(repo: Path, strategy: str) -> tuple[bool, str]:
    if not is_worktree_dirty(repo):
        return True, "worktree clean"

    harness_paths, non_harness_paths = split_dirty_paths(repo)
    if not non_harness_paths:
        if harness_paths:
            return True, "only .harness metadata dirty; skip auto-box"
        return True, "no non-harness changes to box"

    if strategy == DIRTY_STRATEGY_BLOCK:
        return False, "working tree dirty and strategy=block"

    if strategy == DIRTY_STRATEGY_STASH:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        message = f"harness:auto-box:{stamp}"
        stash = run_git_cmd(repo, "stash", "push", "-u", "-m", message, "--", *non_harness_paths)
        if stash.returncode != 0:
            detail = (stash.stderr or stash.stdout or "").strip()
            return False, f"stash failed: {detail}"
        return True, f"auto-boxed non-harness changes by stash: {message}"

    if strategy == DIRTY_STRATEGY_WIP:
        add = run_git_cmd(repo, "add", "--", *non_harness_paths)
        if add.returncode != 0:
            detail = (add.stderr or add.stdout or "").strip()
            return False, f"git add failed: {detail}"
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        msg = f"chore(wip): auto-box before task switch {stamp}"
        commit = run_git_cmd(repo, "commit", "-m", msg)
        if commit.returncode != 0:
            detail = (commit.stderr or commit.stdout or "").strip()
            return False, f"wip commit failed: {detail}"
        return True, f"auto-boxed by local wip commit: {msg}"

    return False, f"unsupported dirty strategy: {strategy}"


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
    for key in ("review_pending", "reset_required"):
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
    for c in candidates:
        if c.exists():
            return c
    return None


def invoke_ensure_branch(repo: Path, workspace: Path, prompt: str) -> tuple[int, str]:
    script = ensure_script_path(repo, workspace)
    if script is None:
        return 1, "ensure_task_branch.py not found"

    cmd = ["python3", str(script), "--target-dir", str(repo)]
    if prompt.strip():
        cmd.extend(["--prompt", prompt.strip()])
    result = subprocess.run(cmd, capture_output=True, text=True)
    out = (result.stdout or "").strip()
    err = (result.stderr or "").strip()
    detail = out if out else err
    return result.returncode, detail


def resolve_feature_file(workspace: Path) -> Path:
    idx = workspace / "task-harness" / "index.json"
    if not idx.exists():
        return workspace / "feature_list.json"
    try:
        data = json.loads(idx.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, ValueError):
        return workspace / "feature_list.json"
    active = str(data.get("active_bucket", "") or "")
    buckets = data.get("buckets", []) or []
    rel = ""
    for b in buckets:
        if str(b.get("id", "")) == active:
            rel = str(b.get("path", "") or "")
            break
    if not rel and buckets:
        rel = str((buckets[0] or {}).get("path", "") or "")
    if not rel:
        rel = "feature_list.json"
    path = workspace / rel
    if path.exists():
        return path
    if rel.startswith(f"{HARNESS_DIR_NAME}/"):
        alt = workspace / rel[len(HARNESS_DIR_NAME) + 1 :]
        if alt.exists():
            return alt
    return workspace / "feature_list.json"


def pending_count(workspace: Path) -> int:
    feature_file = resolve_feature_file(workspace)
    if not feature_file.exists():
        return 0
    try:
        data = json.loads(feature_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, ValueError):
        return 0
    features = data.get("features", [])
    if not isinstance(features, list):
        return 0
    return sum(1 for f in features if not bool(f.get("passes")))


def is_rollup_candidate(branch: str) -> bool:
    text = str(branch or "").strip()
    if not text.startswith("feat/"):
        return False
    lowered = text.lower()
    if lowered.endswith("/integration") or lowered.endswith("/rollup"):
        return False
    return True


def load_rollup_state(workspace: Path) -> dict[str, Any]:
    path = workspace / "branch-rollup.json"
    if not path.exists():
        return {"pending_branches": [], "merged_branches": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, ValueError):
        return {"pending_branches": [], "merged_branches": []}
    if not isinstance(data, dict):
        return {"pending_branches": [], "merged_branches": []}
    pending = data.get("pending_branches", [])
    merged = data.get("merged_branches", [])
    if not isinstance(pending, list):
        pending = []
    if not isinstance(merged, list):
        merged = []
    return {"pending_branches": pending, "merged_branches": merged}


def save_rollup_state(workspace: Path, state: dict[str, Any]) -> Path:
    path = workspace / "branch-rollup.json"
    payload = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pending_branches": state.get("pending_branches", []),
        "merged_branches": state.get("merged_branches", []),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def append_rollup_branch(workspace: Path, branch: str) -> Path | None:
    if not is_rollup_candidate(branch):
        return None
    state = load_rollup_state(workspace)
    pending = [str(b) for b in state.get("pending_branches", []) if str(b).strip()]
    if branch not in pending:
        pending.append(branch)
    state["pending_branches"] = pending
    return save_rollup_state(workspace, state)


def render_rollup_target(pattern: str, repo_name: str) -> str:
    text = str(pattern or "").strip() or DEFAULT_ROLLUP_TARGET
    return text.replace("{repo}", repo_name)


def local_branch_exists(repo: Path, branch: str) -> bool:
    return run_git_cmd(repo, "rev-parse", "--verify", f"refs/heads/{branch}").returncode == 0


def remote_branch_exists(repo: Path, branch: str) -> bool:
    return run_git_cmd(repo, "rev-parse", "--verify", f"refs/remotes/origin/{branch}").returncode == 0


def ensure_rollup_branch(repo: Path, branch: str) -> tuple[bool, str]:
    if local_branch_exists(repo, branch):
        checkout = run_git_cmd(repo, "checkout", branch)
        if checkout.returncode != 0:
            return False, (checkout.stderr or checkout.stdout or "").strip()
        return True, f"checked out local rollup branch: {branch}"

    if remote_branch_exists(repo, branch):
        track = run_git_cmd(repo, "checkout", "-b", branch, "--track", f"origin/{branch}")
        if track.returncode != 0:
            return False, (track.stderr or track.stdout or "").strip()
        return True, f"checked out remote rollup branch: origin/{branch}"

    base = "master"
    if not local_branch_exists(repo, "master") and not remote_branch_exists(repo, "master"):
        base = "main"
    if not local_branch_exists(repo, base) and not remote_branch_exists(repo, base):
        base = run_git(repo, "rev-parse", "--abbrev-ref", "HEAD")

    if not local_branch_exists(repo, base) and remote_branch_exists(repo, base):
        create_base = run_git_cmd(repo, "checkout", "-b", base, "--track", f"origin/{base}")
        if create_base.returncode != 0:
            return False, (create_base.stderr or create_base.stdout or "").strip()
    else:
        checkout_base = run_git_cmd(repo, "checkout", base)
        if checkout_base.returncode != 0:
            return False, (checkout_base.stderr or checkout_base.stdout or "").strip()

    create_rollup = run_git_cmd(repo, "checkout", "-b", branch)
    if create_rollup.returncode != 0:
        return False, (create_rollup.stderr or create_rollup.stdout or "").strip()
    return True, f"created rollup branch from {base}: {branch}"


def merge_branch_into_current(repo: Path, source_branch: str) -> tuple[bool, str]:
    if local_branch_exists(repo, source_branch):
        ref = source_branch
    elif remote_branch_exists(repo, source_branch):
        ref = f"origin/{source_branch}"
    else:
        return False, f"branch not found locally/remotely: {source_branch}"

    merge = run_git_cmd(repo, "merge", "--no-ff", "--no-edit", ref)
    if merge.returncode != 0:
        detail = (merge.stderr or merge.stdout or "").strip()
        return False, f"merge failed for {source_branch}: {detail}"
    return True, f"merged {source_branch}"


def rollup_merge(repo: Path, workspace: Path, target_pattern: str) -> tuple[bool, str]:
    state = load_rollup_state(workspace)
    pending = [str(b) for b in state.get("pending_branches", []) if is_rollup_candidate(str(b))]
    pending = list(dict.fromkeys(pending))
    if len(pending) < 2:
        return True, f"rollup skipped: branch count={len(pending)}"

    harness_dirty, non_harness_dirty = split_dirty_paths(repo)
    if non_harness_dirty:
        return False, "cannot rollup merge with non-harness dirty worktree"

    harness_stash_ref = ""
    if harness_dirty:
        stash_msg = f"harness:auto-rollup-metadata:{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        stash = run_git_cmd(repo, "stash", "push", "-u", "-m", stash_msg)
        if stash.returncode != 0:
            detail = (stash.stderr or stash.stdout or "").strip()
            return False, f"failed to stash harness metadata before rollup: {detail}"
        ref = run_git_cmd(repo, "rev-parse", "--verify", "refs/stash")
        if ref.returncode == 0:
            harness_stash_ref = (ref.stdout or "").strip()

    fetch = run_git_cmd(repo, "fetch", "origin", "--prune")
    if fetch.returncode != 0:
        detail = (fetch.stderr or fetch.stdout or "").strip()
        return False, f"git fetch failed before rollup: {detail}"

    target = render_rollup_target(target_pattern, repo.name)
    ok, detail = ensure_rollup_branch(repo, target)
    if not ok:
        return False, detail

    merged: list[str] = []
    for branch in pending:
        if branch == target:
            continue
        done, msg = merge_branch_into_current(repo, branch)
        if not done:
            return False, msg
        merged.append(branch)

    if not merged:
        return True, "rollup skipped: no merge candidates after filtering"

    if run_git_cmd(repo, "remote", "get-url", "origin").returncode == 0:
        push = run_git_cmd(repo, "push", "-u", "origin", target)
        if push.returncode != 0:
            detail = (push.stderr or push.stdout or "").strip()
            return False, f"rollup push failed: {detail}"

    restore_note = ""
    if harness_stash_ref:
        apply = run_git_cmd(repo, "stash", "apply", harness_stash_ref)
        if apply.returncode == 0:
            run_git_cmd(repo, "stash", "drop", harness_stash_ref)
            restore_note = " | restored harness metadata stash"
        else:
            detail = (apply.stderr or apply.stdout or "").strip()
            restore_note = f" | warning: failed to restore harness metadata stash: {detail}"

    state["pending_branches"] = [b for b in pending if b not in merged]
    history = [str(b) for b in state.get("merged_branches", []) if str(b).strip()]
    for b in merged:
        if b not in history:
            history.append(b)
    state["merged_branches"] = history
    save_rollup_state(workspace, state)
    return (
        True,
        f"rollup merged {len(merged)} branches into {target}: {', '.join(merged)}{restore_note}",
    )


def main() -> int:
    args = parse_args()
    repo = Path(args.target_dir).resolve()
    if not (repo / ".git").exists():
        print(f"[switch] target is not git repo: {repo}")
        return 1

    workspace = detect_workspace_dir(repo)
    control = load_session_control(workspace)
    context_mode = str(control.get("context_mode", SESSION_MODE_SOFT))
    flow_mode = str(control.get("flow_mode", FLOW_MODE_REVIEW_FIRST))
    dirty_strategy = str(control.get("dirty_strategy", DIRTY_STRATEGY_STASH))
    auto_merge_on_all_done = bool(control.get("auto_merge_on_all_done", True))
    rollup_target = str(control.get("rollup_target", DEFAULT_ROLLUP_TARGET))

    print(
        "[switch] mode="
        f"{flow_mode} context_mode={context_mode} dirty_strategy={dirty_strategy}"
    )

    ok, box_detail = auto_box_dirty(repo, dirty_strategy)
    print(f"[switch] box: {box_detail}")
    if not ok:
        return 1

    clear_session_markers(workspace)

    before = run_git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    rc, detail = invoke_ensure_branch(repo, workspace, args.prompt)
    if detail:
        print(f"[switch] ensure: {detail}")
    if rc != 0:
        return rc

    after = run_git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    if before != after and is_rollup_candidate(before):
        rollup_file = append_rollup_branch(workspace, before)
        if rollup_file:
            print(f"[switch] rollup track source branch: {before} -> {rollup_file}")

    pending = pending_count(workspace)
    should_merge = args.finalize_merge or (auto_merge_on_all_done and pending == 0)
    if should_merge:
        candidate = after if before == after else before
        if is_rollup_candidate(candidate):
            append_rollup_branch(workspace, candidate)
        done, merge_detail = rollup_merge(repo, workspace, rollup_target)
        print(f"[switch] rollup: {merge_detail}")
        if not done:
            return 1

    print(f"[switch] branch: {before} -> {after}")
    print(f"[switch] pending features: {pending}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
