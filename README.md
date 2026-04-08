# santong Skills 技能仓库

这里是的 Skills 技能集合，每个子目录代表一个独立的技能。

## 目录结构

```
santong-skills/
├── reshape-your-life/        # 重塑人生技能
├── harness-engineering/      # Harness Engineering 框架一键初始化
└── ...
```

## Skills 列表

### harness-engineering

基于 OpenAI (Codex)、Anthropic (三智能体架构)、LangChain (自验证循环) 的 Harness Engineering 框架。

在任意项目中一键初始化 Plan-Build-Verify 开发工作流：
- **双平台入口**: `AGENTS.md` (Codex) + `CLAUDE.md` (Claude)
- **Codex 意图路由**: 在 `AGENTS.md` 中定义 `plan/build/qa/sprint` 执行契约
- **双 Hook 运行时**: `.claude/settings.json` + `.codex/hooks.json`
- **4 个智能体**: Planner / Generator / Evaluator / Doc Gardener
- **4 个命令**: `/plan` / `/build` / `/qa` / `/sprint`
- **3 个 Hooks**: 循环检测 / 完成前检查 / 上下文注入
- **10 条黄金原则**: 无规格不编码、可测试验收标准、契约驱动等

使用: `/harness <项目描述>` 或说 "初始化 harness"


### task-harness

任务管理 Harness。

- **持久化任务源**: `feature_list.json` 作为单一真相来源
- **会话恢复**: `init.sh` + `progress.txt`
- **Codex 契约入口**: 可生成项目级 `AGENTS.md` 约束执行流程

## 如何贡献

欢迎提交新的 Skills！请确保每个技能包含：
- `SKILL.md` - 技能定义文档
- `references/` - 相关参考资料（可选）

## 许可

MIT License
