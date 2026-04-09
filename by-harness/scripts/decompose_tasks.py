#!/usr/bin/env python3
"""
by-harness task decomposition helper.

Append new tasks into feature_list.json with harness-closed-loop defaults.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Append new decomposed tasks into feature_list.json."
    )
    parser.add_argument("--target-dir", required=True, help="目标项目目录")
    parser.add_argument(
        "--item",
        action="append",
        dest="items",
        required=True,
        help="新增任务描述（可重复传多次）",
    )
    parser.add_argument("--category", default="feature", help="任务分类，默认 feature")
    parser.add_argument("--id-prefix", default="feat", help="ID 前缀，默认 feat")
    parser.add_argument(
        "--start-priority",
        type=int,
        default=0,
        help="优先级起点（0 表示自动从现有最大值+1）",
    )
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_id_index(feature_id: str, prefix: str) -> int:
    pattern = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
    match = pattern.match(feature_id)
    return int(match.group(1)) if match else 0


def next_start_index(features, prefix: str) -> int:
    max_idx = 0
    for feat in features:
        max_idx = max(max_idx, parse_id_index(str(feat.get("id", "")), prefix))
    return max_idx + 1


def next_priority_start(features, explicit_start: int) -> int:
    if explicit_start > 0:
        return explicit_start
    max_priority = 0
    for feat in features:
        try:
            max_priority = max(max_priority, int(feat.get("priority", 0)))
        except (TypeError, ValueError):
            pass
    return max_priority + 1


def build_feature(item_desc: str, feature_id: str, category: str, priority: int):
    short_name = feature_id.replace("-", "_")
    return {
        "id": feature_id,
        "category": category,
        "priority": priority,
        "description": item_desc,
        "file": None,
        "steps": [
            f"执行 plan：为该任务生成 docs/specs/{short_name}.md",
            f"执行 contract：在 docs/contracts/{short_name}.md 明确验收标准与验证方式",
            "执行 build：按 contract 范围实现并完成自检（构建/测试/验收标准）",
            "执行 qa：逐条验证并评分，目标 >= 80/100",
            "若 qa < 80，进入修复循环（最多 3 轮）",
            "qa 达标后更新 passes=true，并在 progress.txt 记录结果与证据",
        ],
        "passes": False,
        "verification": "必须有 qa 报告且 score >= 80/100，验收标准逐条可追溯",
    }


def update_task_summary(target_dir: Path, total_features: int, categories):
    task_json = target_dir / "task.json"
    if not task_json.exists():
        return

    data = load_json(task_json)
    summary = data.get("summary", {})
    summary["total_features"] = total_features
    summary["categories"] = categories
    data["summary"] = summary
    data["updated"] = datetime.now().strftime("%Y-%m-%d")
    dump_json(task_json, data)


def append_progress_note(target_dir: Path, added_ids):
    progress_path = target_dir / "progress.txt"
    if not progress_path.exists():
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    note = (
        "\n----------------------------------------\n"
        "任务拆解更新\n"
        "----------------------------------------\n"
        f"时间: {now}\n"
        f"新增任务: {', '.join(added_ids)}\n"
        "说明: 新任务已按 harness 闭环模板生成（plan/build/qa/fix）。\n"
    )
    progress_path.write_text(progress_path.read_text(encoding="utf-8") + note, encoding="utf-8")


def main():
    args = parse_args()
    target_dir = Path(args.target_dir).resolve()
    feature_path = target_dir / "feature_list.json"

    if not feature_path.exists():
        print(f"Error: feature_list.json not found in {target_dir}")
        sys.exit(1)

    data = load_json(feature_path)
    if not isinstance(data.get("features"), list):
        print("Error: feature_list.json lacks valid features array")
        sys.exit(1)

    features = data["features"]
    idx_start = next_start_index(features, args.id_prefix)
    pri_start = next_priority_start(features, args.start_priority)

    added = []
    for offset, item_desc in enumerate(args.items):
        feature_id = f"{args.id_prefix}-{idx_start + offset:02d}"
        priority = pri_start + offset
        feat = build_feature(item_desc, feature_id, args.category, priority)
        features.append(feat)
        added.append(feature_id)

    data["features"] = features
    dump_json(feature_path, data)

    categories = {}
    for feat in features:
        category = str(feat.get("category", "unknown"))
        categories[category] = categories.get(category, 0) + 1
    update_task_summary(target_dir, len(features), categories)
    append_progress_note(target_dir, added)

    print("Added tasks:")
    for task_id in added:
        print(f"  - {task_id}")
    print(f"feature_list.json updated: {feature_path}")
    print("Reminder: each task must run plan/build/qa; set passes=true only when qa>=80.")


if __name__ == "__main__":
    main()
