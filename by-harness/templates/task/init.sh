#!/bin/bash
# ==========================================
#  {{项目名称}} - Agent 环境初始化脚本
# ==========================================
# 用途：每个 Agent 会话开始时运行，快速恢复开发环境
# 用法：bash .harness/scripts/init.sh（legacy 项目可用 bash .harness/init.sh）

set -e

echo "=========================================="
echo "  {{项目名称}} - Agent 环境初始化"
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ "$(basename "$SCRIPT_DIR")" = "scripts" ] && [ -d "$SCRIPT_DIR/../task-harness" ]; then
  HARNESS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
elif [ -d "$SCRIPT_DIR/task-harness" ]; then
  HARNESS_DIR="$SCRIPT_DIR"
else
  HARNESS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

if [ -f "$HARNESS_DIR/../AGENTS.md" ]; then
  REPO_ROOT="$(cd "$HARNESS_DIR/.." && pwd)"
else
  REPO_ROOT="$HARNESS_DIR"
fi

WORKSPACE_NAME="$(basename "$HARNESS_DIR")"
if [ "$HARNESS_DIR" = "$REPO_ROOT" ]; then
  WORKSPACE_PREFIX=""
else
  WORKSPACE_PREFIX="$WORKSPACE_NAME/"
fi

resolve_file() {
  local rel
  for rel in "$@"; do
    if [ -f "$HARNESS_DIR/$rel" ]; then
      echo "$HARNESS_DIR/$rel"
      return 0
    fi
  done
  echo "$HARNESS_DIR/$1"
}

cd "$HARNESS_DIR"

echo ""
echo "[1/8] 当前目录:"
echo "  仓库根目录: $REPO_ROOT"
echo "  Harness 工作目录: $HARNESS_DIR"

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
PYTHONPATH="$HARNESS_DIR/scripts:${PYTHONPATH:-}" python3 - <<'PY' || echo "  (任务状态解析失败)"
from pathlib import Path

try:
    from task_store import load_task_entries
except Exception as exc:
    print(f"  task_store 加载失败: {exc}")
    raise SystemExit(0)

workspace = Path(".").resolve()
try:
    entries = load_task_entries(workspace)
except Exception as exc:
    print(f"  任务存储读取失败: {exc}")
    raise SystemExit(0)

features = [entry.feature for entry in entries]
total = len(features)
passed = sum(1 for feat in features if bool(feat.get("passes")))
pending = [feat for feat in features if not bool(feat.get("passes"))]
pending.sort(
    key=lambda feat: (
        int(feat.get("priority", 10**9)) if str(feat.get("priority", "")).isdigit() else 10**9,
        str(feat.get("created_at", "")),
        str(feat.get("id", "")),
    )
)
source_counts = {}
for entry in entries:
    source_counts[entry.source_kind] = source_counts.get(entry.source_kind, 0) + 1

print(f"  任务源: {', '.join(f'{k}={v}' for k, v in sorted(source_counts.items())) or 'none'}")
print(f"  总计: {total} 个功能")
print(f"  已完成: {passed} 个")
print(f"  剩余: {max(total - passed, 0)} 个")
print("")
print("  未完成的功能:")
if not pending:
    print("    (无)")
else:
    for feat in pending[:20]:
        print(f"    [{feat.get('id','?')}] P{feat.get('priority','?')}: {feat.get('description','')}")
    if len(pending) > 20:
        print(f"    ... 另有 {len(pending) - 20} 个未展示")
PY

echo ""
echo "[5/8] 运行时远程更新检查:"
UPDATE_SCRIPT=""
if [ -f "$HARNESS_DIR/scripts/update_runtime.py" ]; then
  UPDATE_SCRIPT="$HARNESS_DIR/scripts/update_runtime.py"
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
RUNTIME_VERSION_FILE="$(resolve_file "config/runtime-version.json" "runtime-version.json")"
TASK_FILE="$(resolve_file "config/task.json" "task.json")"
RUNTIME_VERSION="unknown"
if [ -f "$RUNTIME_VERSION_FILE" ]; then
  RV=$(RUNTIME_VERSION_FILE="$RUNTIME_VERSION_FILE" python3 - <<'PY'
import json
import os
from pathlib import Path
path = Path(os.environ["RUNTIME_VERSION_FILE"])
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
SESSION_CONTROL=$(TASK_FILE="$TASK_FILE" python3 - <<'PY'
import json
import os
from pathlib import Path

mode = "soft_reset"
path = Path(os.environ["TASK_FILE"])
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

rm -f \
  "$HARNESS_DIR/config/session-context.json" \
  "$HARNESS_DIR/session-context.json" \
  "$HARNESS_DIR/config/session-boundary.json" \
  "$HARNESS_DIR/session-boundary.json"
echo "  session-context/session-boundary 状态文件已禁用；如有旧文件已清理"

echo ""
echo "[7/8] 任务自动定位（当前分支）:"
BRANCH_SCRIPT=""
if [ -f "$HARNESS_DIR/scripts/ensure_task_branch.py" ]; then
  BRANCH_SCRIPT="$HARNESS_DIR/scripts/ensure_task_branch.py"
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
TASK_CONTRACT_FILE="$(resolve_file "docs/TASK-HARNESS.md" "TASK-HARNESS.md")"
if [ -f "$TASK_CONTRACT_FILE" ]; then
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
echo "  2. 阅读 ${WORKSPACE_PREFIX}docs/TASK-HARNESS.md（任务层规则）"
echo "  3. 阅读 ${WORKSPACE_PREFIX}task-harness/progress/YYYY-MM/*.md（latest.txt 仅作 legacy 兼容快照）"
echo "  4. 确认已自动定位当前任务（默认在当前分支开发）"
echo "  5. 若为 Java 项目，先阅读 ${WORKSPACE_PREFIX}docs/java-dev-conventions.md，并按触发维度读取 ${WORKSPACE_PREFIX}docs/java/rules/"
echo "  6. 按 plan/build/qa gate/agent review 流程执行，单元测试、required QA Gate 与 required Agent Review（如启用）通过后才可改 passes"
echo "  7. 明确、局部、可验证的自然语言改动默认先运行：python3 ${WORKSPACE_PREFIX}scripts/quick_fix_classifier.py --target-dir . --prompt '<改动描述>'"
echo "  8. Agent Review 手动收口：python3 ${WORKSPACE_PREFIX}scripts/agent_review.py --backend auto"
echo "  9. 如需手动更新运行时：python3 ${WORKSPACE_PREFIX}scripts/update_runtime.py --target-dir . --dry-run"
echo " 10. 标准任务收口：python3 ${WORKSPACE_PREFIX}scripts/session_close.py --target-dir . --feature-id <task-id> --outcome pass"
echo " 11. quick-fix 收口：python3 ${WORKSPACE_PREFIX}scripts/session_close.py --target-dir . --quick-fix --title '<bug 标题>' --outcome pass --note '<验证命令和结果>'"
echo " 12. fast-track 收口：python3 ${WORKSPACE_PREFIX}scripts/session_close.py --target-dir . --fast-track --title '<改动标题>' --outcome pass --note '<范围、风险判断、验证命令和结果>'"
echo " 13. 自动续跑下个任务：python3 ${WORKSPACE_PREFIX}scripts/task_switch.py continue --target-dir ."
echo " 14. git commit / git push"
echo ""
