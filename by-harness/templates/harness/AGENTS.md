# {{PROJECT_NAME}} Agent 指南

本项目采用 Harness Engineering 工作流。在 Codex 中，请将此文件视为 `Plan -> Build -> Verify` 的执行契约。

## 快速开始（Codex）

可使用以下任一意图：

1. `plan <功能描述>`
2. `build <spec 文件或最新 spec>`
3. `qa <contract 文件或最新 contract>`
4. `sprint <功能描述>`（完整周期）

## Codex 意图路由

当用户请求匹配下列意图时，执行对应流程。

| 意图 | 触发示例 | 必要动作 | 必要输出 |
|---|---|---|---|
| `plan` | “plan login flow”, “write spec for X” | 澄清歧义、检查相关代码、编写 spec | `docs/specs/<feature>.md` |
| `build` | “build latest spec”, “implement checkout spec” | 读取 spec+contract，按范围实现并自检 | 代码改动 + 冲刺报告 |
| `qa` | “qa latest contract”, “evaluate feature X” | 读取 contract，逐条测试并评分 | 结构化 QA 报告 + 分数 |
| `sprint` | “sprint build auth”, “full cycle for X” | 依次执行 plan+contract+build+qa+fix | spec + contract + 实现 + 分数 |

## 执行契约

### Plan 契约

- 不允许编写实现代码。
- Spec 必须包含：
  - 问题陈述（Problem statement）
  - 用户故事（User stories）
  - 可机器验证的验收标准
  - 组件边界（Component boundaries）
  - 数据流（Data flow）
  - 错误处理（Error handling）
  - 至少 3 个边界场景
  - 依赖项（Dependencies）
- 保存路径：`docs/specs/<feature-name>.md`

### Build 契约

- 从 `docs/specs/` 读取目标 spec。
- 从 `docs/contracts/` 读取目标 contract。
- 若 contract 缺失，先基于 `docs/contracts/TEMPLATE.md` 创建再实现。
- 只允许实现 contract 范围内内容。
- 交付前必须自检：
  - 构建/编译通过
  - 测试通过（既有 + 新增）
  - 验收标准逐条核对
  - 无调试残留

### QA 契约

- 评分只依据 contract 标准。
- 每条标准状态仅允许：`PASS` / `FAIL` / `PARTIAL`。
- 评分公式：
  - `score = (pass + 0.5 * partial) / total * 100`
- 阈值：`80`。
- 每个 FAIL 必须包含：
  - 预期行为
  - 实际行为
  - 复现步骤
  - 修复建议

### Sprint 契约

- 顺序必须严格遵守：
  1. Plan
  2. Contract
  3. Build
  4. QA
  5. Fix loop（必要时）
  6. 文档新鲜度检查
- Fix loop 最大迭代：`3`。
- 若 3 轮后仍未达阈值：
  - 停止
  - 汇总未解决失败项
  - 请求缩范围或人工介入

## 操作规则

- 先 spec 后代码。
- 先 contract 后 build。
- 一次只做一个 sprint。
- 禁止隐式扩范围。
- 问题必须显式暴露并附证据。
- 优先可回滚、低风险的朴素方案。

## 与 Task Harness 的集成（可选但推荐）

若项目存在 `feature_list.json` 与 `TASK-HARNESS.md`，按以下方式形成任务闭环：

1. 从 `feature_list.json` 选择优先级最高且 `passes=false` 的 feature
2. 严格执行 `plan -> contract -> build -> qa -> fix` 主流程
3. 仅当 `qa >= 80/100` 时，将该 feature 的 `passes` 置为 `true`
4. 在 `progress.txt` 记录本轮实现、验证结果与下一步
5. 若达到 3 轮仍失败，保持 `passes=false` 并记录阻塞原因

集成约束：
- `AGENTS.md` 负责主闭环，不负责改任务定义
- `TASK-HARNESS.md` 负责任务追踪，不得覆盖主闭环规则
- 禁止为了推进进度跳过 QA 或绕过阈值

## Codex Hook 运行时

- Codex hooks 定义在 `.codex/hooks.json`
- hook 脚本位于 `.codex/hooks/`
- 功能开关位于 `.codex/config.toml`
- 主要目标：
  - PreToolUse 循环检测
  - UserPromptSubmit 上下文注入
  - Stop 阶段完成前检查提醒

## 项目布局

- `AGENTS.md`：Codex 执行入口
- `CLAUDE.md`：Claude 执行入口
- `.codex/config.toml`：Codex hooks 开关
- `.codex/hooks.json`：Codex hooks 注册
- `.codex/hooks/`：Codex hook 脚本
- `.claude/agents/`：角色定义
- `.claude/commands/`：标准命令流程
- `.claude/hooks/`：循环/上下文/检查 hook
- `docs/specs/`：功能规格
- `docs/contracts/`：冲刺契约
- `docs/plans/`：计划产物
- `feature_list.json`：任务状态（可选）
- `TASK-HARNESS.md`：任务层执行契约（可选）

## 提示词示例（Codex）

- `plan 增加邮箱魔法链接免密登录`
- `build latest spec`
- `qa latest contract`
- `sprint 在 dashboard 中增加组织切换器`

## 技术栈

- 项目：`{{PROJECT_NAME}}`
- 类型：`{{PROJECT_TYPE}}`
- 技术栈：`{{TECH_STACK}}`
