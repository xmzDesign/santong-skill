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
echo "[1/8] 当前目录:"
echo "  仓库根目录: $REPO_ROOT"
echo "  Harness 工作目录: $WORKSPACE_DIR"

echo ""
echo "[2/8] Git 状态:"
if git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$REPO_ROOT" status --short || echo "  (无 git 变更)"
else
  echo "  (当前目录不是 git 仓库)"
fi

echo ""
echo "[3/8] 最近 10 条 commit:"
if git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$REPO_ROOT" log --oneline -10 || echo "  (无 commit 历史)"
else
  echo "  (当前目录不是 git 仓库)"
fi

echo ""
echo "[4/8] 功能完成进度:"
FEATURE_FILE="task-harness/features/backlog-core.json"
ACTIVE_BUCKET="backlog-core"
if [ ! -f "task-harness/index.json" ] && [ -f "feature_list.json" ]; then
  FEATURE_FILE="feature_list.json"
  ACTIVE_BUCKET="legacy"
fi
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
print(path or "task-harness/features/backlog-core.json")
print(active or "backlog-core")
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
echo "[5/8] 运行时远程更新检查:"
UPDATE_SCRIPT=""
if [ -f "$WORKSPACE_DIR/scripts/update_runtime.py" ]; then
  UPDATE_SCRIPT="$WORKSPACE_DIR/scripts/update_runtime.py"
elif [ -f "$REPO_ROOT/scripts/update_runtime.py" ]; then
  UPDATE_SCRIPT="$REPO_ROOT/scripts/update_runtime.py"
fi
if [ -n "$UPDATE_SCRIPT" ]; then
  python3 "$UPDATE_SCRIPT" --target-dir "$REPO_ROOT" --check-remote || echo "  (远程更新检查失败，可手动重试)"
else
  echo "  (未找到 update_runtime.py，跳过远程更新检查)"
fi

echo ""
echo "[6/8] 会话模式与上下文重置:"
RUNTIME_VERSION="unknown"
if [ -f "runtime-version.json" ]; then
  RV=$(python3 - <<'PY'
import json
from pathlib import Path
path = Path("runtime-version.json")
try:
    data = json.loads(path.read_text(encoding="utf-8"))
except Exception:
    print("unknown")
else:
    print(str(data.get("runtime_version", "unknown")))
PY
)
  RUNTIME_VERSION=$(printf "%s\n" "$RV" | sed -n '1p')
fi
echo "  runtime_version: $RUNTIME_VERSION"
SESSION_CONTROL=$(python3 - <<'PY'
import json
from pathlib import Path

mode = "soft_reset"
path = Path("task.json")
if path.exists():
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        harness = data.get("harness", {}) if isinstance(data, dict) else {}
        if isinstance(harness, dict):
            sc = harness.get("session_control", {})
            if isinstance(sc, dict):
                if sc.get("mode"):
                    mode = str(sc.get("mode"))
            elif harness.get("session_mode"):
                mode = str(harness.get("session_mode"))
    except Exception:
        pass
print(mode)
PY
)
SESSION_MODE=$(printf "%s\n" "$SESSION_CONTROL" | sed -n '1p')
case "$SESSION_MODE" in
  hard|new_session|hard_new_session)
    SESSION_MODE="hard_new_session"
    ;;
  *)
    SESSION_MODE="soft_reset"
    ;;
esac
echo "  session_mode: $SESSION_MODE"

if [ "$SESSION_MODE" = "hard_new_session" ]; then
  BOUNDARY_FILE="$WORKSPACE_DIR/session-boundary.json"
  if [ -f "$BOUNDARY_FILE" ]; then
    BOUNDARY_FILE="$BOUNDARY_FILE" python3 - <<'PY'
import json
import os
from pathlib import Path

path = Path(os.environ["BOUNDARY_FILE"])
try:
    data = json.loads(path.read_text(encoding="utf-8"))
except Exception:
    print("  检测到 session-boundary.json，但解析失败")
else:
    closed_id = data.get("closed_feature_id", "n/a")
    next_id = data.get("next_feature_id", "n/a")
    print(f"  上一 feature 已收口: {closed_id}")
    print(f"  下一任务建议: {next_id}")
    print("  当前 init 视为新会话启动，将消费边界标记")
PY
    rm -f "$BOUNDARY_FILE"
  else
    echo "  无会话边界标记"
  fi
else
  CONTEXT_FILE="$WORKSPACE_DIR/session-context.json"
  if [ -f "$CONTEXT_FILE" ]; then
    CONTEXT_FILE="$CONTEXT_FILE" python3 - <<'PY'
import json
import os
from pathlib import Path

path = Path(os.environ["CONTEXT_FILE"])
try:
    data = json.loads(path.read_text(encoding="utf-8"))
except Exception:
    print("  检测到 session-context.json，但解析失败")
else:
    epoch = data.get("epoch", "n/a")
    reset_required = bool(data.get("reset_required"))
    closed_id = data.get("closed_feature_id", "n/a")
    print(f"  当前 context epoch: {epoch}")
    print(f"  最近收口 feature: {closed_id}")
    if reset_required:
        data["reset_required"] = False
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("  已消费 soft_reset 标记：后续按新任务上下文执行")
    else:
        print("  soft_reset 标记已消费，无需额外处理")
PY
  else
    echo "  未发现 session-context.json（首次会话或旧版本项目）"
  fi
fi

echo ""
echo "[7/8] 任务自动定位（当前分支）:"
BRANCH_SCRIPT=""
if [ -f "$WORKSPACE_DIR/scripts/ensure_task_branch.py" ]; then
  BRANCH_SCRIPT="$WORKSPACE_DIR/scripts/ensure_task_branch.py"
elif [ -f "$REPO_ROOT/scripts/ensure_task_branch.py" ]; then
  BRANCH_SCRIPT="$REPO_ROOT/scripts/ensure_task_branch.py"
fi
if [ -n "$BRANCH_SCRIPT" ]; then
  python3 "$BRANCH_SCRIPT" --target-dir "$REPO_ROOT" --sync-state || echo "  (任务定位失败，可稍后手动执行)"
else
  echo "  (未找到 ensure_task_branch.py，跳过自动定位)"
fi

echo ""
echo "[8/8] 依赖检查:"
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
echo "  4. 确认已自动定位当前任务（默认在当前分支开发）"
echo "  5. 若为 Java 项目，先阅读 ${WORKSPACE_PREFIX}docs/java-dev-conventions.md"
echo "  6. 按 plan/build/qa 流程执行，单元测试通过后即可改 passes（QA 非阻塞）"
echo "  7. 如需手动更新运行时：python3 ${WORKSPACE_PREFIX}scripts/update_runtime.py --target-dir . --dry-run"
echo "  8. 运行 python3 ${WORKSPACE_PREFIX}scripts/session_close.py --target-dir . --feature-id <feat-id>"
echo "  9. 自动续跑下个任务：python3 ${WORKSPACE_PREFIX}scripts/task_switch.py continue --target-dir ."
echo " 10. git commit / git push"
echo ""
