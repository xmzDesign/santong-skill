# {{项目名称}} - TASK-HARNESS 任务层执行规则

本文件是任务层契约，负责“任务拆分与进度追踪”。  
根目录 `AGENTS.md` 由 Harness Engineering 管理，负责 `Plan -> Build -> Verify` 主闭环。两者必须同时遵循。

## 会话启动（必须按顺序）

1. 运行 `bash init.sh`
2. 阅读根目录 `AGENTS.md`（主工作流约束）
3. 阅读 `TASK-HARNESS.md`（任务追踪约束）
4. 阅读 `progress.txt`
5. 阅读 `feature_list.json`
6. 选择优先级最高且 `passes=false` 的 1 个功能

## 闭环执行契约（严格遵循 Harness Engineering）

针对选中的单个 feature，执行：
1. `plan <feature description>`：生成 spec（禁止直接写实现）
2. Contract：在 `docs/contracts/` 明确验收标准与验证方式
3. `build <spec>`：按 contract 范围实现并自检
4. `qa <contract>`：逐条评估并评分
5. 若 `< 80`：进入修复循环（最多 3 轮）
6. 若 `>= 80`：才允许将该 feature 的 `passes` 设为 `true`

## 任务清单修改规则

- `feature_list.json` 中仅允许修改：
  - `passes: false -> true`（通过 QA 后）
- 禁止修改：
  - `id/category/priority/description/file/steps/verification`
- 如需改任务定义，必须先和用户确认，再由用户批准后调整

## 会话结束前必须完成

1. 写入 `progress.txt`（本轮实现、验证结果、失败项/修复项）
2. 若该 feature 通过阈值：更新 `passes=true`
3. 提交 git commit（建议一个 feature 一个 commit）
4. 输出下一步建议（下一个 feature 或阻塞处理方案）

## 遇到阻塞时

- 立即停止，不要切换到其他 feature
- 在 `progress.txt` 记录：
  - 阻塞现象
  - 已尝试方案
  - 失败原因
  - 建议下一步（缩范围 / 拆子任务 / 人工决策）

## Codex 提示词示例

- `先运行 init.sh，然后按 AGENTS.md + TASK-HARNESS.md 执行下一个 feature`
- `对 feat-03 执行 plan/build/qa 闭环，通过后再更新 passes`
- `按 harness 工作流修复 feat-05，直到 qa >= 80 或达到 3 轮上限`

## 项目信息

- 项目：`{{项目名称}}`
- 描述：`{{项目描述，一句话概括目标和范围}}`
