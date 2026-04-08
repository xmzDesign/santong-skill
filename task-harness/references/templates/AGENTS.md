# {{项目名称}} - Task Harness 执行规则

本项目使用 Task Harness 进行多会话任务管理。请把本文件当作 Codex 的执行契约。

## 会话启动（必须按顺序）

1. 运行 `bash init.sh`
2. 阅读 `progress.txt`
3. 阅读 `feature_list.json`
4. 选择优先级最高且 `passes=false` 的 1 个功能

## 执行契约

- 严格按该功能的 `steps` 执行，不额外扩展范围
- 完成后必须实际验证（运行命令、检查页面、或核对输出）
- 只有在验证通过后，才把该功能 `passes` 设为 `true`
- 在 `feature_list.json` 中只允许修改 `passes` 字段
- 每完成 1 个功能，必须提交一次 git commit，并推送到远程
- 会话结束前必须追加 `progress.txt`

## 每次会话的标准输出

1. 本次完成的功能 ID
2. 验证方式与结果
3. git commit 摘要（hash + message）
4. 当前进度（已完成/总数）
5. 下一个待做功能

## 遇到阻塞时

- 立即停止，不要偷偷切换到其他功能
- 在 `progress.txt` 记录：
  - 阻塞现象
  - 已尝试方案
  - 失败原因
  - 建议下一步

## Codex 提示词示例

- `按 AGENTS.md + feature_list.json 执行下一个未完成功能`
- `先运行 init.sh，然后只完成一个最高优先级功能`
- `完成 feat-03，并按规则更新 passes 和 progress.txt`

## 项目信息

- 项目：`{{项目名称}}`
- 描述：`{{项目描述，一句话概括目标和范围}}`
