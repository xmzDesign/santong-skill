# santong Skills 技能仓库

这里是 Skills 技能集合，每个子目录代表一个独立技能。

## 目录结构

```text
santong-skills/
└── by-harness/   # 独立融合版（初始化 + 持续拆任务 + 会话控制 + 自动续跑）
```

## by-harness（独立融合版 Harness）

`by-harness` 用于一键落地 `plan -> build -> qa -> fix` 统一闭环，不依赖其他 skill 目录。

### 核心能力

- 根目录极简：默认只放 `AGENTS.md`（以及隐藏运行目录 `.codex/.claude`）
- 工作文件集中在 `.harness/`：`CLAUDE.md`、`docs/`、`TASK-HARNESS.md`、`task-harness/`、`progress.txt`、`init.sh`、`task.json`（`feature_list.json` 不再默认创建，仅 legacy 项目兼容）
- 自动任务定位：`.harness/scripts/ensure_task_branch.py`（按任务状态/提示词选出当前要做的 feature，不切分支）
- 会话收口：`.harness/scripts/session_close.py`（会话日志 + 快照 + 会话状态）
- 连续切任务：`.harness/scripts/task_switch.py`（当前分支自动续跑下个任务）
- 持续拆任务：新任务增量写入 active bucket（仅当 legacy 项目已存在 `.harness/feature_list.json` 时才同步兼容镜像）
- 每个任务闭环工件字段：`spec_path` / `contract_path` / `qa_report_path`
- 门禁策略：单元测试通过即可 `passes=true`，QA 默认非阻塞
- 注释准则：所有新增/修改函数、方法必须补齐中文注释（用途、参数、返回值、副作用）

### 一体化初始化

```bash
python3 by-harness/scripts/scaffold.py \
  --project-name "your-project" \
  --description "一句话描述项目目标" \
  --tech-stack "React + Node.js" \
  --project-type "web app" \
  --target-dir "."
```

初始化后先执行：

```bash
bash .harness/init.sh
```

### 常用命令

持续拆任务：

```bash
python3 by-harness/scripts/decompose_tasks.py \
  --target-dir "." \
  --item "新增用户权限矩阵" \
  --item "增加组织级审计日志"
```

任务重平衡：

```bash
python3 by-harness/scripts/rebalance_tasks.py --target-dir "."
```

会话收口：

```bash
python3 .harness/scripts/session_close.py \
  --target-dir "." \
  --feature-id "feat-03" \
  --outcome "in-progress" \
  --qa-score 72 \
  --note "已完成 plan/build，准备进入 fix"
```

自动续跑下个任务（当前分支）：

```bash
python3 .harness/scripts/task_switch.py continue --target-dir "."
```

### 会话控制配置（`.harness/task.json`）

```json
{
  "harness": {
    "session_control": {
      "mode": "soft_reset"
    }
  }
}
```

- `mode`
  - `soft_reset`：同一会话可继续，但自动提升 context epoch，要求忽略旧任务上下文
  - `hard_new_session`：任务收口后强制新会话

### 老仓库升级建议

- 可以再次执行 `scaffold.py`，默认不带 `--force` 时已有文件会 `SKIP`，不会直接覆盖任务数据
- 不要在已有项目直接全量 `--force`
- 升级重点是同步 `.harness/scripts/*.py`（尤其 `ensure_task_branch.py` 与 `task_switch.py`）和 `.harness/task.json` 的 `session_control` 配置
- 推荐直接使用升级脚本（自动备份 + 同步运行时 + 迁移配置）：

```bash
python3 by-harness/scripts/upgrade_legacy_repo.py --target-dir "<你的项目目录>"
```
