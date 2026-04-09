#!/usr/bin/env python3
"""
Session close helper for by-harness projects.

Actions:
1) Append progress.txt
2) Generate HANDOFF.md
3) Print next task recommendation
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Close current by-harness session.")
    parser.add_argument("--target-dir", required=True, help="目标项目目录")
    parser.add_argument("--feature-id", default="", help="本次会话处理的 feature ID（可选）")
    parser.add_argument(
        "--outcome",
        default="in-progress",
        choices=["pass", "fail", "blocked", "in-progress"],
        help="本次会话结果",
    )
    parser.add_argument(
        "--qa-score",
        type=float,
        default=-1,
        help="QA 分数（未知可不填）",
    )
    parser.add_argument(
        "--note",
        action="append",
        default=[],
        help="本次会话说明（可重复）",
    )
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def count_sessions(progress_content: str) -> int:
    matches = re.findall(r"会话 #(\d+)\s*-", progress_content)
    if not matches:
        return 0
    return max(int(item) for item in matches)


def find_feature(features, feature_id: str):
    if not feature_id:
        return None
    for feat in features:
        if str(feat.get("id", "")).strip() == feature_id:
            return feat
    return None


def to_priority(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 10**9


def next_pending_feature(features, exclude_id: str = ""):
    pending = [f for f in features if not bool(f.get("passes")) and str(f.get("id", "")) != exclude_id]
    if not pending:
        return None
    pending.sort(key=lambda f: (to_priority(f.get("priority")), str(f.get("id", ""))))
    return pending[0]


def append_progress(
    progress_path: Path,
    feature,
    outcome: str,
    qa_score: float,
    notes,
    total: int,
    passed: int,
    next_feature,
):
    now = datetime.now()
    content = progress_path.read_text(encoding="utf-8") if progress_path.exists() else ""
    session_no = count_sessions(content) + 1

    feat_id = str(feature.get("id", "n/a")) if feature else "n/a"
    feat_desc = str(feature.get("description", "未指定任务")) if feature else "未指定任务"
    qa_text = f"{qa_score:.1f}" if qa_score >= 0 else "n/a"
    note_lines = notes if notes else ["本轮按闭环推进任务，详见提交与 QA 报告。"]
    next_text = (
        f"{next_feature.get('id')} ({next_feature.get('description')})"
        if next_feature
        else "无（全部任务已完成）"
    )

    entry = (
        "\n----------------------------------------\n"
        f"会话 #{session_no} - {feat_id}: {feat_desc}\n"
        "----------------------------------------\n"
        f"时间: {now.strftime('%Y-%m-%d %H:%M')}\n\n"
        "结果:\n"
        f"  - outcome: {outcome}\n"
        f"  - qa_score: {qa_text}\n"
    )

    if feature:
        entry += (
            f"  - spec: {feature.get('spec_path', 'n/a')}\n"
            f"  - contract: {feature.get('contract_path', 'n/a')}\n"
            f"  - qa_report: {feature.get('qa_report_path', 'n/a')}\n"
        )

    entry += "\n完成工作:\n"
    for line in note_lines:
        entry += f"  - {line}\n"

    entry += (
        "\n进度:\n"
        f"  - 已完成: {passed}/{total}\n"
        f"  - 下一个: {next_text}\n"
    )

    progress_path.write_text(content + entry, encoding="utf-8")


def write_handoff(
    handoff_path: Path,
    feature,
    outcome: str,
    qa_score: float,
    notes,
    total: int,
    passed: int,
    next_feature,
):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    feat_id = str(feature.get("id", "n/a")) if feature else "n/a"
    feat_desc = str(feature.get("description", "未指定任务")) if feature else "未指定任务"
    qa_text = f"{qa_score:.1f}" if qa_score >= 0 else "n/a"
    next_text = (
        f"{next_feature.get('id')} - {next_feature.get('description')}"
        if next_feature
        else "无（全部任务已完成）"
    )

    lines = [
        "# HANDOFF",
        "",
        f"生成时间: {now}",
        "",
        "## Summary",
        f"- 当前会话任务: {feat_id} - {feat_desc}",
        f"- 会话结果: {outcome}",
        f"- QA 分数: {qa_text}",
        f"- 任务进度: {passed}/{total}",
        "",
        "## Decisions",
    ]
    for line in notes if notes else ["未提供额外决策说明。"]:
        lines.append(f"- {line}")

    lines.extend(
        [
            "",
            "## Files / Artifacts",
            f"- feature_list.json",
            f"- progress.txt",
            f"- HANDOFF.md",
        ]
    )

    if feature:
        lines.extend(
            [
                f"- {feature.get('spec_path', 'n/a')}",
                f"- {feature.get('contract_path', 'n/a')}",
                f"- {feature.get('qa_report_path', 'n/a')}",
            ]
        )

    lines.extend(
        [
            "",
            "## Open Loops",
            "- 若 outcome 不是 pass，请优先处理失败项与阻塞原因。",
            "- 未达 qa>=80 前，不应将 passes 置为 true。",
            "",
            "## Next Session Start",
            "1. bash init.sh",
            "2. 阅读 AGENTS.md 与 TASK-HARNESS.md",
            f"3. 优先任务: {next_text}",
            "4. 执行 plan -> build -> qa -> fix -> mark_pass",
        ]
    )

    handoff_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    args = parse_args()
    target_dir = Path(args.target_dir).resolve()
    feature_path = target_dir / "feature_list.json"
    progress_path = target_dir / "progress.txt"
    handoff_path = target_dir / "HANDOFF.md"

    if not feature_path.exists():
        print(f"Error: feature_list.json not found in {target_dir}")
        sys.exit(1)

    data = load_json(feature_path)
    features = data.get("features", [])
    if not isinstance(features, list):
        print("Error: feature_list.json lacks valid features array")
        sys.exit(1)

    feature = find_feature(features, args.feature_id)
    if args.feature_id and feature is None:
        print(f"Error: feature id not found: {args.feature_id}")
        sys.exit(1)

    total = len(features)
    passed = sum(1 for feat in features if bool(feat.get("passes")))
    next_feature = next_pending_feature(features, exclude_id=str(feature.get("id", "")) if feature else "")

    append_progress(
        progress_path=progress_path,
        feature=feature,
        outcome=args.outcome,
        qa_score=args.qa_score,
        notes=args.note,
        total=total,
        passed=passed,
        next_feature=next_feature,
    )

    write_handoff(
        handoff_path=handoff_path,
        feature=feature,
        outcome=args.outcome,
        qa_score=args.qa_score,
        notes=args.note,
        total=total,
        passed=passed,
        next_feature=next_feature,
    )

    print(f"Updated progress: {progress_path}")
    print(f"Generated handoff: {handoff_path}")
    if next_feature:
        print(f"Next recommended task: {next_feature.get('id')} - {next_feature.get('description')}")
    else:
        print("Next recommended task: none (all tasks are passed)")


if __name__ == "__main__":
    main()
