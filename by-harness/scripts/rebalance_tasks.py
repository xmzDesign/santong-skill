#!/usr/bin/env python3
"""
Rebalance feature tasks into sharded buckets.

Default strategy: group by category.
"""

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Rebalance tasks into sharded buckets.")
    parser.add_argument("--target-dir", required=True, help="目标项目目录")
    parser.add_argument(
        "--strategy",
        default="category",
        choices=["category"],
        help="分桶策略（当前仅支持 category）",
    )
    parser.add_argument(
        "--active-bucket",
        default="",
        help="指定重平衡后 active bucket（默认自动选择）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印计划，不落盘",
    )
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def slug(text: str):
    raw = (text or "misc").strip().lower()
    raw = re.sub(r"[^a-z0-9]+", "-", raw)
    raw = raw.strip("-")
    return raw or "misc"


def to_priority(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 10**9


def select_active_bucket(grouped, explicit: str):
    if explicit and explicit in grouped:
        return explicit
    with_pending = [k for k, feats in grouped.items() if any(not bool(f.get("passes")) for f in feats)]
    if with_pending:
        return sorted(with_pending)[0]
    return sorted(grouped)[0]


def build_index(active_bucket: str, bucket_defs):
    return {
        "version": "2",
        "mode": "sharded",
        "active_bucket": active_bucket,
        "updated": datetime.now().strftime("%Y-%m-%d"),
        "buckets": bucket_defs,
        "notes": [
            "优先读取 active_bucket 对应文件",
            "feature_list.json 作为兼容入口（同步 active bucket）",
        ],
    }


def main():
    args = parse_args()
    target_dir = Path(args.target_dir).resolve()
    legacy_path = target_dir / "feature_list.json"

    if not legacy_path.exists():
        print(f"Error: feature_list.json not found in {target_dir}")
        sys.exit(1)

    legacy = load_json(legacy_path)
    features = legacy.get("features", [])
    if not isinstance(features, list):
        print("Error: feature_list.json lacks valid features array")
        sys.exit(1)

    grouped = {}
    for feat in features:
        key = slug(str(feat.get("category", "misc")))
        grouped.setdefault(key, []).append(feat)

    if not grouped:
        print("Nothing to rebalance: no features found")
        return

    for feats in grouped.values():
        feats.sort(key=lambda f: (to_priority(f.get("priority")), str(f.get("id", ""))))

    active_key = select_active_bucket(grouped, args.active_bucket)
    bucket_defs = []
    bucket_payloads = {}
    for key, feats in sorted(grouped.items()):
        bucket_id = f"backlog-{key}"
        rel_path = f"task-harness/features/{bucket_id}.json"
        bucket_defs.append(
            {
                "id": bucket_id,
                "description": f"按 category={key} 自动分桶",
                "path": rel_path,
            }
        )
        bucket_payloads[bucket_id] = {
            "project": legacy.get("project", target_dir.name),
            "description": legacy.get("description", ""),
            "features": feats,
        }

    active_bucket_id = f"backlog-{active_key}"
    index_data = build_index(active_bucket_id, bucket_defs)

    print("Rebalance plan:")
    for bucket_id, payload in bucket_payloads.items():
        print(f"  - {bucket_id}: {len(payload['features'])} features")
    print(f"Active bucket: {active_bucket_id}")

    if args.dry_run:
        print("Dry run mode; no files written.")
        return

    # Backup legacy once.
    backup_path = target_dir / "feature_list.legacy.json"
    if not backup_path.exists():
        shutil.copy2(legacy_path, backup_path)

    # Write bucket files.
    for bucket_id, payload in bucket_payloads.items():
        bucket_path = target_dir / "task-harness" / "features" / f"{bucket_id}.json"
        dump_json(bucket_path, payload)

    # Write index.
    index_path = target_dir / "task-harness" / "index.json"
    dump_json(index_path, index_data)

    # Sync legacy view to active bucket for compatibility.
    active_payload = bucket_payloads[active_bucket_id]
    dump_json(legacy_path, active_payload)

    print(f"Wrote index: {index_path}")
    print(f"Backup legacy file: {backup_path}")
    print("Rebalance completed.")


if __name__ == "__main__":
    main()
