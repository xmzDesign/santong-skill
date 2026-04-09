---
name: task-harness
description: 将需求拆解为结构化任务清单，生成长时运行 Agent 的任务管理系统（基于 Anthropic Effective harnesses 方法论）。当用户需要管理多会话开发任务、跟踪功能完成进度、或要求"拆解任务""任务管理""项目规划"时自动触发
argument-hint: "[项目名称] [需求描述]"
disable-model-invocation: false
user-invocable: true
---

# Task Harness — 结构化任务管理系统

将任意需求拆解为结构化任务清单，为长时运行的 Agent 建立可靠的任务追踪系统。

基于 [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) 方法论。

默认与 `harness-engineering` **组合使用**：
- `harness-engineering` 负责主闭环（`AGENTS.md` + Plan/Build/Verify 规则）
- `task-harness` 负责任务层（`feature_list.json` + `TASK-HARNESS.md` + 进度追踪）
- 两者合并后形成：**拆分任务 -> 执行冲刺 -> QA 验收 -> 更新任务状态**

## 何时使用

- 大型需求需要拆解为多个子任务
- 项目需要跨多个 Agent 会话持续开发
- 需要跟踪功能完成进度（已完成 / 未完成）
- 用户说"拆解任务"、"任务管理"、"项目规划"、"创建任务清单"

## 先决条件（推荐）

在项目中优先执行 `harness-engineering` 初始化，确保存在：
- 根目录 `AGENTS.md`（Codex 主执行契约）
- `docs/specs/`、`docs/contracts/`、`docs/plans/`
- hooks 与 Plan-Build-Verify 规则

若项目尚未初始化 Harness Engineering，先提示用户完成初始化，再创建 task-harness 文件。

## 核心流程

### Step 1: 分析代码库

探索项目结构，理解：
- 技术栈（语言、框架、构建工具）
- 目录结构和架构模式
- 现有配置（package.json、go.mod 等）
- 关键入口文件

### Step 2: 设计任务列表

根据用户需求，将工作拆解为具体的功能点（features）。每个功能点需要：
- 唯一的 `id`（如 `feat-01`、`v2-05`）
- `category` 分类（foundation、layout、components 等）
- `priority` 优先级（数字越小越优先）
- `description` 一句话描述
- `file` 主要涉及的文件路径（可为 null）
- `steps` 具体操作步骤数组（每步一个字符串）
- `passes` 布尔值（初始为 false）
- `verification` 验证条件

### Step 3: 执行脚手架（优先）

优先使用脚手架脚本生成任务层文件：

```bash
python3 {{SKILL_PATH}}/scripts/scaffold.py \
  --project-name "<项目名称>" \
  --description "<项目描述>" \
  --tech-stack "<技术栈>" \
  --design-guidance "<设计约束，可选>" \
  --target-dir "<当前项目目录>"
```

脚本默认要求目标目录存在 `AGENTS.md`（主闭环契约）。  
若确需跳过该检查，可追加：`--allow-missing-main-contract`。

### Step 4: 生成 5 个 Harness 文件（脚本产物）

在项目根目录生成以下文件：

#### `feature_list.json` — 任务清单（唯一真相来源）

```json
{
  "project": "项目名称",
  "description": "项目描述",
  "features": [
    {
      "id": "feat-01",
      "category": "foundation",
      "priority": 1,
      "description": "一句话描述要做什么",
      "file": "path/to/main/file.js",
      "steps": [
        "具体步骤 1",
        "具体步骤 2"
      ],
      "passes": false,
      "verification": "如何验证这个功能已完成"
    }
  ]
}
```

完整模板见 [references/templates/feature_list.json](references/templates/feature_list.json)

**为什么用 JSON 而不是 Markdown？** 模型倾向于自由改写 Markdown 文件（改写措辞、重组结构、删除内容）。JSON 文件被模型更谨慎对待——更可能只修改特定字段。这对维护任务完整性至关重要。

#### `progress.txt` — 叙事性进度日志

