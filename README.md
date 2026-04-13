# santong Skills 技能仓库

这里是 Skills 技能集合，每个子目录代表一个独立的技能。

## 目录结构

```
santong-skills/
├── by-harness/               # 独立融合版（初始化 + 持续拆任务）
├── harness-engineering/      # Harness Engineering 框架一键初始化
└── ...
```

## Skills 列表

### by-harness

独立融合版 Harness。

用于一键落地“拆分任务 -> 执行 -> 测试”的统一闭环，且不依赖其他 skill 目录，核心包含：
- 根目录极简：默认只放 `AGENTS.md`（以及隐藏运行目录 `.codex/.claude`）
- 工作文件集中到 `.harness/`：`CLAUDE.md`、`docs/`、`TASK-HARNESS.md`、`feature_list.json`、`task-harness/`、`progress.txt`、`init.sh`、`task.json`
- 初始化会话收口工具：`.harness/scripts/session_close.py`（维护会话日志 + 最新快照）
- 支持后续持续拆任务：把新任务增量写入 active bucket（自动同步 `.harness/feature_list.json` 兼容镜像）
- 每个任务含闭环工件字段：`spec_path` / `contract_path` / `qa_report_path`
- 工件语义：`spec_path=技术方案`，`contract_path=测试计划/验收标准`，`qa_report_path=测试结果`
- 当前门禁策略：单元测试通过即可 `passes=true`，QA 报告默认非阻塞
- 代码注释准则：所有新增/修改函数、方法必须补齐中文注释（用途、参数、返回值、副作用）

一体化初始化命令：

```bash
python3 by-harness/scripts/scaffold.py \
  --project-name "your-project" \
  --description "一句话描述项目目标" \
  --tech-stack "React + Node.js" \
  --project-type "web app" \
  --target-dir "."
```

初始化后建议先执行：

```bash
bash .harness/init.sh
```

持续拆任务命令：

```bash
python3 by-harness/scripts/decompose_tasks.py \
  --target-dir "." \
  --item "新增用户权限矩阵" \
  --item "增加组织级审计日志"
```

任务重平衡命令（需求持续增长时）：

```bash
python3 by-harness/scripts/rebalance_tasks.py --target-dir "."
```

会话收口命令：

```bash
python3 .harness/scripts/session_close.py \
  --target-dir "." \
  --feature-id "feat-03" \
  --outcome "in-progress" \
  --qa-score 72 \
  --note "已完成 plan/build，准备进入 fix"
```

手动提示词入口（在 Codex 手动选择 `by-harness` 后直接输入）：
- `初始化`
- `持续拆任务 主题：权限系统，拆 6 个`
- `执行 feat-03`

### harness-engineering

基于 OpenAI (Codex)、Anthropic (三智能体架构)、LangChain (自验证循环) 的 Harness Engineering 框架。

在任意项目中一键初始化 Plan-Build-Verify 开发工作流，核心包含：
- **双平台入口**: `AGENTS.md` (Codex) + `CLAUDE.md` (Claude)
- **双 Hook 运行时**: `.codex/hooks.json` + `.claude/settings.json`
- **4 个智能体**: Planner / Generator / Evaluator / Doc Gardener
- **4 个命令**: `/plan` / `/build` / `/qa` / `/sprint`
- **10 条黄金原则**: 无规格不编码、可测试验收标准、契约驱动等
- **中文注释规范**: 所有新增/修改函数、方法必须具备中文注释

#### Claude 与 Codex 使用方式对照

| 维度 | Claude | Codex |
|---|---|---|
| 入口文件 | `CLAUDE.md` | `AGENTS.md` |
| 触发方式 | 斜杠命令（如 `/plan`、`/sprint`） | 自然语言意图（如 `plan xxx`、`sprint xxx`） |
| Hook 配置 | `.claude/settings.json` | `.codex/hooks.json` + `.codex/config.toml` |
| Hook 脚本目录 | `.claude/hooks/` | `.codex/hooks/` |
| 推荐场景 | 以命令驱动的工作流 | 以意图驱动的连续对话工作流 |

