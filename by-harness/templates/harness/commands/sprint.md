---
description: 基于简短描述执行完整 Plan-Build-Verify 冲刺
argument-hint: 功能描述（1-4 句话）
---

# 全流程冲刺

针对以下需求执行完整 `Plan -> Build -> Verify` 周期：$ARGUMENTS

## 冲刺阶段

### 阶段 1：Plan（规划）

调用 `planner` 智能体，`planner` 会：
- 自动归纳歧义并形成低风险假设，不反复向用户提问
- 列出假设、歧义、取舍和范围外事项；影响数据、接口、权限、兼容性或改动范围的问题必须自动落入风险、验证项或范围外事项
- 调研代码库
- 比较最小方案与替代方案，默认选择能满足验收标准的最小方案
- 执行最小实体与成本评估：如无必要，勿增实体；历史项目小改动优先最小成本实施
- 识别 Java/项目局部规范源，并在 spec 中写入 Norm References
- 若涉及 Java，写入 Java 总门禁、触发维度核心门禁与分布式 Java 门禁；所有 Java 改动都必须声明分布式影响
- 在 `.harness/docs/specs/<feature-name>.md` 产出规格说明
- 创建冲刺任务

**门禁**：规格必须落盘且包含关键假设、自动决策和风险；当前命令是 sprint 时自动进入下一阶段，不额外等待用户批准。

### 阶段 2：契约协商（Contract Negotiation）

在 `.harness/docs/contracts/<feature-name>.md` 生成冲刺契约：
- 从规格中提取验收标准
- 明确范围（In Scope / Out of Scope）
- 固化假设、歧义、取舍和范围外事项
- 将“如无必要，勿增实体”和最小成本方案转成可验收清单
- 建立简单性门禁，约束新增抽象、配置、实体、表、DTO、Service 和框架胶水
- 建立变更追溯矩阵，要求每个预计改动文件映射到范围、验收标准或失败修复项
- 为每条标准指定验证方法
- 若涉及 Java，将 Java 总门禁、触发维度核心门禁与分布式 Java 门禁转成可验收清单
- 设置执行门禁：单元测试、convention-check 和 required QA Gate 必须通过
- 设置最大迭代：`3`

输出契约路径、自动决策和验证方式。

**门禁**：契约必须落盘且验收标准可验证；当前命令是 sprint 时自动继续，不额外等待用户批准。

### 阶段 3：Build（实现）

调用 `generator` 智能体：
- 读取 spec + contract
- 复核假设、歧义、取舍、范围外事项、简单性门禁和变更追溯矩阵
- 完成一个冲刺范围内的实现
- 自检（复读代码、检查构建、逐条对照标准、核对变更追溯矩阵、检查简单性门禁）

### 阶段 4：Verify（验证）

调用 `evaluator` 智能体：
- 读取契约
- 按契约执行单元、构建和必要的集成验证
- 检查行为门禁、简单性门禁、变更追溯矩阵和范围外事项
- 对每条验收标准评分
- 计算总分

### 阶段 5：Fix Loop（修复循环）

若单元测试不通过（最多 3 轮）：
1. 将 evaluator 的失败报告回传给 generator
2. generator 分析根因并完成修复
3. generator 对修复结果执行自检
4. 返回阶段 4 重新验证

若 3 轮后仍失败：
- 保持当前 feature 的 `passes=false`。
- 向用户汇总所有累计失败项并记录在进度日志。
- 建议：缩小范围、拆分更小冲刺、人工介入。
- 继续执行下一个 feature，避免阻塞整体推进。

### 阶段 6：Complete（完成）

若单元测试、convention-check 与 required QA Gate 通过：
1. 在 contract 的 Sprint Log 里写入最终结果
2. 确认该 feature 的 `spec_path` 与 `contract_path` 文件真实存在；缺任一文件时回到 Plan/Contract 阶段补齐
3. 确认 `.harness/docs/qa/<feature>.result.json` 中 `gate_status=PASS`
4. 若存在 `.harness/task-harness/index.json`，将对应单任务 JSON 中该 feature 的 `passes` 更新为 `true`
5. 调用 `.harness/scripts/session_close.py` 写入独立进度分片
6. 调用 doc-gardener 智能体执行新鲜度审计
7. 产出冲刺总结：
   - 已构建功能
   - 最终评估分数
   - 使用迭代次数
   - 剩余问题或技术债
   - 下一次冲刺建议时机
