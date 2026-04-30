---
description: 按冲刺工作流实现最近的规格说明
argument-hint: 可选 - 指定 .harness/docs/specs/ 中要实现的 spec 文件
---

# 构建功能

使用 Generator-Evaluator 循环实现功能。

**目标**：$ARGUMENTS（为空时默认使用 `.harness/docs/specs/` 中最近修改的规格）

## 流程

### 1. 读取规格

从 `.harness/docs/specs/` 读取目标规格。若未传参数，自动选择最近修改的 spec 文件。
若本次任务涉及 Java/Spring Boot/Dubbo/XXL-Job/MyBatis/Redis/金额/分页/配置/日志，先读取 `.harness/docs/java-dev-conventions.md` 入口，再按触发维度读取 `.harness/docs/java/rules/` 分片规则，实现前列出 Java 总门禁和触发维度核心门禁，并确认 contract 中已有对应验收项。
若本次任务涉及 Java，实现前必须列出触发维度清单：通用工程、分层与 DDD、Dubbo 与公共 API、日志与异常、持久化与基础设施、测试安全运维；每个触发维度按入口文件中的 5 条核心门禁执行。
所有 Java 改动都必须确认 spec/contract 中已有分布式 Java 门禁；若缺失，先补齐 contract 或回到 plan。实现前声明未触发理由，或列出 `.harness/docs/java/rules/distributed-java-gate.md` 触发条款：外部调用边界、资源隔离、一致性恢复、失败可追踪可降级、发布停机不丢数据。
若本次任务涉及前端/UI/样式，先读取 `.harness/docs/frontend-dev-conventions.md`；新增页面、组件重构或明显视觉变更时继续读取 `.harness/docs/frontend/rules.md`、`.harness/docs/frontend/code-design.md`、`.harness/docs/frontend/ui-design.md`，并打开 `.harness/docs/frontend/references/byai-ds-v/` 中的对应 HTML 参考页。

### 2. 冲刺契约（Sprint Contract）

检查该功能在 `.harness/docs/contracts/` 下是否已有契约：
- 若已存在：读取并继续构建。
- 若不存在：从 Generator 与 Evaluator 双方视角协商创建契约，明确：
  - 本次冲刺的具体范围是什么？
  - 需要验证哪些验收标准？
  - 每条标准采用什么验证方式？
  - 若涉及 Java，Java 总门禁、触发维度核心门禁、分布式 Java 门禁是否都有可验收条目？
  - 若涉及前端，Frontend Gate 与 BYAI 参考是否都有可验收条目？

### 3. 构建循环

最多重复 3 轮：

1. **Build**：调用 `generator` 实现本轮冲刺。
2. **Self-verify**：`generator` 先自检。
   - 检查所有新增/修改函数、方法是否补齐中文注释（用途、参数、返回值、副作用）。
   - 若涉及 Java，逐项检查 Java 总门禁和触发维度核心门禁，并运行 `.codex/hooks/convention-check.py --changed-only` 或 `.claude/hooks/convention-check.py --changed-only`。
   - 若涉及 Java，逐项检查通用工程、分层与 DDD、Dubbo 与公共 API、日志与异常、持久化与基础设施、测试安全运维等触发维度。
   - 若涉及 Java，逐项检查分布式 Java 门禁；未触发需说明理由，触发时必须给出实现证据与人工确认项。
   - 若涉及前端，检查三层前端规范：无硬编码颜色、无裸全局样式、无无解释 inline style，状态覆盖完整，视觉/响应式已验证。
3. **Evaluate**：调用 `evaluator` 按契约测试。
4. **Gate**：检查单元测试是否通过。
   - 若 PASS：冲刺完成（QA 报告保留为质量参考，不阻塞）。
   - 若 FAIL：把失败项回传给 `generator` 修复。

### 4. 最大迭代次数

若连续 3 轮仍失败：
- 记录失败项并保留当前 feature `passes=false`。
- 建议：缩小范围、拆分更小冲刺、或人工介入。
- 继续推进下一个 feature（不阻塞整体流程）。

### 5. 完成收尾

若单元测试通过：
- 更新契约中的冲刺日志。
- 确认目标 feature 的 `spec_path` 与 `contract_path` 文件真实存在；缺任一文件时禁止 `passes=true`。
- 若项目使用 task-harness（存在 `.harness/task-harness/index.json`），仅在单元测试通过且 spec/contract 文件存在后，更新 active bucket 中对应 feature 的 `passes=true`（若存在 `.harness/feature_list.json` 则脚本会同步兼容镜像）。
- 在 `.harness/task-harness/progress/latest.txt` 记录本轮结果（若文件存在）。
- 询问用户是否执行 `doc-gardener` 做文档新鲜度检查。
