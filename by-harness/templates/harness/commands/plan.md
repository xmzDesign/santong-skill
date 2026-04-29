---
description: 根据简短描述创建功能规格说明
argument-hint: 功能描述（1-4 句话）
---

# 规划功能

根据以下需求创建功能规格：$ARGUMENTS

## 流程

1. 用以上描述调用 `planner` 智能体。
2. `planner` 会执行：
   - 若描述存在歧义，先向用户澄清问题。
   - 调研现有代码中的模式与约定。
   - 若涉及 Java/Spring Boot/Dubbo/XXL-Job/MyBatis/Redis/金额/分页/配置/日志，先读取 `.harness/docs/java-dev-conventions.md`，并在 spec 中补充 Java Gate：触发规则、实现方式、验收方式、自动检查项。
   - 若涉及前端/UI/样式，先读取 `.harness/docs/frontend-dev-conventions.md`；新增页面或明显视觉变更时继续读取 `.harness/docs/frontend/` 三层规范，并打开 `.harness/docs/frontend/references/byai-ds-v/` 中的对应 HTML 参考页。
   - 在 `.harness/docs/specs/<feature-name>.md` 生成结构化规格说明。
   - 通过 `TaskCreate` 创建带依赖关系的冲刺任务。
3. 将规格提交给用户评审。
4. 评审通过后，用户可继续执行 `/build` 或 `/sprint`。

**不要开始实现。** 此命令只产出规划与规格，不应改动业务代码。

## 规格结构

规格应包含：
- 问题陈述（Problem statement）
- 用户故事（User stories）
- 可机器验证的验收标准（Acceptance criteria）
- 组件边界（Component boundaries）
- 数据流（Data flow）
- 错误处理（Error handling）
- 边界场景（至少 3 个）
- 依赖项（Dependencies）
- 若涉及 Java：Java Gate 触发项、实现方式、验收方式、自动检查项
- 若涉及前端：页面类型、三层规范适用项、状态/视觉/响应式验收标准
