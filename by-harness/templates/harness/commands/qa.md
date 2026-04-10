---
description: 让 evaluator 对当前代码状态执行评估
argument-hint: 可选 - 指定要评估的 contract 或 spec
---

# 质量保障（QA）

对当前实现执行完整评估流程。

**目标**：$ARGUMENTS（为空时默认对 `.harness/docs/contracts/` 中的契约进行评估）

## 流程

### 1. 选择目标

- 若传入参数：按指定 contract/spec 评估。
- 若未传参数：列出 `.harness/docs/contracts/` 下全部契约让用户选择，或默认评估最新契约。

### 2. 调用 Evaluator

启动 `evaluator` 智能体，其会：
1. 读取冲刺契约中的验收标准。
2. 用 Playwright MCP 做 E2E 浏览器测试。
3. 用 Chrome DevTools 检查控制台错误、网络与性能。
4. 若涉及 UI，结合截图进行视觉检查。
5. 阅读源码并校验逻辑正确性。

### 3. 评分报告

`evaluator` 会输出结构化报告，包含：
- 每条标准的通过/失败状态
- 总分（0-100）
- 具体失败细节、复现步骤和修复建议

### 4. 后续动作

若分数偏低：
- 提示可执行 `/build` 进入修复循环
- 展示需要处理的具体失败项

若分数较高：
- 报告通过
- 可选执行 `doc-gardener` 做文档新鲜度检查

说明：
- QA 报告用于质量跟踪，默认不阻塞任务推进。
- 是否标记 `passes=true` 以单元测试结果为准。
