#!/usr/bin/env python3
"""Auto-select feature from prompt and switch to the corresponding task branch.

Selection priority:
1) explicit task_id / feature id in prompt
2) semantic match from prompt text
3) safe fallback (single doing / current-branch-bound task)
4) conservative no-op with candidate hints
"""

from __future__ import annotations

import argparse
import json
import re
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
STOP_WORDS = {
    "处理",
    "继续",
    "推进",
    "优化",
    "修复",
    "相关",
    "问题",
    "任务",
    "实现",
    "开发",
    "本次",
    "今天",
    "这个",
    "那个",
    "一下",
    "进行",
    "开始",
    "vibe",
    "coding",
}

PUBLIC_MARKERS = [
    "公共",
    "通用",
    "基础能力",
    "公共能力",
]

INFRA_PUBLIC_KEYWORDS = [
    "项目基础建设",
    "基础建设",
    "基础设施",
    "工程化",
    "脚手架",
    "环境",
    "hook",
    "hooks",
    "tooling",
    "infra",
    "infrastructure",
    "并行开发流程",
    "agent流程",
    "codex流程",
    "harness",
]

BUSINESS_WORK_KEYWORDS = [
    "业务",
    "登录",
    "认证",
    "鉴权",
    "权限",
    "用户",
    "租户",
    "账户",
    "线索",
    "交易",
    "财务",
    "采购",
    "投放",
    "结算",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ensure task branch before coding.")
    parser.add_argument("--target-dir", default=".", help="repository root")
    parser.add_argument("--prompt", default="", help="user prompt text")
    parser.add_argument(
        "--sync-state",
        action="store_true",
        help="sync selected feature branch/status/updated_at back to task files",
    )
    return parser.parse_args()


def run_git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def run_git_cmd(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
    )


def git_error_detail(result: subprocess.CompletedProcess[str], fallback: str) -> str:
    stderr = (result.stderr or "").strip()
    stdout = (result.stdout or "").strip()
    return stderr or stdout or fallback


def detect_workspace_dir(repo: Path) -> Path:
    harness_dir = repo / HARNESS_DIR_NAME
    if harness_dir.exists():
        return harness_dir
    return repo


def resolve_bucket_feature_path(workspace_dir: Path, rel_path: str) -> Path:
    raw = str(rel_path or "").strip()
    if not raw:
        return workspace_dir / "__invalid_bucket_path__"

    candidates = [workspace_dir / raw]
    if raw.startswith(f"{HARNESS_DIR_NAME}/"):
        candidates.append(workspace_dir / raw[len(HARNESS_DIR_NAME) + 1 :])

    if workspace_dir.name == HARNESS_DIR_NAME:
        candidates.append(workspace_dir.parent / raw)
        if raw.startswith(f"{HARNESS_DIR_NAME}/"):
            candidates.append(workspace_dir.parent / raw[len(HARNESS_DIR_NAME) + 1 :])

    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def default_feature_file(workspace_dir: Path) -> Path:
    legacy = workspace_dir / "feature_list.json"
    if legacy.exists():
        return legacy
    return workspace_dir / "task-harness" / "features" / "backlog-core.json"


def resolve_feature_file(workspace_dir: Path) -> tuple[Path, Path, dict[str, Any] | None]:
    idx = workspace_dir / "task-harness" / "index.json"
    if not idx.exists():
        feature_file = default_feature_file(workspace_dir)
        return feature_file, feature_file, None

    data = json.loads(idx.read_text(encoding="utf-8"))
    active = str(data.get("active_bucket", "") or "")
    buckets = data.get("buckets", []) or []
    rel_path = ""
    for bucket in buckets:
        if str(bucket.get("id", "")) == active:
            rel_path = str(bucket.get("path", "") or "")
            break
    if not rel_path and buckets:
        rel_path = str((buckets[0] or {}).get("path", "") or "")
    if not rel_path:
        rel_path = "task-harness/features/backlog-core.json"

    feature_file = resolve_bucket_feature_path(workspace_dir, rel_path)
    legacy_mirror = workspace_dir / "feature_list.json"
    return feature_file, legacy_mirror, data


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


def load_session_control(workspace_dir: Path) -> dict[str, str]:
    control = {
        "context_mode": SESSION_MODE_SOFT,
        "flow_mode": FLOW_MODE_REVIEW_FIRST,
        "dirty_strategy": DIRTY_STRATEGY_BLOCK,
    }
    task_path = workspace_dir / "task.json"
    if not task_path.exists():
        return control
    try:
        data = json.loads(task_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, ValueError):
        return control
    harness = data.get("harness", {})
    if not isinstance(harness, dict):
        return control
    session_control = harness.get("session_control", {})
    if isinstance(session_control, dict):
        mode = session_control.get("mode", "")
        if mode:
            control["context_mode"] = normalize_session_mode(mode)
        flow_mode = session_control.get("flow_mode", "")
        if flow_mode:
            control["flow_mode"] = normalize_flow_mode(flow_mode)
        dirty_strategy = session_control.get("dirty_strategy", "")
        if dirty_strategy:
            control["dirty_strategy"] = normalize_dirty_strategy(dirty_strategy)

    legacy_mode = harness.get("session_mode", "")
    if legacy_mode:
        control["context_mode"] = normalize_session_mode(legacy_mode)
    return control


def load_session_boundary(workspace_dir: Path) -> dict[str, Any] | None:
    boundary_path = workspace_dir / "session-boundary.json"
    if not boundary_path.exists():
        return None
    try:
        data = json.loads(boundary_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, ValueError):
        return {"invalid": True, "_path": str(boundary_path)}
    if not isinstance(data, dict):
        return {"invalid": True, "_path": str(boundary_path)}
    data["_path"] = str(boundary_path)
    return data


def load_session_context(workspace_dir: Path) -> dict[str, Any] | None:
    context_path = workspace_dir / "session-context.json"
    if not context_path.exists():
        return None
    try:
        data = json.loads(context_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    return data


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


def non_harness_dirty_paths(repo: Path) -> list[str]:
    paths = dirty_paths(repo)
    return sorted(
        p
        for p in paths
        if p != HARNESS_DIR_NAME and not p.startswith(f"{HARNESS_DIR_NAME}/")
    )


def collect_all_features(workspace_dir: Path, index_data: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not index_data:
        for feature_file in (
            workspace_dir / "feature_list.json",
            workspace_dir / "task-harness" / "features" / "backlog-core.json",
        ):
            if not feature_file.exists():
                continue
            data = json.loads(feature_file.read_text(encoding="utf-8"))
            feats = data.get("features", [])
            if isinstance(feats, list):
                return feats
        return []

    all_features: list[dict[str, Any]] = []
    for bucket in index_data.get("buckets", []) or []:
        rel_path = str((bucket or {}).get("path", "") or "")
        if not rel_path:
            continue
        feature_path = resolve_bucket_feature_path(workspace_dir, rel_path)
        if not feature_path.exists():
            continue
        try:
            data = json.loads(feature_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError, ValueError):
            continue
        feats = data.get("features", [])
        if isinstance(feats, list):
            all_features.extend(feats)
    return all_features


def to_priority(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 10**9


def sort_key(feature: dict[str, Any]) -> tuple[int, str]:
    return (to_priority(feature.get("priority")), str(feature.get("id", "")))


def active_pending(features: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pending = [f for f in features if not bool(f.get("passes"))]
    return sorted(pending, key=sort_key)


def normalize_task_id(value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return "-".join(part.upper() for part in text.split("-"))


def is_feature_done(feature: dict[str, Any]) -> bool:
    status = str(feature.get("status", "")).strip().lower()
    return bool(feature.get("passes")) or status == "done"


def build_task_state(features: list[dict[str, Any]]) -> dict[str, bool]:
    state: dict[str, bool] = {}
    for feature in features:
        task_id = normalize_task_id(feature.get("task_id", ""))
        if not task_id:
            continue
        done = is_feature_done(feature)
        state[task_id] = state.get(task_id, False) or done
    return state


def dependency_unmet(feature: dict[str, Any], task_state: dict[str, bool]) -> list[str]:
    deps = feature.get("depends_on", [])
    if not isinstance(deps, list):
        return []

    unmet: list[str] = []
    for dep in deps:
        dep_text = str(dep or "").strip()
        if not dep_text:
            continue
        dep_key = normalize_task_id(dep_text)
        if not dep_key:
            continue
        if not task_state.get(dep_key, False):
            unmet.append(dep_text)
    return unmet


def is_selectable_feature(feature: dict[str, Any], task_state: dict[str, bool]) -> bool:
    if bool(feature.get("passes")):
        return False
    status = str(feature.get("status", "")).strip().lower()
    if status == "doing":
        return True
    return len(dependency_unmet(feature, task_state)) == 0


def active_selectable(features: list[dict[str, Any]], task_state: dict[str, bool]) -> list[dict[str, Any]]:
    selectable = [f for f in features if is_selectable_feature(f, task_state)]
    return sorted(selectable, key=sort_key)


def extract_prompt_tokens(prompt_text: str) -> tuple[list[str], list[str]]:
    text = (prompt_text or "").strip()
    if not text:
        return [], []

    task_ids: list[str] = []
    feat_ids: list[str] = []

    for match in re.findall(r"\b[a-z]{2,}(?:-[a-z0-9]{1,})+\b", text, flags=re.IGNORECASE):
        normalized = "-".join(part.upper() for part in match.split("-"))
        if normalized not in task_ids:
            task_ids.append(normalized)

    for match in re.findall(r"\bfeat-\d+\b", text, flags=re.IGNORECASE):
        normalized = match.lower()
        if normalized not in feat_ids:
            feat_ids.append(normalized)

    return task_ids, feat_ids


def contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword and keyword in text for keyword in keywords)


def master_branch_policy(prompt_text: str, has_task_reference: bool) -> tuple[bool, str]:
    lowered = (prompt_text or "").strip().lower()
    if not lowered:
        return False, ""

    has_public_marker = contains_any(lowered, PUBLIC_MARKERS)
    has_infra_public = contains_any(lowered, INFRA_PUBLIC_KEYWORDS)
    has_business_scope = contains_any(lowered, BUSINESS_WORK_KEYWORDS)

    if has_task_reference and (has_public_marker or has_infra_public):
        return False, "task-request-with-public-scope"
    if has_business_scope and has_infra_public:
        return False, "mixed-business-and-infra"
    if has_business_scope and has_public_marker:
        return False, "business-public-capability"
    if has_infra_public:
        return True, "infra-public-capability"
    if has_public_marker and not has_business_scope:
        return False, "ambiguous-public-capability"
    return False, ""


def extract_text_tokens(text: str) -> list[str]:
    if not text:
        return []
    lowered = text.lower()
    raw_tokens = re.findall(r"[a-z0-9]{2,}|[\u4e00-\u9fff]{2,}", lowered)
    dedup: list[str] = []
    seen: set[str] = set()
    for token in raw_tokens:
        token_variants = [token]
        if re.fullmatch(r"[\u4e00-\u9fff]{2,}", token):
            for n in (2, 3):
                if len(token) >= n:
                    token_variants.extend(token[i : i + n] for i in range(0, len(token) - n + 1))
        for variant in token_variants:
            if variant in STOP_WORDS:
                continue
            if variant not in seen:
                seen.add(variant)
                dedup.append(variant)
    return dedup


def feature_keywords(feature: dict[str, Any]) -> list[str]:
    words: list[str] = []
    for field in ("task_id", "id", "description"):
        value = str(feature.get(field, "") or "")
        words.extend(extract_text_tokens(value))
    uniq: list[str] = []
    seen: set[str] = set()
    for word in words:
        if word not in seen:
            seen.add(word)
            uniq.append(word)
    return uniq


def semantic_score(prompt_text: str, feature: dict[str, Any]) -> int:
    prompt = (prompt_text or "").lower()
    if not prompt.strip():
        return 0

    score = 0
    f_keywords = feature_keywords(feature)
    p_tokens = extract_text_tokens(prompt_text)
    feature_text = " ".join(
        [
            str(feature.get("task_id", "") or "").lower(),
            str(feature.get("id", "") or "").lower(),
            str(feature.get("description", "") or "").lower(),
        ]
    )

    for kw in f_keywords:
        if len(kw) >= 2 and kw in prompt:
            score += min(6, max(2, len(kw)))

    for token in p_tokens:
        if len(token) >= 2 and token in feature_text:
            score += min(3, max(1, len(token) // 3 + 1))

    return score


def pick_feature_by_prompt(
    features: list[dict[str, Any]], task_ids: list[str], feat_ids: list[str]
) -> dict[str, Any] | None:
    for task_id in task_ids:
        matched = [f for f in features if str(f.get("task_id", "")).upper() == task_id]
        if matched:
            return sorted(matched, key=sort_key)[0]

    for feat_id in feat_ids:
        matched = [f for f in features if str(f.get("id", "")).lower() == feat_id]
        if matched:
            return sorted(matched, key=sort_key)[0]
    return None


def pick_feature_by_semantic(
    features: list[dict[str, Any]], prompt_text: str, task_state: dict[str, bool]
) -> dict[str, Any] | None:
    active = active_selectable(features, task_state)
    if not active:
        return None

    ranked = sorted(
        ((semantic_score(prompt_text, feat), feat) for feat in active),
        key=lambda item: (item[0], -to_priority(item[1].get("priority")), str(item[1].get("id", ""))),
        reverse=True,
    )
    best_score = ranked[0][0]
    if best_score <= 0:
        return None
    if len(ranked) > 1 and best_score - ranked[1][0] < 2:
        return None
    if best_score < 4:
        return None
    return ranked[0][1]


def pick_feature(features: list[dict[str, Any]], task_state: dict[str, bool]) -> dict[str, Any] | None:
    active = active_selectable(features, task_state)
    if not active:
        return None

    doing = [f for f in active if str(f.get("status", "")).strip().lower() == "doing"]
    if doing:
        return sorted(doing, key=sort_key)[0]

    todo = [f for f in active if str(f.get("status", "")).strip().lower() in ("", "todo")]
    if todo:
        return sorted(todo, key=sort_key)[0]

    pending = [f for f in active if str(f.get("status", "")).strip().lower() != "done"]
    if pending:
        return sorted(pending, key=sort_key)[0]
    return None


def slug(value: str) -> str:
    lowered = (value or "").strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered).strip("-")
    return lowered or "task"


def normalize_branch(raw: str) -> str:
    raw = str(raw or "").strip()
    if not raw:
        return ""
    if "/" in raw:
        return "/".join(slug(part) for part in raw.split("/") if part.strip())
    return slug(raw)


def branch_for_feature(repo_short: str, feature: dict[str, Any]) -> str:
    preferred = normalize_branch(str(feature.get("branch") or ""))
    task_id = str(feature.get("task_id") or feature.get("id") or "task")
    generated = f"feat/{slug(repo_short)}/{slug(task_id)}"
    return preferred or generated


def pick_feature_from_current_branch(
    features: list[dict[str, Any]], repo_short: str, current_branch: str
) -> dict[str, Any] | None:
    for feat in active_pending(features):
        if branch_for_feature(repo_short, feat) == current_branch:
            return feat
    return None


def print_candidate_hints(features: list[dict[str, Any]], task_state: dict[str, bool], limit: int = 3) -> None:
    pending = active_pending(features)
    ready = [f for f in pending if is_selectable_feature(f, task_state)]
    blocked = [f for f in pending if not is_selectable_feature(f, task_state)]
    candidates = (ready + blocked)[:limit]
    if not candidates:
        return
    print("[branch] no confident task match; top candidates:")
    for feat in candidates:
        fid = str(feat.get("id", ""))
        tid = str(feat.get("task_id", ""))
        desc = str(feat.get("description", ""))
        unmet = dependency_unmet(feat, task_state)
        if unmet:
            print(f"[branch] candidate {fid} {tid} {desc} unmet_deps={','.join(unmet)}")
        else:
            print(f"[branch] candidate {fid} {tid} {desc} unmet_deps=-")


def sync_feature_fields(
    data: dict[str, Any], feature_id: str, *, branch: str, status: str | None
) -> bool:
    features = data.get("features", [])
    if not isinstance(features, list):
        return False

    changed = False
    today = datetime.now().strftime("%Y-%m-%d")
    for feat in features:
        if str(feat.get("id", "")) != feature_id:
            continue
        if feat.get("branch", "") != branch:
            feat["branch"] = branch
            changed = True
        if status is not None and feat.get("status", "") != status:
            feat["status"] = status
            changed = True
        if feat.get("updated_at", "") != today:
            feat["updated_at"] = today
            changed = True
    return changed


def write_json_if_changed(path: Path, data: dict[str, Any], changed: bool) -> None:
    if not changed:
        return
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def checkout_branch(repo: Path, branch: str, *, push_new_branch: bool = True) -> tuple[bool, str]:
    origin = run_git_cmd(repo, "remote", "get-url", "origin")
    if origin.returncode != 0:
        detail = git_error_detail(origin, "unknown remote error")
        return False, f"missing remote origin: {detail}"

    fetch = run_git_cmd(repo, "fetch", "origin", "--prune")
    if fetch.returncode != 0:
        detail = git_error_detail(fetch, "unknown fetch error")
        return False, f"git fetch failed: {detail}"

    local_exists = run_git_cmd(repo, "rev-parse", "--verify", f"refs/heads/{branch}").returncode == 0
    remote_exists = run_git_cmd(repo, "rev-parse", "--verify", f"refs/remotes/origin/{branch}").returncode == 0

    if remote_exists:
        if local_exists:
            checkout = run_git_cmd(repo, "checkout", branch)
            if checkout.returncode != 0:
                return False, git_error_detail(checkout, "unknown checkout error")
            return True, f"fetched and switched to local branch tracking remote: {branch}"
        track = run_git_cmd(repo, "checkout", "-b", branch, "--track", f"origin/{branch}")
        if track.returncode != 0:
            return False, git_error_detail(track, "unknown checkout error")
        return True, f"fetched and switched to remote branch: origin/{branch}"

    if local_exists:
        checkout = run_git_cmd(repo, "checkout", branch)
        if checkout.returncode != 0:
            return False, git_error_detail(checkout, "unknown checkout error")
        if not push_new_branch:
            return True, f"fetched and switched to existing local branch: {branch}"
        push = run_git_cmd(repo, "push", "-u", "origin", branch)
        if push.returncode != 0:
            return False, f"remote branch missing and push failed: {git_error_detail(push, 'unknown push error')}"
        return True, f"fetched, switched local branch, and pushed to remote: {branch}"

    create = run_git_cmd(repo, "checkout", "-b", branch)
    if create.returncode != 0:
        return False, git_error_detail(create, "unknown checkout error")
    if not push_new_branch:
        return True, f"fetched and created local branch: {branch}"
    push = run_git_cmd(repo, "push", "-u", "origin", branch)
    if push.returncode != 0:
        return False, f"created local branch but push failed: {git_error_detail(push, 'unknown push error')}"
    return True, f"fetched, created local branch, and pushed to remote: {branch}"


def main() -> int:
    args = parse_args()
    repo = Path(args.target_dir).resolve()
    prompt_text = args.prompt or ""

    if not (repo / ".git").exists():
        print(f"[branch] skip: not a git repo: {repo}")
        return 0

    workspace_dir = detect_workspace_dir(repo)
    session_control = load_session_control(workspace_dir)
    context_mode = session_control["context_mode"]
    flow_mode = session_control["flow_mode"]
    dirty_strategy = session_control["dirty_strategy"]
    boundary = load_session_boundary(workspace_dir)
    if boundary and context_mode == SESSION_MODE_HARD:
        closed_id = str(boundary.get("closed_feature_id", "n/a"))
        next_id = str(boundary.get("next_feature_id", "") or "n/a")
        print(
            "[branch] session-boundary active under hard_new_session mode: "
            f"closed_feature={closed_id} next_feature={next_id}"
        )
        print(
            "[branch] session rotation required. "
            "Please open a NEW session and run .harness/init.sh before starting next feature."
        )
        return 0

    if boundary and context_mode == SESSION_MODE_SOFT:
        # Soft mode should not be blocked by stale hard boundary markers.
        boundary_path = Path(str(boundary.get("_path", "")))
        if boundary_path.exists():
            try:
                boundary_path.unlink()
            except OSError:
                pass

    context_state = load_session_context(workspace_dir)
    if (
        flow_mode == FLOW_MODE_REVIEW_FIRST
        and context_state
        and bool(context_state.get("review_pending"))
    ):
        epoch = context_state.get("epoch", "?")
        print(
            "[branch] review gate active: "
            f"epoch={epoch}. Complete review before switching next task branch."
        )
        print(
            "[branch] hint: run `python3 .harness/scripts/task_switch.py continue --target-dir .` "
            "after review to auto-shelve/switch."
        )
        return 0

    if context_mode == SESSION_MODE_SOFT and context_state and bool(context_state.get("reset_required")):
        epoch = context_state.get("epoch", "?")
        print(
            "[branch] soft_reset context epoch active: "
            f"epoch={epoch}. Previous feature context should be considered stale."
        )

    feature_file, legacy_mirror, index_data = resolve_feature_file(workspace_dir)
    if not feature_file.exists():
        print(f"[branch] skip: feature file missing: {feature_file}")
        return 0

    data = json.loads(feature_file.read_text(encoding="utf-8"))
    features = data.get("features", [])
    if not isinstance(features, list):
        print(f"[branch] skip: invalid feature format: {feature_file}")
        return 0

    all_features = collect_all_features(workspace_dir, index_data)
    if not all_features:
        all_features = features
    task_state = build_task_state(all_features)

    repo_short = repo.name
    current = run_git(repo, "rev-parse", "--abbrev-ref", "HEAD")

    task_tokens, feat_tokens = extract_prompt_tokens(prompt_text)
    if prompt_text.strip():
        enforce_master, policy_reason = master_branch_policy(
            prompt_text,
            has_task_reference=bool(task_tokens or feat_tokens),
        )
        if enforce_master:
            print("[branch] detected infra public capability work; switch to master by policy.")
            if current == "master":
                print("[branch] already on master")
                return 0
            ok, detail = checkout_branch(repo, "master", push_new_branch=False)
            if not ok:
                print(
                    f"[branch] failed to switch branch from {current} to master. "
                    f"detail={detail}"
                )
                return 1
            print(f"[branch] {detail}")
            return 0

        if policy_reason in {
            "task-request-with-public-scope",
            "mixed-business-and-infra",
            "business-public-capability",
        }:
            print("[branch] keep current branch: prompt contains business or mixed scope.")

    selected = pick_feature_by_prompt(features, task_tokens, feat_tokens)
    source = "fallback"
    if selected:
        source = "prompt"
    else:
        if task_tokens or feat_tokens:
            print("[branch] prompt referenced task/feature but no exact match in this repo.")
            print(f"[branch] task_tokens={task_tokens} feat_tokens={feat_tokens}")

        if prompt_text.strip():
            selected = pick_feature_by_semantic(features, prompt_text, task_state)
            if selected:
                source = "semantic"

        if not selected:
            doing = [f for f in active_pending(features) if str(f.get("status", "")).strip().lower() == "doing"]
            if len(doing) == 1:
                selected = doing[0]
                source = "fallback-doing"
            elif len(doing) > 1:
                print("[branch] multiple doing tasks, skip automatic switch for safety.")
                print_candidate_hints(features, task_state)
                return 0

        if not selected:
            bound = pick_feature_from_current_branch(features, repo_short, current)
            if bound:
                selected = bound
                source = "fallback-current-branch"

        if not selected and not prompt_text.strip():
            selected = pick_feature(features, task_state)
            if selected:
                source = "fallback-default"

    if not selected:
        if prompt_text.strip():
            print("[branch] no pending feature matches prompt; keep current branch.")
            print_candidate_hints(features, task_state)
        else:
            print("[branch] no pending feature, keep current branch")
        return 0

    task_id = str(selected.get("task_id") or selected.get("id") or "task")
    feature_id = str(selected.get("id") or "feat")
    status = str(selected.get("status") or "todo")
    unmet = dependency_unmet(selected, task_state)
    if unmet and status.strip().lower() != "doing":
        print(
            "[branch] selected feature is blocked by unmet dependencies: "
            f"feature={feature_id} task_id={task_id} unmet_deps={','.join(unmet)}"
        )
        print_candidate_hints(features, task_state)
        return 0

    branch = branch_for_feature(repo_short, selected)
    print(f"[branch] source={source} feature={feature_id} task_id={task_id} status={status}")
    print(f"[branch] target_branch={branch}")

    if args.sync_state:
        next_status = status
        if not bool(selected.get("passes")) and status.strip().lower() in ("", "todo"):
            next_status = "doing"

        changed_active = sync_feature_fields(data, feature_id, branch=branch, status=next_status)
        write_json_if_changed(feature_file, data, changed_active)

        if legacy_mirror != feature_file and legacy_mirror.exists():
            try:
                mirror_data = json.loads(legacy_mirror.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, ValueError):
                mirror_data = {}
            changed_mirror = sync_feature_fields(
                mirror_data,
                feature_id,
                branch=branch,
                status=next_status,
            )
            write_json_if_changed(legacy_mirror, mirror_data, changed_mirror)

    if current == branch:
        print(f"[branch] already on {branch}")
        return 0

    non_harness_dirty = non_harness_dirty_paths(repo)
    if non_harness_dirty:
        print(
            "[branch] switch blocked: working tree has uncommitted changes. "
            f"configured dirty_strategy={dirty_strategy}."
        )
        print(
            "[branch] hint: run `python3 .harness/scripts/task_switch.py continue --target-dir .` "
            "to auto-shelve and switch safely."
        )
        return 0
    if is_worktree_dirty(repo):
        print("[branch] note: only .harness metadata is dirty; allow branch switch.")

    print(
        f"[branch] switching by task: feature={feature_id} task_id={task_id} "
        f"from={current} to={branch}"
    )
    ok, detail = checkout_branch(repo, branch)
    if not ok:
        print(
            f"[branch] failed to switch branch from {current} to {branch}. "
            f"detail={detail}"
        )
        return 1
    print(
        f"[branch] switched by task: feature={feature_id} task_id={task_id} "
        f"from={current} to={branch}"
    )
    print(f"[branch] {detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
