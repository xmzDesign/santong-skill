---
name: harness-engineering
description: "在当前项目一键初始化 Harness Engineering 框架。适用于用户提到 'harness'、'init harness'、'initialize framework'、'setup harness engineering'、'/harness'，或希望搭建 Plan-Build-Verify 工作流（planner/generator/evaluator）时。会生成 AGENTS.md（Codex）、CLAUDE.md（Claude）、智能体定义、命令模板、hooks 与文档结构。"
---

# Harness Engineering 框架

在任意项目目录中，一键初始化完整的 Harness Engineering 研发框架。

该技能综合了 OpenAI（Codex）、Anthropic（三智能体协作）与 LangChain（自验证循环）的实践，初始化内容包括：

- **3 智能体架构**：Planner（规格）、Generator（实现）、Evaluator（测试）
- **Codex + Claude 双入口**：`AGENTS.md` 与 `CLAUDE.md`
- **冲刺契约（Sprint Contract）**：编码前先定义可机器验证的“完成标准”
- **双 Hook 运行时**：Claude hooks（`.claude`）+ Codex hooks（`.codex`）
- **斜杠命令**：`/plan`、`/build`、`/qa`、`/sprint`
- **黄金原则**：跨智能体统一执行的 10 条不可妥协规则

## 适用场景

- 新项目起步，希望快速建立结构化 AI 协作研发流程
- 需要在当前项目落地 `Plan -> Build -> Verify -> Fix` 工作流
- 用户提到 “harness / init harness / setup framework” 等类似意图

## 初始化流程

### 第 1 步：收集项目信息

在生成文件前，先向用户确认：

1. **项目名称**（或从当前目录名自动识别）
2. **技术栈**（可选，如 “React + Node.js”“Python FastAPI”“Go 微服务”）
3. **项目类型**（Web 应用、API 服务、CLI 工具、库等）

如果用户通过 `/harness <description>` 提供描述，直接从上下文抽取上述信息。

### 第 2 步：生成框架文件

执行脚手架脚本：

```bash
python3 {{SKILL_PATH}}/scripts/scaffold.py --project-name "<PROJECT_NAME>" --tech-stack "<TECH_STACK>" --project-type "<PROJECT_TYPE>" --target-dir "<CURRENT_PROJECT_DIR>"
```

会在当前项目生成以下结构：

```
<project>/
  AGENTS.md                        # Codex 指南 / 入口
  CLAUDE.md                        # 项目地图（<80 行）
  .codex/
    config.toml                    # 启用 Codex hooks
    hooks.json                     # Codex hook 注册表
    hooks/
      loop-detector.py             # PreToolUse 循环守卫
      pre-completion-check.py      # Stop 阶段检查提醒
      context-injector.py          # UserPromptSubmit 上下文注入
  .claude/
    agents/
      planner.md                   # 规格生成智能体
      generator.md                 # 实现智能体
      evaluator.md                 # 测试/评分智能体
      doc-gardener.md              # 文档新鲜度智能体
    commands/
      plan.md                      # /plan 命令
      build.md                     # /build 命令
      qa.md                        # /qa 命令
      sprint.md                    # /sprint 命令
    hooks/
      loop-detector.py             # 文件编辑循环检测
      pre-completion-check.py      # 任务完成检查清单
      context-injector.py          # 会话上下文中间件
  docs/
    architecture.md                # 系统设计
    golden-principles.md           # 不可妥协规则
    sprint-workflow.md             # 冲刺流程
    contracts/
      TEMPLATE.md                  # 冲刺契约模板
    specs/                         # （由 planner 产出）
    plans/                         # （由 planner 产出）
```

### 第 3 步：配置 Hooks

`scaffold.py` 会自动完成 Hook 配置：
- Claude hooks：合并写入 `.claude/settings.json`（不存在则创建）
- Codex hooks：合并写入 `.codex/hooks.json`（不存在则创建），并生成 `.codex/config.toml`

### 第 4 步：验证安装结果

确认关键文件已生成：

```bash
ls -la AGENTS.md CLAUDE.md .codex/ .codex/hooks/ .claude/agents/ .claude/commands/ .claude/hooks/ docs/
```

执行 Codex hook 自检：

```bash
test -f .codex/config.toml && \
test -f .codex/hooks.json && \
test -f .codex/hooks/context-injector.py && \
test -f .codex/hooks/loop-detector.py && \
test -f .codex/hooks/pre-completion-check.py && \
python3 -m py_compile .codex/hooks/context-injector.py .codex/hooks/loop-detector.py .codex/hooks/pre-completion-check.py && \
echo "Codex hooks: OK"
```

期望结果：
- 命令退出码为 `0`
- 输出包含 `Codex hooks: OK`

最后向用户汇报“创建了哪些内容”以及“如何开始使用”。

## 初始化完成后的使用方式

| Command | Purpose |
|---------|---------|
| `/plan <description>` | 基于 1-4 句话生成功能规格 |
| `/build` | 按冲刺流程实现最新规格 |
| `/qa` | 对当前代码执行评估 |
| `/sprint <description>` | 从零执行完整 Plan-Build-Verify 周期 |

Codex 用户可通过提示词触发同一流程：
- `plan <description>`
- `build <spec>`
- `qa <contract>`
- `sprint <description>`

Codex hook 运行时会生成在：
- `.codex/config.toml`
- `.codex/hooks.json`
- `.codex/hooks/*.py`

Codex 的执行细节（意图路由、输出契约、停止条件）定义在生成后的 `AGENTS.md` 中。

## 核心原则

框架会强制执行以下规则（安装后见 `docs/golden-principles.md`）：

1. **先 Spec 后代码**：没有书面规格就不允许实现
2. **标准可测试**：每个功能都必须有可机器验证的验收标准
3. **先自检再评估**：Evaluator 运行前，Generator 必须先完成自检
4. **循环感知**：同一文件编辑 5 次以上必须停下来复盘
5. **契约驱动**：编码前先通过 Sprint Contract 定义“完成”

## 架构流程

完整细节请阅读安装后生成的 `docs/architecture.md`。关键流转如下：

```
用户需求 → Planner（产出 spec）→ Generator + Evaluator 协商契约
→ Generator 实现 → Evaluator 测试 → 修复循环（最多 3 轮）→ 完成
```
