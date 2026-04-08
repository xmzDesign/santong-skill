# santong Skills 技能仓库

这里是 Skills 技能集合，每个子目录代表一个独立的技能。

## 目录结构

```
santong-skills/
├── harness-engineering/      # Harness Engineering 框架一键初始化
└── ...
```

## Skills 列表

### harness-engineering

基于 OpenAI (Codex)、Anthropic (三智能体架构)、LangChain (自验证循环) 的 Harness Engineering 框架。

在任意项目中一键初始化 Plan-Build-Verify 开发工作流，核心包含：
- **双平台入口**: `AGENTS.md` (Codex) + `CLAUDE.md` (Claude)
- **双 Hook 运行时**: `.codex/hooks.json` + `.claude/settings.json`
- **4 个智能体**: Planner / Generator / Evaluator / Doc Gardener
- **4 个命令**: `/plan` / `/build` / `/qa` / `/sprint`
- **10 条黄金原则**: 无规格不编码、可测试验收标准、契约驱动等

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

用于把需求拆解为可长期追踪的任务系统，核心包含：
- **持久化任务源**: `feature_list.json` 作为单一真相来源
- **会话恢复**: `init.sh` + `progress.txt`
- **执行契约入口**: `AGENTS.md`（尤其适配 Codex 多轮会话）
- **项目总览**: `task.json`（里程碑、规则、文件清单）

#### Claude 与 Codex 使用方式对照

| 维度 | Claude | Codex |
|---|---|---|
| 主要入口 | `task-harness/SKILL.md` 流程引导 | 项目根 `AGENTS.md` 执行契约 |
| 触发方式 | “拆解任务/任务管理/项目规划”类请求 | 自然语言执行意图（如“执行下一个未完成任务”） |
| 会话启动 | 建议先读 `progress.txt` + `feature_list.json` | 强制先 `bash init.sh`，再按 `AGENTS.md` 规则执行 |
| 状态更新 | 完成功能后更新 `passes` + 记录日志 | 同上，但更强调契约化输出与阻塞上报 |
| 适合场景 | 规划与拆解阶段 | 长时、多会话、持续推进阶段 |

#### 核心文件作用说明

| 文件 | 作用 | 使用要点 |
|---|---|---|
| `feature_list.json` | 任务单一真相来源 | 仅修改 `passes: false -> true`，不要改结构/描述 |
| `init.sh` | 会话快速恢复脚本 | 每次会话开头运行，输出 git 状态与剩余任务 |
| `progress.txt` | 叙事化进度日志 | 记录“做了什么 + 为什么 + 下一步” |
| `task.json` | 项目级总览 | 维护里程碑、规则和修改文件范围 |
| `AGENTS.md` | 执行契约 | 固化会话顺序、验证要求、阻塞处理和输出格式 |

## 如何贡献

欢迎提交新的 Skills！请确保每个技能包含：
- `SKILL.md` - 技能定义文档
- `references/` - 相关参考资料（可选）

## 许可

MIT License
