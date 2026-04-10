#!/usr/bin/env python3
"""
Task Harness scaffold generator.

Generate task-harness files in a target project directory, and integrate with
Harness Engineering by default (requires AGENTS.md to exist).
"""

import argparse
import sys
from datetime import date
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Initialize task-harness files in a project directory."
    )
    parser.add_argument("--project-name", required=True, help="项目名称")
    parser.add_argument(
        "--description",
        required=True,
        help="项目描述（一句话概括目标和范围）",
    )
    parser.add_argument(
        "--tech-stack",
        default="待补充",
        help="主要技术栈信息（默认：待补充）",
    )
    parser.add_argument(
        "--design-guidance",
        default="无",
        help="设计约束和风格指南（默认：无）",
    )
    parser.add_argument("--target-dir", required=True, help="目标项目目录")
    parser.add_argument(
        "--force",
        action="store_true",
        help="覆盖已存在的目标文件",
    )
    parser.add_argument(
        "--allow-missing-main-contract",
        action="store_true",
        help="允许目标目录缺少 AGENTS.md（默认不允许）",
    )
    return parser.parse_args()


def get_skill_dir():
    return Path(__file__).resolve().parent.parent


def substitute(template: str, args) -> str:
    today = date.today().isoformat()
    replacements = {
        "{{项目名称}}": args.project_name,
        "{{项目描述，一句话概括目标和范围}}": args.description,
        "{{一句话描述项目目标和范围}}": args.description,
        "{{项目描述}}": args.description,
        "{{主要技术栈信息}}": args.tech_stack or "待补充",
        "{{设计约束和风格指南}}": args.design_guidance or "无",
        "{{YYYY-MM-DD}}": today,
        "{{里程碑 1 名称}}": "M1-首批功能闭环",
        "{{里程碑描述}}": "完成首批高优先级 feature 的 plan/build/qa 闭环",
        "{{重要发现 1}}": "待首次会话补充",
        "{{重要发现 2}}": "待首次会话补充",
        "{{重要发现 3}}": "待首次会话补充",
    }

    out = template
    for key, value in replacements.items():
        out = out.replace(key, value)
    return out


def generate_file(template_path: Path, target_path: Path, args) -> bool:
    if target_path.exists() and not args.force:
        print(f"  SKIP (exists): {target_path}")
        return False

    target_path.parent.mkdir(parents=True, exist_ok=True)
    content = template_path.read_text(encoding="utf-8")
    rendered = substitute(content, args)
    target_path.write_text(rendered, encoding="utf-8")

    if target_path.name == "init.sh":
        target_path.chmod(target_path.stat().st_mode | 0o755)

    print(f"  CREATE: {target_path}")
    return True


def validate_main_contract(target_dir: Path, allow_missing: bool) -> bool:
    agents_path = target_dir / "AGENTS.md"
    if agents_path.exists():
        return True

    if allow_missing:
        print("  WARN: AGENTS.md 缺失，未启用主闭环契约（你使用了 --allow-missing-main-contract）。")
        return True

    print("Error: 目标目录缺少 AGENTS.md。")
    print("建议先运行 harness-engineering 初始化主闭环，再执行 task-harness 脚手架。")
    print("如需跳过检查，可加参数：--allow-missing-main-contract")
    return False


def print_post_checks(target_dir: Path):
    checks = [
        ("主契约", target_dir / "AGENTS.md"),
        ("任务契约", target_dir / "TASK-HARNESS.md"),
        ("任务清单", target_dir / "feature_list.json"),
        ("进度日志", target_dir / "progress.txt"),
        ("初始化脚本", target_dir / "init.sh"),
        ("项目总览", target_dir / "task.json"),
    ]
    print("\nPost-check:")
    for label, path in checks:
        mark = "OK" if path.exists() else "MISSING"
        print(f"  - {label}: {mark} ({path})")


def main():
    args = parse_args()
    target_dir = Path(args.target_dir).resolve()
    templates_dir = get_skill_dir() / "references" / "templates"

    if not target_dir.exists():
        print(f"Error: target directory does not exist: {target_dir}")
        sys.exit(1)

    if not validate_main_contract(target_dir, args.allow_missing_main_contract):
        sys.exit(1)

    file_mappings = [
        ("feature_list.json", "feature_list.json"),
        ("progress.txt", "progress.txt"),
        ("init.sh", "init.sh"),
        ("task.json", "task.json"),
        ("TASK-HARNESS.md", "TASK-HARNESS.md"),
    ]

    print(f"\nInitializing task-harness in: {target_dir}")
    print(f"Project: {args.project_name}")
    print(f"Description: {args.description}")
    print(f"Tech stack: {args.tech_stack}")
    print()

    created = 0
    skipped = 0

    for template_rel, target_rel in file_mappings:
        template_path = templates_dir / template_rel
        target_path = target_dir / target_rel

        if not template_path.exists():
            print(f"  WARN: template not found: {template_path}")
            continue

        if generate_file(template_path, target_path, args):
            created += 1
        else:
            skipped += 1

    print(f"\nDone. Created {created} files, skipped {skipped} files.")
    print_post_checks(target_dir)
    print("\nNext steps:")
    print("  1. 运行 `bash init.sh`")
    print("  2. 阅读 `AGENTS.md` 与 `TASK-HARNESS.md`")
    print("  3. 选择一个 passes=false 的 feature 执行 plan/build/qa")
    print("  4. 单元测试通过即可更新 passes=true（QA 非阻塞），并追加 progress.txt")


if __name__ == "__main__":
    main()
