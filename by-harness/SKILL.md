---
name: by-harness
description: 独立的一体化 Harness skill（不依赖其他 skill 文件）。可初始化主闭环脚手架，并持续执行任务拆解。适用于“拆分任务-执行-测试”闭环场景，生成 AGENTS.md/CLAUDE.md、hooks、spec/contract/qa 文档、feature_list.json、TASK-HARNESS.md、progress.txt、init.sh、task.json、scripts/session_close.py。
argument-hint: "[项目名称] [项目描述]"
disable-model-invocation: false
user-invocable: true
---

# by-harness

`by-harness` 是一个**独立 skill**，内部自带模板和脚本。

它提供两种能力：
- **初始化主闭环**：生成 Harness Engineering 工作流（`AGENTS.md`、`CLAUDE.md`、hooks、docs）
- **持续任务拆解**：持续向 `feature_list.json` 增量追加任务，且任务默认符合 Harness 闭环要求（plan/build/qa/fix）

目标闭环：
`拆分任务 -> plan -> build -> qa -> (fix) -> qa达标后更新passes`

## 快捷意图（手动选 skill 后可直接输入）

### 1) `初始化`

当用户输入类似：
- `初始化`
- `初始化 项目名：xxx 主题：yyy`

执行动作：
1. 收集参数（项目名、描述、技术栈、类型、target-dir）
2. 运行 `scripts/scaffold.py`
3. 运行 `bash init.sh`
4. 回报已生成文件与首个推荐任务

### 2) `持续拆任务 主题：...`

当用户输入类似：
- `持续拆任务 主题：权限系统`
- `持续拆任务 主题：订单重构，拆 6 个`

执行动作：
1. 先基于主题自动拆出若干可执行子任务（默认 4-8 个，用户指定数量优先）
2. 调用 `scripts/decompose_tasks.py --item ...` 追加到 `feature_list.json`
3. 回报新增任务 ID、优先级与建议执行顺序

### 3) `执行 feat-03`

当用户输入类似：
- `执行 feat-03`
- `按 by-harness 执行 feat-03`

执行动作（严格闭环）：
1. 读取 `feature_list.json` 定位任务
2. 执行 `plan -> build -> qa -> (fix)`，最多 3 轮修复
3. 仅在 `qa >= 80/100` 后将 `passes=true`
4. 追加 `progress.txt`，回报结果与下一任务

若 `qa < 80` 且达到上限：保持 `passes=false`，输出阻塞原因与建议。

## 使用流程

### Step 1: 初始化项目闭环（首次）

```bash
python3 {{SKILL_PATH}}/scripts/scaffold.py \
  --project-name "<项目名称>" \
  --description "<项目描述>" \
  --tech-stack "<技术栈，可选>" \
  --project-type "<项目类型，可选>" \
  --design-guidance "<设计约束，可选>" \
  --target-dir "<项目目录>"
```

初始化后会生成：
- 主契约：`AGENTS.md`、`CLAUDE.md`
- 双 hook 运行时：`.claude/` + `.codex/`
- 文档结构：`docs/specs/`、`docs/contracts/`、`docs/plans/`
- 任务层：`TASK-HARNESS.md`、`feature_list.json`、`progress.txt`、`init.sh`、`task.json`

### Step 2: 持续任务拆解（可重复执行）

```bash
python3 {{SKILL_PATH}}/scripts/decompose_tasks.py \
  --target-dir "<项目目录>" \
  --item "<任务描述1>" \
  --item "<任务描述2>" \
  --category "feature"
```

该命令会把新任务追加到 `feature_list.json`，并自动生成符合 Harness 思想的默认步骤：
1. 先 plan（产出 spec）
2. 再 contract（定义验收标准）
3. build 实现并自检
4. qa 评分（阈值 80）
5. 未达标进入修复循环（最多 3 轮）
6. 达标后才允许 `passes=true`

同时每个任务都会具备闭环工件字段：
- `spec_path`
- `contract_path`
- `qa_report_path`

### Step 3: 每个会话执行规范

每次会话建议顺序：
1. `bash init.sh`
2. 阅读 `AGENTS.md`（主闭环）
3. 阅读 `TASK-HARNESS.md`（任务层）
4. 选择一个 `passes=false` 的任务执行 plan/build/qa
5. `qa >= 80` 后执行 mark_pass（更新 `passes=true`）
6. 会话结束执行 `python3 scripts/session_close.py --target-dir . --feature-id <feat-id>`

## 运行约束

- `AGENTS.md` 是主契约，负责 Plan/Build/Verify/Fix。
- `TASK-HARNESS.md` 是任务层契约，负责 feature 追踪与进度记录。
- 仅在 `qa >= 80/100` 后允许 `passes=false -> true`。
- 禁止 task 层规则覆盖主闭环规则。
- `feature_list.json` 只允许修改 `passes`（常规执行时），不要随意改已有任务定义。

## 典型提示词

- `用 by-harness 初始化这个仓库，项目名 xxx，目标是 xxx`
- `继续拆解 3 个新任务，并写入 feature_list.json`
- `按 by-harness 规则执行下一个任务，qa 不达标不要改 passes`
