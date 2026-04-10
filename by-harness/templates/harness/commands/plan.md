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
