---
name: by-harness
description: Harness skill。可初始化主闭环脚手架，并持续拆解与执行任务，默认采用分片任务存储（index + buckets）；同时下发前端三层编码与视觉规范，用于约束 AI 在 React/Vue/TypeScript/UI/样式任务中的实现质量；feature_list 仅在 legacy 项目存在时兼容沿用。
argument-hint: "[项目名称] [项目描述]"
disable-model-invocation: false
user-invocable: true
---

# by-harness

`by-harness` 是一个**独立 skill**，内部自带模板和脚本。

目标是让你在 Codex 里稳定执行这个闭环：
`拆分任务 -> read task -> plan -> build -> qa -> fix -> mark_pass -> session_close`

同时，`by-harness` 会向目标仓库下发前端三层规范：

- 约束层：`.harness/docs/frontend/rules.md`
- 示范层：`.harness/docs/frontend/code-design.md`
- 视觉层：`.harness/docs/frontend/ui-design.md`
- 视觉参考：`.harness/docs/frontend/references/byai-ds-v/index.html`

当任务涉及 React/Vue/Next.js、TypeScript 组件、UI、样式、表格、表单、图表、Agent 界面或交互状态时，模型必须先读取 `.harness/docs/frontend-dev-conventions.md`，再按任务类型读取三层规范；新增页面、重构页面或明显视觉变更时，还必须打开 BYAI HTML 参考页。

## 手动意图（你期望的三种入口）

### 1) `初始化`

示例：
- `初始化`
- `初始化 项目名：xxx 主题：yyy`

执行动作：
1. 收集参数（项目名、描述、技术栈、类型、target-dir）
2. 执行 `scripts/scaffold.py`
3. 执行 `bash .harness/scripts/init.sh`
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
- 兼容镜像：`.harness/feature_list.json`（仅 legacy 项目存在时沿用，并同步 active bucket 视图）
- 运行时版本：`.harness/config/runtime-version.json`（用于版本化升级）
- 远程更新策略：`.harness/config/update-policy.json`（定时检查与自动升级策略）
- 最新快照：`.harness/task-harness/progress/latest.txt`（由会话收口脚本刷新）

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
- 根目录最小集：`AGENTS.md`、`CLAUDE.md` + `.codex/` + `.claude/`
- `.harness/`：`config/`、`docs/`、`scripts/`、`task-harness/`
- 规范文档：`.harness/docs/java-dev-conventions.md`（后端）与 `.harness/docs/frontend-dev-conventions.md`（前端）
- 前端三层规范：`.harness/docs/frontend/README.md`、`rules.md`、`code-design.md`、`ui-design.md`
- BYAI HTML 参考：`.harness/docs/frontend/references/byai-ds-v/`，包含 gallery、12 个页面设计稿、组件 showcase、tokens 与设计说明快照
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
- 在分片模式下，若存在 `.harness/feature_list.json` 则自动同步兼容镜像

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
2. 刷新 `.harness/task-harness/progress/latest.txt` 最新快照
3. 输出下一任务建议

## 任务重平衡（任务越来越多时）

```bash
python3 {{SKILL_PATH}}/scripts/rebalance_tasks.py --target-dir "<项目目录>"
```

用途：
- 把大文件按 category 自动分桶到 `.harness/task-harness/features/*.json`
- 生成/更新 `.harness/task-harness/index.json`
- 若存在 `.harness/feature_list.json`，则保持其兼容视图同步

## 老仓库一键升级（推荐）

```bash
python3 {{SKILL_PATH}}/scripts/update_runtime.py --target-dir "<项目目录>"
```

默认行为：
- 升级前自动备份 `.harness/config/task.json` 与 `.harness/scripts/*.py`
- 若 `manifest_url` 已配置：从远程 manifest 拉取并同步运行时脚本
- 若 `manifest_url` 未配置：执行本地兼容迁移（不依赖远程）
- 读取 `.harness/config/runtime-version.json` 并按版本差异执行迁移链（缺失时自动推断旧版本）
- 当本地版本高于内置或远程版本时，只告警并保持当前版本，不做降级覆盖
- 自动迁移 `task.json` 的 `session_control` 到当前简化模式（仅保留 `mode` 相关配置）
- 默认按“当前分支自动续跑”执行任务，不再依赖自动切分支配置

远程检查（定时 + 自动应用）：

```bash
python3 .harness/scripts/update_runtime.py --target-dir . --check-remote
```

说明：
- 默认 `update-policy.json` 为 `enabled=false`，需先配置 `manifest_url` 并开启后才会自动检查。

## 运行约束

- `AGENTS.md` 是主契约，定义 Plan/Build/Verify/Fix。
- `.harness/docs/TASK-HARNESS.md` 是任务层契约，不得覆盖主契约。
- 单元测试通过即可 `passes=false -> true`；QA 默认非阻塞。
- 所有新增/修改函数、方法必须补齐中文注释（用途、参数、返回值、副作用）。
- 常规执行只改 `passes`，不改任务结构字段。
- 前端/UI/样式任务必须遵守 `.harness/docs/frontend-dev-conventions.md` 和 `.harness/docs/frontend/` 三层规范；新增页面、重构页面或明显视觉变更时必须参考 `.harness/docs/frontend/references/byai-ds-v/`；完成前需自检 token、状态覆盖、响应式、可访问性和反例规避。

## 典型提示词

- `用 by-harness 初始化这个仓库，项目名 xxx，目标是 xxx`
- `持续拆任务 主题：支付链路稳定性，拆 5 个`
- `执行 feat-03，严格按 read task -> plan -> build -> qa(non-blocking) -> fix -> mark_pass`
