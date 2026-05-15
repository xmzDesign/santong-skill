---
description: 根据简短描述创建功能规格说明
argument-hint: 功能描述（1-4 句话）
---

# 规划功能

根据以下需求创建功能规格：$ARGUMENTS

## 流程

1. 用以上描述调用 `planner` 智能体。
2. `planner` 会执行：
   - 若描述存在歧义，不反复向用户澄清；基于当前技术方案、代码和规范自动形成低风险假设。
   - 在写 spec 前列出假设、歧义、取舍和范围外事项；影响数据、接口、权限、兼容性或改动范围的歧义必须自动落入假设、风险和验证项。
   - 调研现有代码中的模式与约定。
   - 执行最小实体与成本评估：如无必要，勿增实体；历史项目小改动优先复用既有实体、表、DTO、Service、配置和扩展点。
   - 比较最小方案与替代方案；默认选择满足验收标准的最小方案，不规划未请求的抽象、配置或重构。
   - 识别规范源，并在 spec 中写入 Norm References：实际读取的 Java/项目局部规范、适用原因、未适用原因。
   - 若涉及 Java/Spring Boot/Dubbo/XXL-Job/MyBatis/Redis/金额/分页/配置/日志，先读取 `.harness/docs/java-dev-conventions.md` 入口，再按触发维度读取 `.harness/docs/java/rules/` 分片规则，并在 spec 中补充 Java 总门禁、魔法值治理、维度核心门禁、实现方式、验收方式、自动检查项。
   - Java spec 必须按需覆盖触发维度：通用工程、分层与 DDD、Dubbo 与公共 API、日志与异常、持久化与基础设施、测试安全运维；每个触发维度按入口文件中的 5 条核心门禁落地。
   - 所有 Java 改动都必须补充分布式 Java 门禁：声明未触发并说明理由，或列出 `.harness/docs/java/rules/distributed-java-gate.md` 触发条款、实现证据、验收方法和人工确认项。
   - 在 `.harness/docs/specs/<feature-name>.md` 生成结构化规格说明。
   - 通过 `TaskCreate` 创建带依赖关系的冲刺任务。
3. 输出规格路径、自动决策、关键假设和风险。
4. 用户可继续执行 `/build` 或 `/sprint`；不要在本命令中额外要求用户确认规格。

**不要开始实现。** 此命令只产出规划与规格，不应改动业务代码。

## 规格结构

规格应包含：
- 假设（Assumptions）：当前采用的前提、证据和风险
- 歧义与自动决策（Ambiguities & Decisions）：未明确事项、采用方案、证据、风险和验证方式
- 取舍（Tradeoffs）：最小方案、替代方案、选择理由、放弃理由
- 范围外（Non-goals）：本次不做的功能、重构、格式化、清理和兼容扩展
- 问题陈述（Problem statement）
- 规范引用（Norm References）
- 用户故事（User stories）
- 可机器验证的验收标准（Acceptance criteria）
- 组件边界（Component boundaries）
- 最小实体与成本评估：复用对象、新增必要性、替代方案、兼容性、迁移成本、回滚影响
- 数据流（Data flow）
- 错误处理（Error handling）
- 边界场景（至少 3 个）
- 依赖项（Dependencies）
- 若涉及 Java：Java 总门禁 5 条、魔法值治理、触发维度核心门禁、实现方式、验收方式、自动检查项
- 若涉及 Java：触发维度清单，包括通用工程、分层与 DDD、Dubbo 与公共 API、日志与异常、持久化与基础设施、测试安全运维
- 若涉及 Java：分布式 Java 门禁未触发理由，或分布式规则触发条款、实现证据、验收方式、人工确认项
