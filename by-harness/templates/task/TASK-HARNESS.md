# {{项目名称}} - TASK-HARNESS 任务层执行规则

本文件是任务层契约，负责“任务拆分与进度追踪”。  
根目录 `AGENTS.md` 由 Harness Engineering 管理，负责 `Plan -> Build -> Verify` 主闭环。两者必须同时遵循。

## 工件定位（技术方案 / 测试计划 / 验证结果）

- 技术方案：`spec_path` 指向的规格文件（通常为 `.harness/docs/specs/<task-id>.md`）
- 测试计划与验收标准：`contract_path` 指向的契约文件（通常为 `.harness/docs/contracts/<task-id>.md`）
- 测试结果与评分：`qa_report_path` 指向的 QA 报告（通常为 `.harness/docs/qa/<task-id>.md`）

## 会话启动（必须按顺序）

1. 运行 `bash .harness/scripts/init.sh`（legacy 项目可用 `bash .harness/init.sh`）
2. 阅读根目录 `AGENTS.md`/`CLAUDE.md`（主工作流约束）
3. 阅读 `.harness/docs/TASK-HARNESS.md`（任务追踪约束）
4. 阅读 `.harness/task-harness/index.json`（定位 `task_globs`）
5. 阅读对应单任务文件（如 `.harness/task-harness/tasks/<batch-id>/<display-id>-<title>-<hash>.json`；旧 `.harness/task-harness/tasks/<task-id>.json`、`.harness/task-harness/features/*.json` 与 `.harness/feature_list.json` 仅作兼容查看）
6. 阅读 `.harness/task-harness/progress/YYYY-MM/*.md`（`latest.txt` 只作 legacy 兼容快照）
7. 选择优先级最高且 `passes=false` 的 1 个功能

## 闭环执行契约（严格遵循 Harness Engineering）

## 任务粒度契约

- 一个任务应尽量对应一个完整、可验证、可独立闭环的功能，而不是一个技术步骤。
- 同一功能涉及的 DDL、Mapper/DAO、Service、Controller/API、前端、测试、文档，默认放在同一个任务的 `steps` 内，不拆成多个任务。
- 只有子项可以独立发布、独立验证、独立回滚，且有独立验收标准时，才允许拆成多个任务。
- 如果任务描述无法写出独立验收标准或验证命令，说明粒度太细，应并回所属功能任务。

针对选中的单个 feature，必须按以下严格顺序执行（不得跳步）：
1. **读取任务（read task）**：从单任务 JSON 读取该 feature 的 `description/steps/spec_path/contract_path/qa_report_path`
2. **plan**：生成/更新 `spec_path` 对应规格文件（禁止直接写实现）
3. **build**：基于 spec + contract 实现并自检；所有新增/修改函数、方法必须补齐中文注释
4. **qa gate**：运行 `.harness/scripts/qa_runner.py`，生成 `qa_report_path` 与对应 `.result.json`，按 contract 逐条评分；required 集成门禁和 required Agent Review（如启用）失败会阻塞 `passes=true`
5. **fix**：若单元测试未通过，进入修复循环（最多 3 轮）
6. **mark_pass**：单元测试通过、required QA Gate 通过、required Agent Review（如启用）无 accepted/actionable finding，且 `spec_path` / `contract_path` 文件真实存在后，才可将该 feature `passes=false -> true`

## 会话启动更新检查

每个新会话开始、处理用户请求前，必须先执行：

```bash
python3 .harness/scripts/update_runtime.py --target-dir . --check-remote
```

该命令仍受 `.harness/config/update-policy.json` 的 `check_interval_minutes` 限制，默认 12 小时内不会重复访问远程。脚本不存在、网络失败或检查失败时，只记录原因并继续当前任务，不阻断开发。

## Quick / Fast Track 分流（快速模式）

明确、局部、可验证的改动可先进入快速分流，避免为小修复或中等局部改动生成完整 spec/contract。即使用户没有显式说 quick-fix 或 fast-track，只要是修复、调整、优化、补测试、改校验、改提示或处理报错这类自然语言改动，且没有显式指定 plan/build/qa/sprint，也必须先分类。进入前必须运行：

```bash
python3 .harness/scripts/quick_fix_classifier.py --target-dir . --prompt "<改动描述>"
```

分流结果按以下规则执行：
- `recommended_mode=quick_fix` 且 `confidence=high`：可直接轻量修复。
- `recommended_mode=fast_track` 且 `confidence=high|medium`：可走快速通道完成局部中等改动。
- `recommended_mode=standard_feature` 或 `confidence=low`：必须回到标准闭环。

