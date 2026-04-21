#!/usr/bin/env python3
"""Upgrade initialized by-harness projects to latest runtime defaults.

Upgrade scope (safe defaults):
1) Refresh runtime scripts in `.harness/scripts/`
2) Migrate `.harness/task.json` session_control to current-branch mode

The command is idempotent and keeps existing task data.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

HARNESS_DIR_NAME = ".harness"
RUNTIME_SCRIPTS = ("session_close.py", "ensure_task_branch.py", "task_switch.py")
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upgrade existing by-harness repository runtime.")
    parser.add_argument("--target-dir", required=True, help="已初始化仓库目录（或 .harness 目录）")
    parser.add_argument("--dry-run", action="store_true", help="只打印变更计划，不落盘")
    parser.add_argument("--no-backup", action="store_true", help="跳过升级前备份")
    parser.add_argument(
        "--backup-dir",
        default="",
        help="自定义备份目录（默认 .harness/backups/upgrade-YYYYMMDD-HHMMSS）",
    )
    return parser.parse_args()


def get_skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def normalize_mode(raw: Any) -> str:
    text = str(raw or "").strip().lower()
    if text in {"hard_new_session", "hard", "new_session"}:
        return "hard_new_session"
    if text in {"soft_reset", "soft", "reset"}:
        return "soft_reset"
    return DEFAULT_MODE


def detect_harness_dir(target: Path) -> Path:
    if target.name == HARNESS_DIR_NAME and target.exists():
        return target
    harness_dir = target / HARNESS_DIR_NAME
    if harness_dir.exists():
        return harness_dir
    raise RuntimeError(f"未检测到 {HARNESS_DIR_NAME} 目录：{target}")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def migrate_task_json(data: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    changed = False
    payload = dict(data) if isinstance(data, dict) else {}
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

    next_control: dict[str, Any] = {
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
    today = datetime.now().strftime("%Y-%m-%d")
    if str(payload.get("updated", "")) != today:
        payload["updated"] = today
        changed = True
    return payload, changed


def copy_runtime_scripts(skill_dir: Path, harness_dir: Path, dry_run: bool) -> int:
    count = 0
    dst_dir = harness_dir / "scripts"
    for name in RUNTIME_SCRIPTS:
        src = skill_dir / "scripts" / name
        dst = dst_dir / name
        if not src.exists():
            raise RuntimeError(f"运行时脚本缺失：{src}")
        if dry_run:
            print(f"[dry-run] runtime: {src} -> {dst}")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            dst.chmod(dst.stat().st_mode | 0o755)
        count += 1
    return count


def main() -> int:
    args = parse_args()
    target_dir = Path(args.target_dir).resolve()
    skill_dir = get_skill_dir()

    try:
        harness_dir = detect_harness_dir(target_dir)
    except RuntimeError as exc:
        print(f"Error: {exc}")
        return 1

    task_json_path = harness_dir / "task.json"
    if not task_json_path.exists():
        print(f"Error: task.json 不存在：{task_json_path}")
        return 1

    backup_root = (
        Path(args.backup_dir).resolve()
        if args.backup_dir
        else harness_dir / "backups" / f"upgrade-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )

    backup_targets = [task_json_path] + [harness_dir / "scripts" / name for name in RUNTIME_SCRIPTS]

    print(f"Upgrade target: {harness_dir}")
    if args.dry_run:
        print("Mode: dry-run")

    if not args.no_backup:
        backed_up = backup_files(harness_dir, backup_root, backup_targets, args.dry_run)
        print(f"Backup files: {backed_up} -> {backup_root}")
    else:
        print("Backup: skipped (--no-backup)")

    runtime_count = copy_runtime_scripts(skill_dir, harness_dir, args.dry_run)
    print(f"Runtime scripts refreshed: {runtime_count}")

    task_payload = load_json(task_json_path)
    migrated, changed = migrate_task_json(task_payload)
    if changed:
        if args.dry_run:
            print(f"[dry-run] migrate task config: {task_json_path}")
        else:
            dump_json(task_json_path, migrated)
        print("Task config migrated: yes")
    else:
        print("Task config migrated: no-change")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
