# santong Skills 技能仓库

这里是 Skills 技能集合，每个子目录代表一个独立的技能。

## 目录结构

```
santong-skills/
├── by-harness/               # 独立融合版（初始化 + 持续拆任务）
├── harness-engineering/      # Harness Engineering 框架一键初始化
└── ...
```

## Skills 列表

### by-harness

独立融合版 Harness。

用于一键落地“拆分任务 -> 执行 -> 测试”的统一闭环，且不依赖其他 skill 目录，核心包含：
- 根目录极简：默认只放 `AGENTS.md`（以及隐藏运行目录 `.codex/.claude`）
- 工作文件集中到 `.harness/`：`CLAUDE.md`、`docs/`、`TASK-HARNESS.md`、`feature_list.json`、`task-harness/`、`progress.txt`、`init.sh`、`task.json`
- 初始化会话收口工具：`.harness/scripts/session_close.py`（维护会话日志 + 最新快照）
- 支持后续持续拆任务：把新任务增量写入 active bucket（自动同步 `.harness/feature_list.json` 兼容镜像）
- 每个任务含闭环工件字段：`spec_path` / `contract_path` / `qa_report_path`
- 工件语义：`spec_path=技术方案`，`contract_path=测试计划/验收标准`，`qa_report_path=测试结果`
- 当前门禁策略：单元测试通过即可 `passes=true`，QA 报告默认非阻塞
- 代码注释准则：所有新增/修改函数、方法必须补齐中文注释（用途、参数、返回值、副作用）

一体化初始化命令：

```bash
python3 by-harness/scripts/scaffold.py \
  --project-name "your-project" \
  --description "一句话描述项目目标" \
  --tech-stack "React + Node.js" \
  --project-type "web app" \
  --target-dir "."
```

初始化后建议先执行：

```bash
bash .harness/init.sh
```

持续拆任务命令：

```bash
python3 by-harness/scripts/decompose_tasks.py \
  --target-dir "." \
  --item "新增用户权限矩阵" \
  --item "增加组织级审计日志"
```

任务重平衡命令（需求持续增长时）：

```bash
python3 by-harness/scripts/rebalance_tasks.py --target-dir "."
```

会话收口命令：

```bash
python3 .harness/scripts/session_close.py \
  --target-dir "." \
  --feature-id "feat-03" \
  --outcome "in-progress" \
  --qa-score 72 \
  --note "已完成 plan/build，准备进入 fix"
```

手动提示词入口（在 Codex 手动选择 `by-harness` 后直接输入）：
- `初始化`
- `持续拆任务 主题：权限系统，拆 6 个`
- `执行 feat-03`