#### Hook 文件作用说明

以下三个 hook 文件在 Claude/Codex 两套运行时中职责一致，只是接入配置不同：

| Hook 文件 | 作用 | 典型触发时机 |
|---|---|---|
| `context-injector.py` | 注入当前项目上下文（分支、最近提交、活跃 spec/contract/plan） | 用户新一轮输入时（`UserPromptSubmit`） |
| `loop-detector.py` | 追踪同一文件的反复编辑次数，接近阈值警告，超阈值阻断 | 工具写入前（`PreToolUse`） |
| `pre-completion-check.py` | 在结束前提醒完成质量清单（构建、测试、验收标准、文档） | 完成/停止阶段（Claude: `PostToolUse`；Codex: `Stop`） |

使用方式：在项目目录执行 `harness-engineering` 初始化后，按需在 `AGENTS.md` 或 `CLAUDE.md` 开始工作流即可。


### task-harness

任务管理 Harness。

用于把需求拆解为可长期追踪的任务系统，默认与 `harness-engineering` 组合使用，核心包含：
- **持久化任务源**: `feature_list.json` 作为单一真相来源
- **会话恢复**: `init.sh` + `progress.txt`
- **任务层契约**: `TASK-HARNESS.md`（不覆盖 `AGENTS.md`）
- **项目总览**: `task.json`（里程碑、规则、文件清单）

#### Claude 与 Codex 使用方式对照

| 维度 | Claude | Codex |
|---|---|---|
| 主要入口 | `task-harness/SKILL.md` 流程引导 | `AGENTS.md`（主闭环）+ `TASK-HARNESS.md`（任务层） |
| 触发方式 | “拆解任务/任务管理/项目规划”类请求 | 自然语言执行意图（如“执行下一个未完成任务”） |
| 会话启动 | 建议先读 `progress.txt` + `feature_list.json` | 强制先 `bash init.sh`，再读两个契约文件 |
| 状态更新 | 完成功能后更新 `passes` + 记录日志 | 单元测试通过即可 `passes=true`（QA 报告非阻塞） |
| 适合场景 | 规划与拆解阶段 | 长时、多会话、持续推进阶段 |

#### 核心文件作用说明

| 文件 | 作用 | 使用要点 |
|---|---|---|
| `feature_list.json` | 任务单一真相来源 | 仅修改 `passes: false -> true`，不要改结构/描述 |
| `init.sh` | 会话快速恢复脚本 | 每次会话开头运行，输出 git 状态与剩余任务 |
| `progress.txt` | 叙事化进度日志 | 记录“做了什么 + 为什么 + 下一步” |
| `task.json` | 项目级总览 | 维护里程碑、规则和修改文件范围 |
| `AGENTS.md` | 主执行契约（harness-engineering） | 固化 Plan-Build-Verify-Fix 规则 |
| `TASK-HARNESS.md` | 任务层契约（task-harness） | 固化选任务、更新 passes、记录 progress 的规则 |

#### 推荐闭环顺序（组合模式）

1. 先初始化 `harness-engineering`（生成 `AGENTS.md` 和 hooks）
2. 再执行 `task-harness` 脚手架（生成 `feature_list.json` / `TASK-HARNESS.md` 等）
3. 每次会话按单个 feature 执行：`plan -> build -> qa -> (fix)`  
4. 单元测试通过即可更新该 feature 的 `passes=true`（QA 报告仅用于质量跟踪）

初始化命令示例：

```bash
python3 task-harness/scripts/scaffold.py \
  --project-name "your-project" \
  --description "一句话描述项目目标" \
  --tech-stack "React + Node.js" \
  --target-dir "."
```

## 如何贡献

欢迎提交新的 Skills！请确保每个技能包含：
- `SKILL.md` - 技能定义文档
- `references/` - 相关参考资料（可选）

## 许可

MIT License