记录每个会话的详细工作内容，供后续会话理解上下文。

完整模板见 [references/templates/progress.txt](references/templates/progress.txt)

#### `init.sh` — 环境初始化脚本

每个新会话开始时运行，5 秒内恢复全部上下文。

完整模板见 [references/templates/init.sh](references/templates/init.sh)

#### `task.json` — 项目总览

记录里程碑、规则、文件清单等项目级信息。

完整模板见 [references/templates/task.json](references/templates/task.json)

#### `TASK-HARNESS.md` — 任务层执行契约（不覆盖 AGENTS.md）

定义任务拆分与进度追踪规则，且明确要求执行时遵循根目录 `AGENTS.md` 的 Harness 主闭环。

完整模板见 [references/templates/TASK-HARNESS.md](references/templates/TASK-HARNESS.md)

### Step 5: 校验 TASK-HARNESS.md 规则

根据项目上下文替换 `TASK-HARNESS.md` 模板中的占位符（项目名、项目描述），并确保其规则与 `feature_list.json` 保持一致。

同时检查根目录 `AGENTS.md` 是否存在：
- 存在：保持不覆盖，直接集成使用
- 不存在：提示先执行 `harness-engineering` 初始化

### Step 6: 首次验证

运行 `bash init.sh`，确认：
- 脚本可正常执行
- feature_list.json 解析正确
- 进度统计准确显示
- `TASK-HARNESS.md` 已创建
- 根目录 `AGENTS.md` 存在且可用于 Codex 主闭环

### Step 7: 输出下一步指引

告诉用户：
- 已创建的文件列表
- 如何按 `AGENTS.md + TASK-HARNESS.md` 开始第一个任务
- 如何在新会话中恢复工作

## Agent 工作流（每个会话）

```
1. bash init.sh                    ← 5 秒上下文恢复
2. Read AGENTS.md                  ← 主闭环（Plan/Build/Verify）契约
3. Read TASK-HARNESS.md            ← 任务层契约
4. Read progress.txt               ← 理解之前做了什么、为什么
5. Read feature_list.json          ← 找到优先级最高的未完成功能
6. Pick 1 feature                  ← 一次只推进一个功能
7. Execute plan/build/qa loop      ← 严格按 Harness Engineering 流程
8. Verify qa score >= 80           ← 通过后才允许标记完成
9. Update feature_list.json        ← 仅改 passes: false → true
10. Append progress.txt            ← 记录本次会话结果与下一步
11. git commit + git push          ← 同步稳定进度
```

## 严格规则

- **AGENTS.md 为主契约**：Plan -> Contract -> Build -> QA -> Fix loop 流程必须执行，禁止跳阶段。
- **只修改 `passes` 字段**：在 feature_list.json 中，只将 `passes` 从 `false` 改为 `true`。永远不要删除功能、编辑描述、修改优先级或重组 JSON。
- **一次一个功能**：每个会话优先只做一个 feature，避免上下文污染。
- **必须 QA 达标后再标记完成**：仅在 `qa >= 80/100` 后可更新 `passes=true`。
- **必须 commit + push**：每个功能完成后必须 git commit 和 push，确保进度永不丢失且可独立回滚。
- **必须更新 progress.txt**：会话结束时更新进度日志，让下一个会话有完整上下文。
- **遇到阻塞时停止**：在 progress.txt 中记录阻塞原因并停止。不要默默绕过问题。

## 文件间关系

```
init.sh ──读取──→ feature_list.json (任务状态)
    │
    └──提示──→ progress.txt (历史上下文)

task.json ────→ 项目总览（里程碑、规则、文件清单）

AGENTS.md ───────→ Harness 主执行契约（Plan/Build/Verify）
TASK-HARNESS.md ─→ 任务层执行契约（挑任务/更新 passes/记录进度）
```

## 引用

- [方法论详解](references/methodology.md) — 为什么用 harness、常见问题、最佳实践
- [模板文件](references/templates/) — 所有 harness 文件的空白模板
