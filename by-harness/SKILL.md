---
name: by-harness
description: 独立的一体化 Harness skill（不依赖其他 skill 文件）。可初始化主闭环脚手架，并持续拆解与执行任务，默认采用分片任务存储（index + buckets）并保留 feature_list 兼容镜像。
argument-hint: "[项目名称] [项目描述]"
disable-model-invocation: false
user-invocable: true
---

# by-harness

`by-harness` 是一个**独立 skill**，内部自带模板和脚本，不依赖其他 skill 目录。

目标是让你在 Codex 里稳定执行这个闭环：
`拆分任务 -> read task -> plan -> build -> qa -> fix -> mark_pass -> session_close`

## 手动意图（你期望的三种入口）

### 1) `初始化`

示例：
- `初始化`
- `初始化 项目名：xxx 主题：yyy`

执行动作：
1. 收集参数（项目名、描述、技术栈、类型、target-dir）
2. 执行 `scripts/scaffold.py`
3. 执行 `bash .harness/init.sh`
4. 回报首个推荐任务

### 2) `持续拆任务 主题：...`

示例：
- `持续拆任务 主题：权限系统`
- `持续拆任务 主题：订单重构，拆 6 个`

执行动作：
1. 按主题自动拆出 4-8 个可执行任务（用户指定数量优先）
2. 执行 `scripts/decompose_tasks.py --item ...`
3. 默认写入 active bucket（可 `--bucket` 指定）
4. 回报新增任务 ID、优先级、执行顺序建议

### 3) `执行 feat-03`

示例：
- `执行 feat-03`
- `按 by-harness 执行 feat-03`

执行动作（严格闭环）：
1. `read task`：定位 feature 并读取 `description/steps/spec_path/contract_path/qa_report_path`
2. `plan -> build -> qa（非阻塞）`
3. 若单元测试失败，进入 `fix`（最多 3 轮）
4. `mark_pass`：单元测试通过时 `passes=false -> true`
5. 执行 `.harness/scripts/session_close.py` 追加会话日志并刷新最新快照

若单元测试 3 轮仍失败：保持 `passes=false`，记录原因并继续下一个任务。

## 存储模型（分片优先）

- 根目录：`AGENTS.md`（主契约） + 隐藏运行目录（`.codex/.claude`）
- 工作目录：`.harness/`（其余文件统一收纳）
- 索引文件：`.harness/task-harness/index.json`
- 任务分片：`.harness/task-harness/features/*.json`
- 进度分片：`.harness/task-harness/progress/YYYY-MM.md`
- 兼容镜像：`.harness/feature_list.json`（同步 active bucket 视图）
- 最新快照：`.harness/progress.txt`（由会话收口脚本刷新）

## 初始化（首次）

```bash
python3 {{SKILL_PATH}}/scripts/scaffold.py \
  --project-name "<项目名称>" \
  --description "<项目描述>" \
  --tech-stack "<技术栈，可选>" \
  --project-type "<项目类型，可选>" \
  --design-guidance "<设计约束，可选>" \
  --target-dir "<项目目录>"
```

初始化后生成：
- 根目录最小集：`AGENTS.md` + `.codex/` + `.claude/`
- `.harness/`：`CLAUDE.md`、`docs/`、`TASK-HARNESS.md`、`task-harness/`、`feature_list.json`、`progress.txt`、`init.sh`、`task.json`
- 收口工具：`.harness/scripts/session_close.py`

## 持续拆任务（可重复执行）

```bash
python3 {{SKILL_PATH}}/scripts/decompose_tasks.py \
  --target-dir "<项目目录>" \
  --item "<任务描述1>" \
  --item "<任务描述2>" \
  --category "feature"
```

默认行为：
- 自动补齐闭环工件字段：`spec_path` / `contract_path` / `qa_report_path`
- 自动生成闭环步骤：`read task -> plan -> build -> qa(non-blocking) -> fix -> mark_pass`
- 在分片模式下自动同步 `.harness/feature_list.json` 兼容镜像

## 会话收口（每次会话末尾）

```bash
python3 .harness/scripts/session_close.py \
  --target-dir . \
  --feature-id feat-03 \
  --outcome in-progress \
  --qa-score 72 \
  --note "已完成 plan/build，下一轮优先 fix"
```

该脚本会自动完成三件事：
1. 追加进度日志（分片或 legacy）
2. 刷新 `.harness/progress.txt` 最新快照
3. 输出下一任务建议

## 任务重平衡（任务越来越多时）

```bash
python3 {{SKILL_PATH}}/scripts/rebalance_tasks.py --target-dir "<项目目录>"
```

用途：
- 把大文件按 category 自动分桶到 `.harness/task-harness/features/*.json`
- 生成/更新 `.harness/task-harness/index.json`
- 保留 `.harness/feature_list.json` 兼容视图

## 运行约束

- `AGENTS.md` 是主契约，定义 Plan/Build/Verify/Fix。
- `.harness/TASK-HARNESS.md` 是任务层契约，不得覆盖主契约。
- 单元测试通过即可 `passes=false -> true`；QA 默认非阻塞。
- 常规执行只改 `passes`，不改任务结构字段。

## 典型提示词

- `用 by-harness 初始化这个仓库，项目名 xxx，目标是 xxx`
- `持续拆任务 主题：支付链路稳定性，拆 5 个`
- `执行 feat-03，严格按 read task -> plan -> build -> qa(non-blocking) -> fix -> mark_pass`
