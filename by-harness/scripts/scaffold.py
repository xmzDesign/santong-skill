#!/usr/bin/env python3
"""
by-harness scaffold generator.

Standalone initializer:
- Generate main harness loop skeleton
- Generate task tracking files

No runtime dependency on other skills.
"""

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

HARNESS_DIR_NAME = ".harness"
HARNESS_RUNTIME_VERSION = "2.1.0"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Initialize by-harness standalone scaffold."
    )
    parser.add_argument("--project-name", required=True, help="项目名称")
    parser.add_argument("--description", required=True, help="项目描述")
    parser.add_argument("--tech-stack", default="", help="技术栈（可选）")
    parser.add_argument("--project-type", default="", help="项目类型（可选）")
    parser.add_argument("--design-guidance", default="无", help="设计约束（可选）")
    parser.add_argument("--target-dir", required=True, help="目标目录")
    parser.add_argument("--force", action="store_true", help="覆盖已存在文件")
    return parser.parse_args()


def get_skill_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def substitute(template: str, args) -> str:
    today = date.today().isoformat()
    replacements = {
        "{{PROJECT_NAME}}": args.project_name,
        "{{TECH_STACK}}": args.tech_stack or "Not specified",
        "{{PROJECT_TYPE}}": args.project_type or "General",
        "{{DATE}}": today,
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
        "{{HARNESS_RUNTIME_VERSION}}": HARNESS_RUNTIME_VERSION,
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

    if template_path.suffix in (".md", ".txt", ".json", ".toml", ".sh"):
        content = template_path.read_text(encoding="utf-8")
        rendered = substitute(content, args)
        target_path.write_text(rendered, encoding="utf-8")
    else:
        shutil.copy2(template_path, target_path)

    if target_path.suffix in (".py", ".sh"):
        target_path.chmod(target_path.stat().st_mode | 0o755)

    print(f"  CREATE: {target_path}")
    return True


def _hook_group_signature(group: dict):
    matcher = group.get("matcher", "")
    hooks = group.get("hooks", [])
    hook_sigs = []
    for hook in hooks:
        hook_sigs.append(f"{hook.get('type', '')}:{hook.get('command', '')}")
    return f"{matcher}|{'|'.join(hook_sigs)}"


def merge_settings(target_dir: Path, template_settings_path: Path):
    settings_path = target_dir / ".claude" / "settings.json"
    template_content = json.loads(template_settings_path.read_text(encoding="utf-8"))

    if settings_path.exists():
        existing = json.loads(settings_path.read_text(encoding="utf-8"))
    else:
        existing = {}

    if "hooks" not in existing or not isinstance(existing.get("hooks"), dict):
        existing["hooks"] = {}
    for event_name, groups in template_content.get("hooks", {}).items():
        if event_name not in existing["hooks"] or not isinstance(existing["hooks"][event_name], list):
            existing["hooks"][event_name] = groups
            continue
        existing_sigs = {_hook_group_signature(g) for g in existing["hooks"][event_name]}
        for group in groups:
            sig = _hook_group_signature(group)
            if sig not in existing_sigs:
                existing["hooks"][event_name].append(group)
                existing_sigs.add(sig)

    existing_permissions = existing.get("permissions", {})
    template_permissions = template_content.get("permissions", {})
    merged_permissions = {}
    for key in ("allow", "deny"):
        values = []
        for source in (existing_permissions.get(key, []), template_permissions.get(key, [])):
            for item in source:
                if item not in values:
                    values.append(item)
        if values:
            merged_permissions[key] = values
    if merged_permissions:
        existing["permissions"] = merged_permissions

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  MERGE: {settings_path}")


def merge_codex_hooks(target_dir: Path, template_hooks_path: Path):
    hooks_path = target_dir / ".codex" / "hooks.json"
    template_content = json.loads(template_hooks_path.read_text(encoding="utf-8"))
    template_hooks_map = template_content.get("hooks", {})

    if hooks_path.exists():
        existing = json.loads(hooks_path.read_text(encoding="utf-8"))
    else:
        existing = {}

    if "hooks" not in existing or not isinstance(existing.get("hooks"), dict):
        existing["hooks"] = {}

    for event_name, groups in template_hooks_map.items():
        if event_name not in existing["hooks"] or not isinstance(existing["hooks"][event_name], list):
            existing["hooks"][event_name] = groups
            continue

        existing_sigs = {_hook_group_signature(g) for g in existing["hooks"][event_name]}
        for group in groups:
            sig = _hook_group_signature(group)
            if sig not in existing_sigs:
                existing["hooks"][event_name].append(group)
                existing_sigs.add(sig)

    hooks_path.parent.mkdir(parents=True, exist_ok=True)
    hooks_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  MERGE: {hooks_path}")


def ship_runtime_script(
    skill_dir: Path,
    harness_dir: Path,
    script_name: str,
    args,
) -> bool:
    src = skill_dir / "scripts" / script_name
    dst = harness_dir / "scripts" / script_name
    if not src.exists():
        print(f"  WARN: helper not found: {src}")
        return False
    return generate_file(src, dst, args)


def verify_outputs(target_dir: Path):
    required = [
        "AGENTS.md",
        f"{HARNESS_DIR_NAME}/CLAUDE.md",
        f"{HARNESS_DIR_NAME}/TASK-HARNESS.md",
        f"{HARNESS_DIR_NAME}/task-harness/index.json",
        f"{HARNESS_DIR_NAME}/task-harness/features/backlog-core.json",
        f"{HARNESS_DIR_NAME}/runtime-version.json",
        f"{HARNESS_DIR_NAME}/update-policy.json",
        f"{HARNESS_DIR_NAME}/progress.txt",
        f"{HARNESS_DIR_NAME}/scripts/session_close.py",
        f"{HARNESS_DIR_NAME}/scripts/ensure_task_branch.py",
        f"{HARNESS_DIR_NAME}/scripts/task_switch.py",
        f"{HARNESS_DIR_NAME}/scripts/update_runtime.py",
        f"{HARNESS_DIR_NAME}/init.sh",
        f"{HARNESS_DIR_NAME}/task.json",
        ".codex/config.toml",
        ".codex/hooks.json",
        ".codex/hooks/context-injector.py",
        ".codex/hooks/loop-detector.py",
        ".codex/hooks/pre-completion-check.py",
        ".claude/settings.json",
        f"{HARNESS_DIR_NAME}/docs/contracts/TEMPLATE.md",
        f"{HARNESS_DIR_NAME}/docs/java-dev-conventions.md",
        f"{HARNESS_DIR_NAME}/docs/frontend-dev-conventions.md",
        f"{HARNESS_DIR_NAME}/docs/qa",
        f"{HARNESS_DIR_NAME}/task-harness/progress",
    ]
    missing = [rel for rel in required if not (target_dir / rel).exists()]
    if missing:
        raise RuntimeError("Missing files after scaffold:\n- " + "\n- ".join(missing))


def main():
    args = parse_args()
    skill_dir = get_skill_dir()
    templates_harness = skill_dir / "templates" / "harness"
    target_dir = Path(args.target_dir).resolve()

    if not target_dir.exists():
        print(f"Error: target directory does not exist: {target_dir}")
        sys.exit(1)

    harness_dir = target_dir / HARNESS_DIR_NAME
    file_mappings = [
        ("harness/AGENTS.md", "AGENTS.md"),
        ("harness/CLAUDE.md", f"{HARNESS_DIR_NAME}/CLAUDE.md"),
        ("harness/docs/architecture.md", f"{HARNESS_DIR_NAME}/docs/architecture.md"),
        ("harness/docs/golden-principles.md", f"{HARNESS_DIR_NAME}/docs/golden-principles.md"),
        ("harness/docs/sprint-workflow.md", f"{HARNESS_DIR_NAME}/docs/sprint-workflow.md"),
        ("harness/docs/java-dev-conventions.md", f"{HARNESS_DIR_NAME}/docs/java-dev-conventions.md"),
        ("harness/docs/frontend-dev-conventions.md", f"{HARNESS_DIR_NAME}/docs/frontend-dev-conventions.md"),
        ("harness/docs/contracts/TEMPLATE.md", f"{HARNESS_DIR_NAME}/docs/contracts/TEMPLATE.md"),
        ("harness/agents/planner.md", ".claude/agents/planner.md"),
        ("harness/agents/generator.md", ".claude/agents/generator.md"),
        ("harness/agents/evaluator.md", ".claude/agents/evaluator.md"),
        ("harness/agents/doc-gardener.md", ".claude/agents/doc-gardener.md"),
        ("harness/commands/plan.md", ".claude/commands/plan.md"),
        ("harness/commands/build.md", ".claude/commands/build.md"),
        ("harness/commands/qa.md", ".claude/commands/qa.md"),
        ("harness/commands/sprint.md", ".claude/commands/sprint.md"),
        ("harness/hooks/loop-detector.py", ".claude/hooks/loop-detector.py"),
        ("harness/hooks/pre-completion-check.py", ".claude/hooks/pre-completion-check.py"),
        ("harness/hooks/context-injector.py", ".claude/hooks/context-injector.py"),
        ("harness/codex/config.toml", ".codex/config.toml"),
        ("harness/codex/hooks/context-injector.py", ".codex/hooks/context-injector.py"),
        ("harness/codex/hooks/loop-detector.py", ".codex/hooks/loop-detector.py"),
        ("harness/codex/hooks/pre-completion-check.py", ".codex/hooks/pre-completion-check.py"),
        ("task/index.json", f"{HARNESS_DIR_NAME}/task-harness/index.json"),
        ("task/backlog-core.json", f"{HARNESS_DIR_NAME}/task-harness/features/backlog-core.json"),
        ("task/runtime-version.json", f"{HARNESS_DIR_NAME}/runtime-version.json"),
        ("task/update-policy.json", f"{HARNESS_DIR_NAME}/update-policy.json"),
        ("task/progress.txt", f"{HARNESS_DIR_NAME}/progress.txt"),
        ("task/init.sh", f"{HARNESS_DIR_NAME}/init.sh"),
        ("task/task.json", f"{HARNESS_DIR_NAME}/task.json"),
        ("task/TASK-HARNESS.md", f"{HARNESS_DIR_NAME}/TASK-HARNESS.md"),
    ]

    print(f"\nInitializing by-harness in: {target_dir}")
    print(f"Project: {args.project_name}")
    print(f"Description: {args.description}")
    print(f"Tech stack: {args.tech_stack or 'Not specified'}")
    print(f"Project type: {args.project_type or 'General'}")
    print()

    created = 0
    skipped = 0
    for template_rel, target_rel in file_mappings:
        template_path = skill_dir / "templates" / template_rel
        target_path = target_dir / target_rel
        if not template_path.exists():
            print(f"  WARN: template not found: {template_path}")
            continue
        if generate_file(template_path, target_path, args):
            created += 1
        else:
            skipped += 1

    # Ship runtime helpers into initialized project
    for runtime_script in (
        "session_close.py",
        "ensure_task_branch.py",
        "task_switch.py",
        "update_runtime.py",
        "upgrade_legacy_repo.py",
    ):
        if ship_runtime_script(skill_dir, harness_dir, runtime_script, args):
            created += 1
        else:
            skipped += 1

    (harness_dir / "docs" / "specs").mkdir(parents=True, exist_ok=True)
    (harness_dir / "docs" / "plans").mkdir(parents=True, exist_ok=True)
    (harness_dir / "docs" / "qa").mkdir(parents=True, exist_ok=True)
    (harness_dir / "task-harness" / "progress").mkdir(parents=True, exist_ok=True)

    merge_settings(target_dir, templates_harness / "settings.json")
    merge_codex_hooks(target_dir, templates_harness / "codex" / "hooks.json")

    try:
        verify_outputs(target_dir)
    except RuntimeError as exc:
        print(f"\nError: {exc}")
        sys.exit(1)

    print(f"\nDone. Created {created} files, skipped {skipped} files.")
    print("\nNext steps:")
    print(f"  1. bash {HARNESS_DIR_NAME}/init.sh")
    print(f"  2. 阅读 AGENTS.md 与 {HARNESS_DIR_NAME}/TASK-HARNESS.md")
    print("  3. 选择 passes=false 的 feature，执行 plan/build/qa 闭环")
    print(f"  4. 单元测试通过即可更新 passes=true（QA 非阻塞），并写入 {HARNESS_DIR_NAME}/task-harness/progress/YYYY-MM.md")
    print(f"  5. 会话结束执行：python3 {HARNESS_DIR_NAME}/scripts/session_close.py --target-dir . --feature-id <feat-id>")
    print(f"  6. 自动续跑下个任务（当前分支）：python3 {HARNESS_DIR_NAME}/scripts/task_switch.py continue --target-dir .")
    print(f"  7. 配置并启用远程更新：编辑 {HARNESS_DIR_NAME}/update-policy.json")


if __name__ == "__main__":
    main()
