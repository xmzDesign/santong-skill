#!/usr/bin/env python3
"""Versioned runtime updater for by-harness projects.

This updater supports:
1) Runtime version tracking via `.harness/runtime-version.json`
2) Periodic remote manifest checks
3) Auto-apply based on update policy
4) Incremental migrations by local version chain
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

HARNESS_DIR_NAME = ".harness"
VERSION_FILE_NAME = "runtime-version.json"
POLICY_FILE_NAME = "update-policy.json"
STATE_FILE_NAME = "update-state.json"
LATEST_RUNTIME_VERSION = "2.1.0"
RUNTIME_SCRIPT_NAMES = (
    "session_close.py",
    "ensure_task_branch.py",
    "task_switch.py",
    "update_runtime.py",
    "upgrade_legacy_repo.py",
)
RUNTIME_DOC_REL_PATHS = (
    "TASK-HARNESS.md",
    "docs/architecture.md",
    "docs/golden-principles.md",
    "docs/sprint-workflow.md",
    "docs/java-dev-conventions.md",
    "docs/frontend-dev-conventions.md",
    "docs/contracts/TEMPLATE.md",
)

DEFAULT_MODE = "soft_reset"
SUPPORTED_MODES = ["soft_reset", "hard_new_session"]
MODE_GUIDE = {
    "soft_reset": "默认模式：同一聊天可继续，但每次 feature 收口后自动提升 context epoch，并要求忽略旧 feature 上下文。",
    "hard_new_session": "严格模式：每个 feature 收口后必须新开会话，未新开会话前阻止进入下一个 feature。",
}
TASK_SWITCH_RULE = "继续下个任务可执行：python3 .harness/scripts/task_switch.py continue --target-dir .（仅当前分支）"
RULE_PREFIXES_TO_REMOVE = (
    "连续模式切任务：",
    "多个任务分支在全部完成后自动汇总合并到 rollup_target 分支",
)
LEGACY_CONTROL_KEYS = (
    "flow_mode",
    "dirty_strategy",
    "auto_merge_on_all_done",
    "rollup_target",
    "supported_flow_modes",
    "supported_dirty_strategies",
    "flow_mode_guide",
    "dirty_strategy_guide",
)
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

DEFAULT_POLICY = {
    "enabled": False,
    "channel": "stable",
    "manifest_url": "",
    "check_interval_minutes": 360,
    "auto_apply_patch": True,
    "auto_apply_minor": False,
    "auto_apply_major": False,
    "require_checksum": True,
    "request_timeout_seconds": 10,
}

MIGRATIONS: dict[str, tuple[str, str]] = {
    "1.0.0": ("2.0.0", "migrate_remove_branch_switching"),
    "2.0.0": ("2.1.0", "migrate_runtime_versioning"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Versioned runtime updater for by-harness projects.")
    parser.add_argument("--target-dir", required=True, help="已初始化仓库目录（或 .harness 目录）")
    parser.add_argument(
        "--check-remote",
        action="store_true",
        help="按 update-policy 执行定时检查并按策略自动应用（用于 init/task_switch 自动触发）",
    )
    parser.add_argument(
        "--force-check",
        action="store_true",
        help="忽略检测间隔，强制检查远程版本",
    )
    parser.add_argument(
        "--manifest-url",
        default="",
        help="覆盖 policy 的 manifest_url（便于测试或临时切换源）",
    )
    parser.add_argument("--dry-run", action="store_true", help="只打印变更计划，不落盘")
    parser.add_argument("--no-backup", action="store_true", help="跳过升级前备份")
    parser.add_argument(
        "--backup-dir",
        default="",
        help="自定义备份目录（默认 .harness/backups/update-YYYYMMDD-HHMMSS）",
    )
    return parser.parse_args()


def detect_harness_dir(target: Path) -> Path:
    if target.name == HARNESS_DIR_NAME and target.exists():
        return target
    harness_dir = target / HARNESS_DIR_NAME
    if harness_dir.exists():
        return harness_dir
    raise RuntimeError(f"未检测到 {HARNESS_DIR_NAME} 目录：{target}")


def parse_semver(value: str) -> tuple[int, int, int] | None:
    text = str(value or "").strip()
    m = SEMVER_RE.match(text)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def semver_lt(a: str, b: str) -> bool:
    pa = parse_semver(a)
    pb = parse_semver(b)
    if pa is None or pb is None:
        return False
    return pa < pb


def semver_gt(a: str, b: str) -> bool:
    pa = parse_semver(a)
    pb = parse_semver(b)
    if pa is None or pb is None:
        return False
    return pa > pb


def classify_bump(current: str, target: str) -> str:
    pc = parse_semver(current)
    pt = parse_semver(target)
    if pc is None or pt is None:
        return "unknown"
    if pt[0] != pc[0]:
        return "major"
    if pt[1] != pc[1]:
        return "minor"
    if pt[2] != pc[2]:
        return "patch"
    return "none"


def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def to_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_policy(harness_dir: Path) -> dict[str, Any]:
    policy_path = harness_dir / POLICY_FILE_NAME
    if not policy_path.exists():
        return dict(DEFAULT_POLICY)
    try:
        payload = load_json(policy_path)
    except (json.JSONDecodeError, OSError, ValueError):
        return dict(DEFAULT_POLICY)
    if not isinstance(payload, dict):
        return dict(DEFAULT_POLICY)
    policy = dict(DEFAULT_POLICY)
    policy.update(payload)
    return policy


def load_state(harness_dir: Path) -> dict[str, Any]:
    state_path = harness_dir / STATE_FILE_NAME
    if not state_path.exists():
        return {}
    try:
        payload = load_json(state_path)
    except (json.JSONDecodeError, OSError, ValueError):
        return {}
    if not isinstance(payload, dict):
        return {}
    return payload


def save_state(harness_dir: Path, state: dict[str, Any], dry_run: bool) -> None:
    path = harness_dir / STATE_FILE_NAME
    if dry_run:
        print(f"[dry-run] write state: {path}")
        return
    dump_json(path, state)


def runtime_version_path(harness_dir: Path) -> Path:
    return harness_dir / VERSION_FILE_NAME


def infer_current_version(harness_dir: Path) -> tuple[str, str]:
    version_path = runtime_version_path(harness_dir)
    if version_path.exists():
        try:
            payload = load_json(version_path)
            v = str(payload.get("runtime_version", "")).strip()
            if parse_semver(v):
                return v, VERSION_FILE_NAME
        except (json.JSONDecodeError, OSError, ValueError):
            pass

    task_path = harness_dir / "task.json"
    if not task_path.exists():
        return "1.0.0", "default"
    try:
        task = load_json(task_path)
    except (json.JSONDecodeError, OSError, ValueError):
        return "1.0.0", "task-json-invalid"

    harness = task.get("harness", {})
    sc = harness.get("session_control", {}) if isinstance(harness, dict) else {}
    if not isinstance(sc, dict):
        return "1.0.0", "task-json"
    if any(key in sc for key in LEGACY_CONTROL_KEYS):
        return "1.0.0", "task-json-legacy-keys"
    return "2.0.0", "task-json-modern-no-version-file"


def normalize_mode(raw: Any) -> str:
    text = str(raw or "").strip().lower()
    if text in {"hard_new_session", "hard", "new_session"}:
        return "hard_new_session"
    if text in {"soft_reset", "soft", "reset"}:
        return "soft_reset"
    return DEFAULT_MODE


def migrate_task_json_to_current_branch_mode(task_data: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    changed = False
    payload = dict(task_data) if isinstance(task_data, dict) else {}
    harness = payload.get("harness", {})
    if not isinstance(harness, dict):
        harness = {}
        changed = True

    session_control = harness.get("session_control", {})
    legacy_mode = harness.get("session_mode", "")
    mode = DEFAULT_MODE
    if isinstance(session_control, dict) and session_control.get("mode"):
        mode = normalize_mode(session_control.get("mode"))
    elif legacy_mode:
        mode = normalize_mode(legacy_mode)

    next_control = {
        "mode": mode,
        "supported_modes": SUPPORTED_MODES,
        "mode_guide": MODE_GUIDE,
    }
    if session_control != next_control:
        changed = True
    harness["session_control"] = next_control

    if "session_mode" in harness:
        harness.pop("session_mode", None)
        changed = True

    files = harness.get("files", {})
    if isinstance(files, dict):
        if "feature_list" in files and "legacy_feature_list" not in files:
            files["legacy_feature_list"] = files.pop("feature_list")
            changed = True
        if "legacy_feature_list" not in files:
            files["legacy_feature_list"] = ".harness/feature_list.json"
            changed = True
        if files.get("runtime_version") != f".harness/{VERSION_FILE_NAME}":
            files["runtime_version"] = f".harness/{VERSION_FILE_NAME}"
            changed = True
        if files.get("update_policy") != f".harness/{POLICY_FILE_NAME}":
            files["update_policy"] = f".harness/{POLICY_FILE_NAME}"
            changed = True
        if files.get("update_state") != f".harness/{STATE_FILE_NAME}":
            files["update_state"] = f".harness/{STATE_FILE_NAME}"
            changed = True
        harness["files"] = files

    rules = harness.get("rules", [])
    if isinstance(rules, list):
        normalized: list[str] = []
        for raw in rules:
            text = str(raw)
            if any(text.startswith(prefix) for prefix in RULE_PREFIXES_TO_REMOVE):
                changed = True
                continue
            normalized.append(text)
        if TASK_SWITCH_RULE not in normalized:
            normalized.append(TASK_SWITCH_RULE)
            changed = True
        harness["rules"] = normalized

    payload["harness"] = harness
    updated = datetime.now().strftime("%Y-%m-%d")
    if str(payload.get("updated", "")) != updated:
        payload["updated"] = updated
        changed = True
    return payload, changed


def cleanup_session_context(session_context_path: Path, dry_run: bool) -> bool:
    if not session_context_path.exists():
        return False
    try:
        payload = load_json(session_context_path)
    except (json.JSONDecodeError, OSError, ValueError):
        return False
    if not isinstance(payload, dict):
        return False
    if "review_pending" not in payload:
        return False
    payload.pop("review_pending", None)
    if dry_run:
        print(f"[dry-run] cleanup key review_pending: {session_context_path}")
    else:
        dump_json(session_context_path, payload)
    return True


def remove_file(path: Path, dry_run: bool) -> bool:
    if not path.exists():
        return False
    if dry_run:
        print(f"[dry-run] remove: {path}")
    else:
        path.unlink()
    return True


def migrate_remove_branch_switching(harness_dir: Path, dry_run: bool) -> dict[str, int]:
    stats = {"task_json_changed": 0, "context_cleaned": 0, "files_removed": 0}
    task_path = harness_dir / "task.json"
    task_data = load_json(task_path)
    migrated, changed = migrate_task_json_to_current_branch_mode(task_data)
    if changed:
        if dry_run:
            print(f"[dry-run] migrate task config to current-branch mode: {task_path}")
        else:
            dump_json(task_path, migrated)
        stats["task_json_changed"] += 1
    if cleanup_session_context(harness_dir / "session-context.json", dry_run):
        stats["context_cleaned"] += 1
    if remove_file(harness_dir / "branch-rollup.json", dry_run):
        stats["files_removed"] += 1
    return stats


def migrate_runtime_versioning(harness_dir: Path, dry_run: bool) -> dict[str, int]:
    stats = {"task_json_changed": 0, "context_cleaned": 0, "files_removed": 0}
    task_path = harness_dir / "task.json"
    task_data = load_json(task_path)
    migrated, changed = migrate_task_json_to_current_branch_mode(task_data)
    if changed:
        if dry_run:
            print(f"[dry-run] migrate runtime-version pointers: {task_path}")
        else:
            dump_json(task_path, migrated)
        stats["task_json_changed"] += 1
    if cleanup_session_context(harness_dir / "session-context.json", dry_run):
        stats["context_cleaned"] += 1
    return stats


def run_migration(step_name: str, harness_dir: Path, dry_run: bool) -> dict[str, int]:
    if step_name == "migrate_remove_branch_switching":
        return migrate_remove_branch_switching(harness_dir, dry_run)
    if step_name == "migrate_runtime_versioning":
        return migrate_runtime_versioning(harness_dir, dry_run)
    raise RuntimeError(f"未知迁移步骤：{step_name}")


def write_runtime_version(harness_dir: Path, version: str, dry_run: bool, updated_by: str) -> bool:
    path = runtime_version_path(harness_dir)
    if path.exists():
        try:
            current = load_json(path)
            if str(current.get("runtime_version", "")).strip() == version:
                return False
        except (json.JSONDecodeError, OSError, ValueError):
            pass

    payload = {
        "skill": "by-harness",
        "runtime_version": version,
        "updated_at": now_iso(),
        "updated_by": updated_by,
    }
    if dry_run:
        print(f"[dry-run] write runtime version: {path} -> {version}")
    else:
        dump_json(path, payload)
    return True


def backup_files(harness_dir: Path, backup_root: Path, paths: list[Path], dry_run: bool) -> int:
    count = 0
    for src in paths:
        if not src.exists():
            continue
        rel = src.relative_to(harness_dir)
        dst = backup_root / rel
        if dry_run:
            print(f"[dry-run] backup: {src} -> {dst}")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        count += 1
    return count


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_bytes(url: str, timeout_seconds: int) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "by-harness-updater/1.0"})
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        return resp.read()


def fetch_manifest(manifest_url: str, timeout_seconds: int) -> dict[str, Any]:
    raw = fetch_bytes(manifest_url, timeout_seconds)
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("manifest must be a JSON object")
    return payload


def should_check_remote(policy: dict[str, Any], state: dict[str, Any], force_check: bool) -> tuple[bool, str]:
    if force_check:
        return True, "force-check"
    if not bool(policy.get("enabled", False)):
        return False, "policy-disabled"
    interval_minutes = max(1, to_int(policy.get("check_interval_minutes", 360), 360))
    last_check_ts = to_int(state.get("last_check_unix", 0), 0)
    now_ts = int(datetime.now().timestamp())
    if last_check_ts <= 0:
        return True, "first-check"
    if now_ts - last_check_ts >= interval_minutes * 60:
        return True, "interval-elapsed"
    return False, "interval-not-elapsed"


def update_state_after_check(
    harness_dir: Path,
    state: dict[str, Any],
    *,
    result: str,
    remote_version: str = "",
    error: str = "",
    dry_run: bool,
) -> None:
    now_ts = int(datetime.now().timestamp())
    state["last_check_at"] = now_iso()
    state["last_check_unix"] = now_ts
    state["last_result"] = result
    if remote_version:
        state["last_remote_version"] = remote_version
    if error:
        state["last_error"] = error
    else:
        state.pop("last_error", None)
    save_state(harness_dir, state, dry_run)


def decide_auto_apply(policy: dict[str, Any], current: str, target: str) -> bool:
    bump = classify_bump(current, target)
    if bump == "patch":
        return bool(policy.get("auto_apply_patch", True))
    if bump == "minor":
        return bool(policy.get("auto_apply_minor", False))
    if bump == "major":
        return bool(policy.get("auto_apply_major", False))
    return False


def validate_manifest(manifest: dict[str, Any], current_version: str) -> tuple[str, list[dict[str, Any]]]:
    target_version = str(manifest.get("version", "")).strip()
    if parse_semver(target_version) is None:
        raise RuntimeError("manifest.version is invalid semver")

    min_compatible = str(manifest.get("min_compatible_version", "1.0.0")).strip() or "1.0.0"
    if parse_semver(min_compatible) and semver_lt(current_version, min_compatible):
        raise RuntimeError(
            f"current version {current_version} is lower than min_compatible_version {min_compatible}"
        )

    files = manifest.get("files", [])
    if not isinstance(files, list):
        raise RuntimeError("manifest.files must be an array")
    return target_version, files


def secure_target_path(harness_dir: Path, rel_path: str) -> Path:
    raw = str(rel_path or "").strip().replace("\\", "/")
    if not raw or raw.startswith("/") or ".." in raw.split("/"):
        raise RuntimeError(f"invalid manifest file path: {rel_path}")
    path = (harness_dir / raw).resolve()
    if harness_dir.resolve() not in path.parents and path != harness_dir.resolve():
        raise RuntimeError(f"path escapes harness directory: {rel_path}")
    return path


def materialize_manifest_files(
    harness_dir: Path,
    files: list[dict[str, Any]],
    *,
    timeout_seconds: int,
    require_checksum: bool,
) -> list[tuple[Path, bytes]]:
    rendered: list[tuple[Path, bytes]] = []
    for item in files:
        if not isinstance(item, dict):
            raise RuntimeError("manifest file item must be an object")
        rel_path = str(item.get("path", "")).strip()
        target = secure_target_path(harness_dir, rel_path)

        if "content" in item:
            content = item.get("content")
            if isinstance(content, dict) or isinstance(content, list):
                data = (json.dumps(content, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            else:
                data = str(content).encode("utf-8")
        else:
            url = str(item.get("url", "")).strip()
            if not url:
                raise RuntimeError(f"manifest file missing url/content: {rel_path}")
            data = fetch_bytes(url, timeout_seconds)

        expected = str(item.get("sha256", "")).strip().lower()
        if require_checksum:
            if not expected:
                raise RuntimeError(f"checksum required but missing sha256 for {rel_path}")
            actual = sha256_hex(data)
            if actual != expected:
                raise RuntimeError(f"sha256 mismatch for {rel_path}: expected={expected} actual={actual}")
        rendered.append((target, data))
    return rendered


def write_rendered_files(rendered: list[tuple[Path, bytes]], dry_run: bool) -> int:
    count = 0
    for target, data in rendered:
        if dry_run:
            print(f"[dry-run] write file: {target}")
            count += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        if target.suffix in {".py", ".sh"}:
            target.chmod(target.stat().st_mode | 0o755)
        count += 1
    return count


def run_known_migrations(harness_dir: Path, current_version: str, target_version: str, dry_run: bool) -> dict[str, int]:
    stats = {"task_json_changed": 0, "context_cleaned": 0, "files_removed": 0}
    version = current_version
    while True:
        step = MIGRATIONS.get(version)
        if step is None:
            break
        next_version, step_name = step
        if semver_gt(next_version, target_version):
            break
        print(f"Apply migration: {version} -> {next_version} ({step_name})")
        result = run_migration(step_name, harness_dir, dry_run)
        for k, v in result.items():
            stats[k] = stats.get(k, 0) + int(v)
        version = next_version
    return stats


def apply_remote_update(
    *,
    harness_dir: Path,
    manifest: dict[str, Any],
    current_version: str,
    target_version: str,
    files: list[dict[str, Any]],
    backup_root: Path,
    no_backup: bool,
    dry_run: bool,
    timeout_seconds: int,
    require_checksum: bool,
) -> tuple[int, dict[str, int]]:
    backup_targets = [harness_dir / "task.json", runtime_version_path(harness_dir)]
    backup_targets.extend(harness_dir / "scripts" / name for name in RUNTIME_SCRIPT_NAMES)
    backup_targets.extend(harness_dir / rel for rel in RUNTIME_DOC_REL_PATHS)
    if no_backup:
        print("Backup: skipped (--no-backup)")
        backed_up = 0
    else:
        backed_up = backup_files(harness_dir, backup_root, backup_targets, dry_run)
        print(f"Backup files: {backed_up} -> {backup_root}")

    rendered = materialize_manifest_files(
        harness_dir,
        files,
        timeout_seconds=timeout_seconds,
        require_checksum=require_checksum,
    )
    updated_files = write_rendered_files(rendered, dry_run)
    print(f"Manifest files applied: {updated_files}")

    stats = run_known_migrations(harness_dir, current_version, target_version, dry_run)
    wrote_version = write_runtime_version(
        harness_dir,
        target_version,
        dry_run,
        updated_by="update_runtime.py(remote)",
    )
    print(f"Runtime version file updated: {'yes' if wrote_version else 'no-change'}")
    return backed_up, stats


def fallback_local_update(
    *,
    harness_dir: Path,
    current_version: str,
    backup_root: Path,
    no_backup: bool,
    dry_run: bool,
) -> None:
    backup_targets = [harness_dir / "task.json", runtime_version_path(harness_dir)]
    backup_targets.extend(harness_dir / "scripts" / name for name in RUNTIME_SCRIPT_NAMES)
    backup_targets.extend(harness_dir / rel for rel in RUNTIME_DOC_REL_PATHS)
    if no_backup:
        print("Backup: skipped (--no-backup)")
    else:
        backed_up = backup_files(harness_dir, backup_root, backup_targets, dry_run)
        print(f"Backup files: {backed_up} -> {backup_root}")

    stats = run_known_migrations(harness_dir, current_version, LATEST_RUNTIME_VERSION, dry_run)
    target_version = LATEST_RUNTIME_VERSION
    if semver_gt(current_version, LATEST_RUNTIME_VERSION):
        # 当前版本已经高于本地内置迁移认知版本，禁止本地 fallback 降级覆盖。
        target_version = current_version
        print(
            "Local fallback keep current runtime version (no downgrade): "
            f"current={current_version} latest_known={LATEST_RUNTIME_VERSION}"
        )
    wrote_version = write_runtime_version(
        harness_dir,
        target_version,
        dry_run,
        updated_by="update_runtime.py(local-fallback)",
    )
    print(f"Runtime version file updated: {'yes' if wrote_version else 'no-change'}")
    print(
        "Migration summary: "
        f"task_json_changed={stats['task_json_changed']}, "
        f"context_cleaned={stats['context_cleaned']}, "
        f"files_removed={stats['files_removed']}"
    )


def resolve_backup_root(args: argparse.Namespace, harness_dir: Path) -> Path:
    if args.backup_dir:
        return Path(args.backup_dir).resolve()
    return harness_dir / "backups" / f"update-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def main() -> int:
    args = parse_args()
    target_dir = Path(args.target_dir).resolve()
    try:
        harness_dir = detect_harness_dir(target_dir)
    except RuntimeError as exc:
        print(f"Error: {exc}")
        return 1

    task_path = harness_dir / "task.json"
    if not task_path.exists():
        print(f"Error: task.json 不存在：{task_path}")
        return 1

    policy = load_policy(harness_dir)
    state = load_state(harness_dir)
    current_version, source = infer_current_version(harness_dir)
    if parse_semver(current_version) is None:
        print(f"Error: 无法识别当前版本：{current_version}")
        return 1

    print(f"Update target: {harness_dir}")
    print(f"Current runtime version: {current_version} (source={source})")
    print(f"Updater known latest: {LATEST_RUNTIME_VERSION}")
    if args.dry_run:
        print("Mode: dry-run")

    manifest_url = str(args.manifest_url or policy.get("manifest_url", "")).strip()
    if semver_gt(current_version, LATEST_RUNTIME_VERSION) and not manifest_url:
        print(
            "Warning: 当前项目版本高于本地 updater 的内置迁移版本，且未配置 manifest_url。"
            f" current={current_version} latest_known={LATEST_RUNTIME_VERSION}"
        )
        print("Warning: 仅可执行有限本地迁移；建议尽快配置远程更新源。")
    timeout_seconds = max(1, to_int(policy.get("request_timeout_seconds", 10), 10))
    require_checksum = bool(policy.get("require_checksum", True))
    backup_root = resolve_backup_root(args, harness_dir)

    # Automatic periodic mode: check policy + interval; auto-apply by bump rules.
    if args.check_remote:
        should_check, reason = should_check_remote(policy, state, args.force_check)
        if not should_check:
            print(f"Remote check skipped: {reason}")
            return 0
        print(f"Remote check trigger: {reason}")
        if not manifest_url:
            print("Remote check skipped: manifest_url not configured in update-policy.json")
            update_state_after_check(
                harness_dir,
                state,
                result="skipped-no-manifest-url",
                dry_run=args.dry_run,
            )
            return 0

        try:
            manifest = fetch_manifest(manifest_url, timeout_seconds)
            target_version, files = validate_manifest(manifest, current_version)
        except (RuntimeError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            print(f"Remote check failed: {exc}")
            update_state_after_check(
                harness_dir,
                state,
                result="check-failed",
                error=str(exc),
                dry_run=args.dry_run,
            )
            return 0

        if not semver_gt(target_version, current_version):
            print(f"Remote runtime is up-to-date: {target_version}")
            update_state_after_check(
                harness_dir,
                state,
                result="up-to-date",
                remote_version=target_version,
                dry_run=args.dry_run,
            )
            return 0

        bump = classify_bump(current_version, target_version)
        auto_apply = decide_auto_apply(policy, current_version, target_version)
        print(f"Remote update available: {current_version} -> {target_version} (bump={bump})")
        if not auto_apply:
            print("Auto-apply blocked by policy; update is only recorded.")
            update_state_after_check(
                harness_dir,
                state,
                result="update-available-policy-blocked",
                remote_version=target_version,
                dry_run=args.dry_run,
            )
            return 0

        try:
            apply_remote_update(
                harness_dir=harness_dir,
                manifest=manifest,
                current_version=current_version,
                target_version=target_version,
                files=files,
                backup_root=backup_root,
                no_backup=args.no_backup,
                dry_run=args.dry_run,
                timeout_seconds=timeout_seconds,
                require_checksum=require_checksum,
            )
        except (RuntimeError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            print(f"Remote apply failed: {exc}")
            update_state_after_check(
                harness_dir,
                state,
                result="apply-failed",
                remote_version=target_version,
                error=str(exc),
                dry_run=args.dry_run,
            )
            return 0

        update_state_after_check(
            harness_dir,
            state,
            result="updated",
            remote_version=target_version,
            dry_run=args.dry_run,
        )
        print("Done.")
        return 0

    # Manual mode: if manifest exists -> force check + apply latest; else fallback local migrations.
    if manifest_url:
        print("Manual mode: manifest configured, force check latest remote runtime.")
        try:
            manifest = fetch_manifest(manifest_url, timeout_seconds)
            target_version, files = validate_manifest(manifest, current_version)
        except (RuntimeError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            print(f"Remote fetch failed: {exc}")
            return 1

        if semver_gt(target_version, current_version):
            print(f"Apply remote update: {current_version} -> {target_version}")
            try:
                apply_remote_update(
                    harness_dir=harness_dir,
                    manifest=manifest,
                    current_version=current_version,
                    target_version=target_version,
                    files=files,
                    backup_root=backup_root,
                    no_backup=args.no_backup,
                    dry_run=args.dry_run,
                    timeout_seconds=timeout_seconds,
                    require_checksum=require_checksum,
                )
            except (RuntimeError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                print(f"Remote apply failed: {exc}")
                return 1
            print("Done.")
            return 0
        if semver_gt(current_version, target_version):
            print(
                "Remote runtime is older than current; skip version overwrite: "
                f"current={current_version} remote={target_version}"
            )
            print("Done.")
            return 0
        print(f"Remote runtime is already latest: {target_version}")
        wrote = write_runtime_version(
            harness_dir,
            target_version,
            args.dry_run,
            updated_by="update_runtime.py(remote-manual-noop)",
        )
        print(f"Runtime version file updated: {'yes' if wrote else 'no-change'}")
        print("Done.")
        return 0

    print("Manual mode: manifest_url not configured, run local migration fallback only.")
    fallback_local_update(
        harness_dir=harness_dir,
        current_version=current_version,
        backup_root=backup_root,
        no_backup=args.no_backup,
        dry_run=args.dry_run,
    )
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
