# {{项目名称}} - TASK-HARNESS 任务层执行规则

本文件是任务层契约，负责“任务拆分与进度追踪”。  
根目录 `AGENTS.md` 由 Harness Engineering 管理，负责 `Plan -> Build -> Verify` 主闭环。两者必须同时遵循。

## 会话启动（必须按顺序）

1. 运行 `bash init.sh`
2. 阅读根目录 `AGENTS.md`（主工作流约束）
3. 阅读 `TASK-HARNESS.md`（任务追踪约束）
4. 阅读 `task-harness/index.json`（定位 active bucket）
5. 阅读对应任务文件（如 `task-harness/features/backlog-core.json`，兼容入口为 `feature_list.json`）
6. 阅读 `task-harness/progress/*.md`（兼容入口为 `progress.txt`）
7. 选择优先级最高且 `passes=false` 的 1 个功能

## 闭环执行契约（严格遵循 Harness Engineering）

针对选中的单个 feature，必须按以下严格顺序执行（不得跳步）：
1. **读取任务（read task）**：从 active bucket 文件（兼容入口 `feature_list.json`）读取该 feature 的 `description/steps/spec_path/contract_path/qa_report_path`
2. **plan**：生成/更新 `spec_path` 对应规格文件（禁止直接写实现）
3. **build**：基于 spec + contract 实现并自检
4. **qa**：生成 `qa_report_path`，按 contract 逐条评分
5. **fix**：若 `qa < 80`，进入修复循环（最多 3 轮）
6. **mark_pass**：仅在 `qa >= 80` 后，才允许将该 feature `passes=false -> true`

## 任务清单修改规则

- active bucket 对应任务文件（例如 `task-harness/features/backlog-core.json`）中仅允许修改：
  - `passes: false -> true`（通过 QA 后）
- `feature_list.json` 为兼容镜像，常规不直接手改（由脚本同步）
- 禁止修改：
  - `id/category/priority/description/file/spec_path/contract_path/qa_report_path/steps/verification`
- 如需改任务定义，必须先和用户确认，再由用户批准后调整

## 会话结束前必须完成

1. 写入进度日志（`task-harness/progress/YYYY-MM.md`，兼容入口 `progress.txt`）
2. 若该 feature 通过阈值：更新 `passes=true`
3. 运行会话收口脚本：`python3 scripts/session_close.py --target-dir . --feature-id <feat-id>`
4. 提交 git commit（建议一个 feature 一个 commit）
5. 输出下一步建议（下一个 feature 或阻塞处理方案）

## 遇到阻塞时

- 立即停止，不要切换到其他 feature
- 在 `task-harness/progress/YYYY-MM.md`（兼容入口 `progress.txt`）记录：
  - 阻塞现象
  - 已尝试方案
  - 失败原因
  - 建议下一步（缩范围 / 拆子任务 / 人工决策）

## Codex 提示词示例

- `先运行 init.sh，然后按 AGENTS.md + TASK-HARNESS.md 执行下一个 feature`
- `执行 feat-03：严格按 read task -> plan -> build -> qa -> fix -> mark_pass`
- `按 harness 工作流修复 feat-05，直到 qa >= 80 或达到 3 轮上限`

## 项目信息

- 项目：`{{项目名称}}`
- 描述：`{{项目描述，一句话概括目标和范围}}`
