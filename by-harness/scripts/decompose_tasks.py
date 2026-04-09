#!/usr/bin/env python3
"""
by-harness task decomposition helper.

Append new tasks into feature list storage with harness-closed-loop defaults.
Supports:
- legacy mode: feature_list.json
- sharded mode: task-harness/index.json + task-harness/features/*.json
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Append new decomposed tasks into feature list storage."
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
    parser.add_argument(
        "--bucket",
        default="",
        help="目标任务桶 ID（仅 sharded 模式有效；默认 active_bucket）",
    )
    parser.add_argument(
        "--use-legacy",
        action="store_true",
        help="强制使用 legacy 模式（feature_list.json）",
    )
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
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


def artifact_paths(feature_id: str):
    return {
        "spec_path": f"docs/specs/{feature_id}.md",
        "contract_path": f"docs/contracts/{feature_id}.md",
        "qa_report_path": f"docs/qa/{feature_id}.md",
    }


def ensure_artifact_fields(features):
    updated = 0
    for feat in features:
        feature_id = str(feat.get("id", "")).strip()
        if not feature_id:
            continue
        paths = artifact_paths(feature_id)
        for key, value in paths.items():
            if not feat.get(key):
                feat[key] = value
                updated += 1
    return updated


def build_feature(item_desc: str, feature_id: str, category: str, priority: int):
    paths = artifact_paths(feature_id)
    return {
        "id": feature_id,
        "category": category,
        "priority": priority,
        "description": item_desc,
        "file": None,
        "spec_path": paths["spec_path"],
        "contract_path": paths["contract_path"],
        "qa_report_path": paths["qa_report_path"],
        "steps": [
            f"读取任务定义：feature_list 中 {feature_id} 的目标与约束",
            f"执行 plan：生成 {paths['spec_path']}",
            f"执行 contract：生成 {paths['contract_path']} 并明确验收标准与验证方式",
            "执行 build：按 contract 范围实现并完成自检（构建/测试/验收标准）",
            f"执行 qa：生成 {paths['qa_report_path']}，逐条验证并评分，目标 >= 80/100",
            "若 qa < 80，进入 fix 循环（最多 3 轮）",
            "执行 mark_pass：仅在 qa>=80 后将 passes 置为 true",
        ],
        "passes": False,
        "verification": "必须有 qa 报告且 score >= 80/100，验收标准逐条可追溯",
    }


def resolve_store(target_dir: Path, bucket_arg: str, use_legacy: bool):
    index_path = target_dir / "task-harness" / "index.json"
    if use_legacy or not index_path.exists():
        return {
            "mode": "legacy",
            "feature_path": target_dir / "feature_list.json",
            "bucket_id": "legacy",
            "index": None,
            "index_path": index_path,
        }

    index = load_json(index_path)
    buckets = index.get("buckets", [])
    if not isinstance(buckets, list) or not buckets:
        raise RuntimeError("task-harness/index.json 缺少有效 buckets 配置")

    bucket_id = bucket_arg or index.get("active_bucket", "")
    if not bucket_id:
        bucket_id = buckets[0].get("id", "")
    bucket_obj = next((b for b in buckets if b.get("id") == bucket_id), None)
    if bucket_obj is None:
        valid = ", ".join(str(b.get("id", "")) for b in buckets)
        raise RuntimeError(f"bucket 不存在: {bucket_id}，可选: {valid}")

    rel_path = bucket_obj.get("path", "")
    if not rel_path:
        raise RuntimeError(f"bucket {bucket_id} 未配置 path")

    return {
        "mode": "sharded",
        "feature_path": target_dir / rel_path,
        "bucket_id": bucket_id,
        "index": index,
        "index_path": index_path,
    }


def load_or_init_feature_doc(feature_path: Path, target_dir: Path):
    if feature_path.exists():
        data = load_json(feature_path)
        if not isinstance(data.get("features"), list):
            data["features"] = []
        return data

    legacy = target_dir / "feature_list.json"
    if legacy.exists():
        data = load_json(legacy)
        if not isinstance(data.get("features"), list):
            data["features"] = []
        data["features"] = []
        return data

    return {
        "project": target_dir.name,
        "description": "待补充",
        "features": [],
    }


def aggregate_features(target_dir: Path, store):
    if store["mode"] == "legacy":
        return load_json(store["feature_path"]).get("features", [])

    all_features = []
    index = store["index"] or {}
    for bucket in index.get("buckets", []):
        rel_path = bucket.get("path", "")
        if not rel_path:
            continue
        feature_path = target_dir / rel_path
        if feature_path.exists():
            data = load_json(feature_path)
            features = data.get("features", [])
            if isinstance(features, list):
                all_features.extend(features)
    return all_features


def sync_legacy_view(target_dir: Path, data):
    legacy_path = target_dir / "feature_list.json"
    dump_json(legacy_path, data)


def update_task_summary(target_dir: Path, all_features):
    task_json = target_dir / "task.json"
    if not task_json.exists():
        return

    data = load_json(task_json)
    summary = data.get("summary", {})
    summary["total_features"] = len(all_features)
    categories = {}
    for feat in all_features:
        category = str(feat.get("category", "unknown"))
        categories[category] = categories.get(category, 0) + 1
    summary["categories"] = categories
    data["summary"] = summary
    data["updated"] = datetime.now().strftime("%Y-%m-%d")
    dump_json(task_json, data)


def append_progress_note(target_dir: Path, added_ids, bucket_id: str, mode: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    note = (
        "\n----------------------------------------\n"
        "任务拆解更新\n"
        "----------------------------------------\n"
        f"时间: {now}\n"
        f"新增任务: {', '.join(added_ids)}\n"
        f"任务桶: {bucket_id}\n"
        "说明: 新任务已按 harness 闭环模板生成（read task/plan/build/qa/fix/mark_pass）。\n"
    )

    if mode == "sharded":
        monthly = datetime.now().strftime("%Y-%m")
        progress_path = target_dir / "task-harness" / "progress" / f"{monthly}.md"
    else:
        progress_path = target_dir / "progress.txt"

    content = progress_path.read_text(encoding="utf-8") if progress_path.exists() else ""
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path.write_text(content + note, encoding="utf-8")


def main():
    args = parse_args()
    target_dir = Path(args.target_dir).resolve()

    try:
        store = resolve_store(target_dir, args.bucket, args.use_legacy)
    except RuntimeError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    feature_path = store["feature_path"]
    data = load_or_init_feature_doc(feature_path, target_dir)
    if not isinstance(data.get("features"), list):
        data["features"] = []

    features = data["features"]
    repaired = ensure_artifact_fields(features)

    # Ensure id/priority are globally monotonic across all buckets in sharded mode.
    existing_for_index = aggregate_features(target_dir, store)
    if store["mode"] == "legacy":
        existing_for_index = features

    idx_start = next_start_index(existing_for_index, args.id_prefix)
    pri_start = next_priority_start(existing_for_index, args.start_priority)

    added = []
    for offset, item_desc in enumerate(args.items):
        feature_id = f"{args.id_prefix}-{idx_start + offset:02d}"
        priority = pri_start + offset
        feat = build_feature(item_desc, feature_id, args.category, priority)
        features.append(feat)
        added.append(feature_id)

    data["features"] = features
    dump_json(feature_path, data)

    # Keep feature_list.json as compatibility view in sharded mode.
    if store["mode"] == "sharded":
        sync_legacy_view(target_dir, data)

    all_features = aggregate_features(target_dir, store)
    update_task_summary(target_dir, all_features)
    append_progress_note(target_dir, added, store["bucket_id"], store["mode"])

    print("Added tasks:")
    for task_id in added:
        print(f"  - {task_id}")
    if repaired > 0:
        print(f"Backfilled artifact fields on existing tasks: {repaired} fields updated")
    print(f"Target store: {store['mode']} / bucket={store['bucket_id']}")
    print(f"Feature file updated: {feature_path}")
    if store["mode"] == "sharded":
        print(f"Legacy mirror synced: {target_dir / 'feature_list.json'}")
    print("Reminder: each task must run read task -> plan -> build -> qa -> fix -> mark_pass.")


if __name__ == "__main__":
    main()
