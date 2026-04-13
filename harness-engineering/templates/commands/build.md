---
description: 按冲刺工作流实现最近的规格说明
argument-hint: 可选 - 指定 docs/specs/ 中要实现的 spec 文件
---

# 构建功能

使用 Generator-Evaluator 循环实现功能。

**目标**：$ARGUMENTS（为空时默认使用 `docs/specs/` 中最近修改的规格）

## 流程

### 1. 读取规格

从 `docs/specs/` 读取目标规格。若未传参数，自动选择最近修改的 spec 文件。

### 2. 冲刺契约（Sprint Contract）

检查该功能在 `docs/contracts/` 下是否已有契约：
- 若已存在：读取并继续构建。
- 若不存在：从 Generator 与 Evaluator 双方视角协商创建契约，明确：
  - 本次冲刺的具体范围是什么？
  - 需要验证哪些验收标准？
  - 每条标准采用什么验证方式？

### 3. 构建循环

最多重复 3 轮：

1. **Build**：调用 `generator` 实现本轮冲刺。
2. **Self-verify**：`generator` 先自检。
   - 检查所有新增/修改函数、方法是否补齐中文注释（用途、参数、返回值、副作用）。
3. **Evaluate**：调用 `evaluator` 按契约测试。
4. **Grade**：检查评分是否 `>= 80/100`。
   - 若 PASS：冲刺完成。
   - 若 FAIL：把失败项回传给 `generator` 修复。

### 4. 最大迭代次数

若连续 3 轮仍失败：
- 暂停流程并向用户汇总所有失败项。
- 建议：缩小范围、拆分更小冲刺、或人工介入。
- **不要继续盲目迭代。**

### 5. 完成收尾

若冲刺通过：
- 更新契约中的冲刺日志。
- 若项目使用 task-harness（存在 `feature_list.json`），仅在 `qa >= 80/100` 后更新对应 feature 的 `passes=true`。
- 在 `progress.txt` 记录本轮结果（若文件存在）。
- 询问用户是否执行 `doc-gardener` 做文档新鲜度检查。
