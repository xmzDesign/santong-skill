#!/bin/bash
# ==========================================
#  {{项目名称}} - Agent 环境初始化脚本
# ==========================================
# 用途：每个 Agent 会话开始时运行，快速恢复开发环境
# 用法：bash .harness/init.sh（legacy 项目可用 bash init.sh）

set -e

echo "=========================================="
echo "  {{项目名称}} - Agent 环境初始化"
echo "=========================================="

WORKSPACE_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$WORKSPACE_DIR/AGENTS.md" ]; then
  REPO_ROOT="$WORKSPACE_DIR"
else
  REPO_ROOT="$(cd "$WORKSPACE_DIR/.." && pwd)"
fi
WORKSPACE_NAME="$(basename "$WORKSPACE_DIR")"
if [ "$WORKSPACE_DIR" = "$REPO_ROOT" ]; then
  WORKSPACE_PREFIX=""
else
  WORKSPACE_PREFIX="$WORKSPACE_NAME/"
fi

cd "$WORKSPACE_DIR"

echo ""
echo "[1/5] 当前目录:"
echo "  仓库根目录: $REPO_ROOT"
echo "  Harness 工作目录: $WORKSPACE_DIR"

echo ""
echo "[2/5] Git 状态:"
if git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$REPO_ROOT" status --short || echo "  (无 git 变更)"
else
  echo "  (当前目录不是 git 仓库)"
fi

echo ""
echo "[3/5] 最近 10 条 commit:"
if git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$REPO_ROOT" log --oneline -10 || echo "  (无 commit 历史)"
else
  echo "  (当前目录不是 git 仓库)"
fi

echo ""
echo "[4/5] 功能完成进度:"
FEATURE_FILE="feature_list.json"
ACTIVE_BUCKET="legacy"
if [ -f "task-harness/index.json" ]; then
  MAP=$(python3 - <<'PY'
import json
from pathlib import Path

idx_path = Path("task-harness/index.json")
idx = json.loads(idx_path.read_text())
active = idx.get("active_bucket", "")
buckets = idx.get("buckets", [])
path = ""
for b in buckets:
    if b.get("id") == active:
        path = b.get("path", "")
        break
if not path and buckets:
    active = buckets[0].get("id", "")
    path = buckets[0].get("path", "")
print(path or "feature_list.json")
print(active or "legacy")
PY
)
  FEATURE_FILE=$(printf "%s\n" "$MAP" | sed -n '1p')
  ACTIVE_BUCKET=$(printf "%s\n" "$MAP" | sed -n '2p')
fi

if [ -f "$FEATURE_FILE" ]; then
  TOTAL_RAW=$(python3 -c "import json; f=open('$FEATURE_FILE'); d=json.load(f); print(len(d['features']))" 2>/dev/null || echo "0")
  PASSED_RAW=$(python3 -c "import json; f=open('$FEATURE_FILE'); d=json.load(f); print(sum(1 for x in d['features'] if x.get('passes')))" 2>/dev/null || echo "0")

  if [[ "$TOTAL_RAW" =~ ^[0-9]+$ ]]; then
    TOTAL="$TOTAL_RAW"
  else
    TOTAL=0
  fi

  if [[ "$PASSED_RAW" =~ ^[0-9]+$ ]]; then
    PASSED="$PASSED_RAW"
  else
    PASSED=0
  fi

  if [ "$PASSED" -gt "$TOTAL" ]; then
    PASSED="$TOTAL"
  fi

  echo "  任务桶: $ACTIVE_BUCKET"
  echo "  任务文件: $FEATURE_FILE"
  echo "  总计: $TOTAL 个功能"
  echo "  已完成: $PASSED 个"
  echo "  剩余: $((TOTAL - PASSED)) 个"

  echo ""
  echo "  未完成的功能:"
  python3 -c "
import json
with open('$FEATURE_FILE') as f:
    d = json.load(f)
for feat in d['features']:
    if not feat.get('passes'):
        print(f\"    [{feat.get('id','?')}] P{feat.get('priority','?')}: {feat.get('description','')}\")
" 2>/dev/null || echo "    (解析失败)"
else
  echo "  (任务文件不存在: $FEATURE_FILE)"
fi

echo ""
echo "[5/5] 依赖检查:"
if [ -d "$REPO_ROOT/node_modules" ]; then
  echo "  node_modules 已存在"
else
  echo "  node_modules 不存在，需要运行依赖安装命令"
fi
if [ -f "$REPO_ROOT/AGENTS.md" ]; then
  echo "  AGENTS.md 已存在（Harness 主执行契约）"
else
  echo "  ⚠️ AGENTS.md 不存在，建议先执行 by-harness 脚手架初始化"
fi
if [ -f "$WORKSPACE_DIR/TASK-HARNESS.md" ]; then
  echo "  TASK-HARNESS.md 已存在（任务层执行契约）"
else
  echo "  ⚠️ TASK-HARNESS.md 不存在，建议重新执行 by-harness 脚手架"
fi

echo ""
echo "=========================================="
echo "  初始化完成"
echo "=========================================="
echo ""
echo "下一步操作:"
echo "  1. 阅读 AGENTS.md（Harness 主闭环规则）"
echo "  2. 阅读 ${WORKSPACE_PREFIX}TASK-HARNESS.md（任务层规则）"
echo "  3. 阅读 ${WORKSPACE_PREFIX}task-harness/progress/*.md（${WORKSPACE_PREFIX}progress.txt 为最新快照）"
echo "  4. 阅读当前任务文件（见上方任务文件路径）找到下一个未完成 feature"
echo "  5. 按 plan/build/qa 流程执行，单元测试通过后即可改 passes（QA 非阻塞）"
echo "  6. 运行 python3 ${WORKSPACE_PREFIX}scripts/session_close.py --target-dir . --feature-id <feat-id>"
echo "  7. git commit / git push"
echo ""
