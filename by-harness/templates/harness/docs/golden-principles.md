# 黄金原则（Golden Principles）

以下是适用于所有智能体与工作流的**不可妥协规则**，吸收了 OpenAI（Codex）、Anthropic（三智能体架构）与 LangChain（自检循环）的核心经验。

---

## 1. 先有 Spec，再写代码（Spec Before Code）

没有写入 `docs/specs/` 的规格说明，就不允许进入实现阶段。

**为什么**：没有明确目标时，模型容易发散。Spec 能锚定 Generator，也让 Evaluator 有可验证对象。（OpenAI）

**如何执行**：Planner 必须先产出 spec，再允许编码。即使你“已经很清楚”，也要先写 spec。

## 2. 验收标准必须可测试（Testable Acceptance Criteria）

每个功能都必须有机器可判定的通过/失败标准。

**为什么**：“看起来不错”这类主观标准会导致评估偏宽松。机器可验证标准能强制精确表达。（Anthropic）

**如何执行**：每条 contract 验收标准都要指定验证方式：单元测试、Playwright E2E、控制台检查、视觉对比或构建成功。

## 3. 一次只做一个 Sprint（One Sprint at a Time）

Generator 每次只实现一个功能冲刺，随后由 Evaluator 验证，再进入下一项。

**为什么**：长任务会引发上下文漂移与“上下文焦虑”（提前收尾、反复犯错）。拆成 Sprint 可保持稳定。（Anthropic）

**如何执行**：每个 sprint contract 都要有清晰边界。完成一个、评估一个，再开始下一个。

## 4. 先自检，再评估（Self-Verify First）

Generator 在交给 Evaluator 前必须先完成自检。

**为什么**：模型天然偏向“第一个看起来可行的答案”。先自检可拦截明显错误，避免浪费评估轮次。（LangChain）

**如何执行**：实现后必须：1）复读代码；2）检查编译/构建；3）逐条对照 spec；4）运行可用测试。

## 5. 循环感知（Loop Awareness）

同一文件若连续编辑 5 次以上仍无进展，必须停止并重估方案。

**为什么**：模型容易进入“无效循环”——在错误路径上反复微调。Loop hook 是防浪费机制。（LangChain）

**如何执行**：`loop-detector` 在阈值后阻断写入。被阻断后应换策略，而不是继续微调同一方案。

## 6. 控制上下文预算（Context Budget）

智能体只读“必要信息”，不要通读全仓库。

**为什么**：上下文是稀缺资源。无关内容过多会挤占任务空间，导致漏约束或优化方向错误。（OpenAI）

**如何执行**：Planner 只读相关代码；Generator 以 spec+contract 为主；Evaluator 只读 contract 与必要源码。

## 7. 渐进披露（Progressive Disclosure）

文档采用三层结构：摘要 → 细节 → 引用。

**为什么**：遵循“地图而非百科全书”原则。入口轻量、细节可跳转，可兼顾上下文精简与深度可达。（OpenAI）

**如何执行**：`AGENTS.md`（Codex）与 `CLAUDE.md`（Claude）作为入口地图；`docs/` 承载细节；spec 与 contract 承载任务深度。

## 8. 文档新鲜度（Doc Freshness）

每次冲刺后，都要验证文档是否与代码一致。

**为什么**：过期文档比没有文档更危险，会把实现引向错误假设。（OpenAI 的 doc gardening 实践）

**如何执行**：冲刺完成后运行 `doc-gardener`，检查引用路径存在性、示例有效性、新功能文档覆盖情况。

## 9. 问题必须显式暴露（Fail Loudly）

hook 与智能体发现问题时必须显式报告，不能静默降级。

**为什么**：静默失败会积累为高成本技术债。越早暴露，修复成本越低。（OpenAI）

**如何执行**：hook 阻断要给明确原因；智能体要给结构化失败报告；禁止“默认应该没问题”的隐式假设。

## 10. 契约驱动（Contract-Driven）

在实现开始前，由 sprint contract 明确定义“完成”标准。

**为什么**：没有共识标准时，Generator 与 Evaluator 会出现“各自的成功定义”。契约可在编码前统一预期。（Anthropic）

**如何执行**：每次 sprint 前，Generator 提出实现内容与验证方式，Evaluator 审核确认，双方一致后再开始编码。