快速模式的强制边界：
- quick-fix：明确小 bug、小文案、空值保护、日志、错误提示、单测/编译小修；修改不超过 5 个文件，post-diff 变更不超过 200 行。
- fast-track：局部业务逻辑调整、内部校验规则、Mapper/转换逻辑、非公共配置、小型前端交互、测试补齐、局部异常处理；修改不超过 8 个文件，post-diff 变更不超过 400 行。
- 不涉及 DB migration、权限/安全、计费、限流、缓存一致性、事务、幂等、外部 API、公共 DTO 或接口契约。
- 修改后必须运行 `quick_fix_classifier.py --phase post-diff` 复核；一旦出现 risk_flags 或超阈值，立即补 spec/contract 并升级标准流程。
- quick-fix/fast-track 只写进度日志，不允许把 feature `passes` 改成 `true`。

quick-fix 收口命令：

```bash
python3 .harness/scripts/session_close.py \
  --target-dir . \
  --quick-fix \
  --title "<bug 标题>" \
  --outcome pass \
  --note "<修改文件、验证命令和结果>"
```

fast-track 收口命令：

```bash
python3 .harness/scripts/session_close.py \
  --target-dir . \
  --fast-track \
  --title "<改动标题>" \
  --outcome pass \
  --note "<范围、风险判断、验证命令和结果>"
```

日志写入 `.harness/task-harness/progress/YYYY-MM/<timestamp>-quickfix-<slug>.md` 或 `<timestamp>-fasttrack-<slug>.md`。如果快速模式关联已有任务，可追加 `--feature-id <task-id>` 作为引用，但仍不得绕过该任务的 spec/contract/QA Gate 门禁。

## 任务清单修改规则

- 对应单任务 JSON（例如 `.harness/task-harness/tasks/<batch-id>/<display-id>-<title>-<hash>.json`）中仅允许修改：
  - `status: todo|doing|done`
  - `passes: false -> true`（单元测试通过、required QA Gate 通过、required Agent Review 如启用已通过且 spec/contract 已落盘后）
- quick-fix/fast-track 收口不得修改任务定义或 `passes`；若要完成任务，必须回到标准闭环
- 若存在 `.harness/feature_list.json` 或 `.harness/task-harness/features/*.json`，其为 legacy 兼容数据，常规不直接手改
- 禁止修改：
  - `id/category/priority/description/file/spec_path/contract_path/qa_report_path/steps/verification`
- 如需改任务定义，默认不在当前执行流中修改；记录为后续任务或风险，除非用户原始指令已经明确要求调整任务定义

## 会话结束前必须完成

1. 写入进度日志（`.harness/task-harness/progress/YYYY-MM/<timestamp>-<feature-id>.md`）
2. 若该 feature 单元测试通过、required QA Gate 通过、required Agent Review（如启用）通过且 `spec_path` / `contract_path` 文件存在：更新 `passes=true`
3. 运行会话收口脚本：`python3 .harness/scripts/session_close.py --target-dir . --feature-id <task-id> --outcome pass|fail|blocked|in-progress`
4. quick-fix/fast-track 可改用：`python3 .harness/scripts/session_close.py --target-dir . --quick-fix|--fast-track --title "<标题>" --outcome pass --note "<范围、风险判断、验证命令和结果>"`
5. 提交 git commit（建议一个 feature 一个 commit）
6. 输出下一步建议（下一个 feature 或阻塞处理方案）
7. 根据 `.harness/config/task.json` 的 `harness.session_control.mode` 自动执行会话切换：
   - `soft_reset`：不写 session-context 状态文件；继续当前会话时，必须按会话日志和下一任务提示处理下一 feature
   - `hard_new_session`：不写 session-boundary 状态文件；必须由模型按收口输出主动新开会话后再开始下一 feature
8. 自动续跑下一个任务可执行：
   - `python3 .harness/scripts/task_switch.py continue --target-dir .`
   - 该命令会在当前分支自动定位下一个任务并更新状态（不切分支）

## 遇到阻塞时

- 立即停止当前 feature 的继续堆叠开发，先记录阻塞证据
- 若同一 feature 修复 3 轮仍未通过单元测试：保持 `passes=false`，并继续下一个任务
- 在 `.harness/task-harness/progress/YYYY-MM/<timestamp>-<feature-id>.md` 记录：
  - 阻塞现象
  - 已尝试方案
  - 失败原因
  - 建议下一步（缩范围 / 拆子任务 / 人工决策）

## Codex 提示词示例

- `先运行 .harness/scripts/init.sh，然后按 AGENTS.md + .harness/docs/TASK-HARNESS.md 执行下一个 feature`
- `执行 20260508T153012Z-feat-login-rate-limit-a3f9c2：严格按 read task -> plan -> build -> qa gate -> fix -> mark_pass`
- `按 harness 工作流修复指定任务 ID，最多 3 轮；若单测仍失败则继续下一个任务`
- `quick-fix 修复一个明确小 bug，先分类，修完后 quick close`
- `fast-track 做一个局部校验规则调整，先分类，修完后 fast close`

## 项目信息

- 项目：`{{项目名称}}`
- 描述：`{{项目描述，一句话概括目标和范围}}`
