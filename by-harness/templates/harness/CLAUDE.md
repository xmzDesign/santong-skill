# {{PROJECT_NAME}}

> Harness Engineering Framework 已启用，Plan-Build-Verify 工作流已生效。

## 快速参考

| 命令 | 作用 |
|---------|---------|
| `/plan <description>` | 根据 1-4 句话生成功能 spec |
| `/build` | 按冲刺流程实现最新 spec |
| `/qa` | 对当前代码执行评估 |
| `/sprint <description>` | 执行完整 Plan-Build-Verify 周期 |

Codex 用户请参考 `AGENTS.md`（提示词驱动工作流）。  
Codex hooks 配置位于 `.codex/config.toml` 与 `.codex/hooks.json`。

## 架构

系统设计请见 [docs/architecture.md](docs/architecture.md)。

## 黄金原则

请阅读 [docs/golden-principles.md](docs/golden-principles.md)，这些规则不可妥协。

## 智能体

| Agent | 角色 | 触发 |
|-------|------|---------|
| planner | 将简述需求扩展为 spec | `/plan` |
| generator | 按 sprint 实现功能 | `/build` |
| evaluator | 测试并评分 | `/qa` |
| doc-gardener | 维护文档新鲜度 | Sprint 完成后 |

## 冲刺工作流

1. **Plan**：Planner 在 `docs/specs/` 产出 spec  
2. **Contract**：Generator + Evaluator 先对“完成标准”达成一致  
3. **Build**：Generator 完成一个 sprint 的实现  
4. **Verify**：Evaluator 按 contract 测试（阈值 `80/100`）  
5. **Fix**：若分数 `< 80`，Generator 进入修复（最多 3 轮）  
6. **Complete**：更新文档并执行 doc-gardener  

完整流程请见 [docs/sprint-workflow.md](docs/sprint-workflow.md)。

## 项目结构

``` 
docs/
  architecture.md     -- 系统设计
  golden-principles.md -- 核心规则
  sprint-workflow.md  -- 冲刺流程
  contracts/          -- Sprint 完成定义
  specs/              -- 功能规格
  plans/              -- 实施计划
.claude/
  agents/             -- 智能体定义
  commands/           -- 斜杠命令
  hooks/              -- 自动守卫
```

## 已启用 Hook

- **循环检测**：同一文件编辑超过 5 次后阻断
- **完成前检查**：标记完成前注入检查清单
- **上下文注入**：会话开始时补充环境信息

## 技术栈

{{TECH_STACK}}
