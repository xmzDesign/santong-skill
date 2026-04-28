# 前端三层规范入口

本目录是 `.harness/docs/frontend-dev-conventions.md` 的展开层，用于让 AI 代理在编码时获得更具体的前端约束。

读取顺序：

1. `rules.md`：先读。它是约束层，定义禁止项、token、状态、无障碍、反例。
2. `code-design.md`：需要写代码时读。它给出页面、表格、表单、弹层、状态视图、Agent UI 的标准结构。
3. `ui-design.md`：涉及视觉与页面布局时读。它定义默认产品气质、页面类型参考和视觉验收。
4. `references/byai-ds-v/index.html`：需要对齐视觉效果时再打开。它是 BYAI Design System 的 HTML 参考入口。

使用原则：

- 若任务只改纯逻辑，可只读 `frontend-dev-conventions.md`。
- 若任务涉及 UI 或样式，必须至少读 `rules.md`。
- 若要新增页面或重写组件，必须读 `rules.md` + `code-design.md` + `ui-design.md`。
- 若任务要求“贴近设计稿”“按参考页实现”“视觉差异大”，必须打开 `references/byai-ds-v/index.html` 或对应页面 HTML。
- 若项目已有设计系统，以项目系统为准；本目录作为缺省标准和审查清单。

## BYAI HTML 参考

HTML 参考文件是视觉对齐材料，不是可直接复制到业务代码里的模板。使用方式：

- 先用 `ui-design.md` 确认页面类型，再打开对应 HTML。
- 观察布局密度、层级、token、状态、动线和组件组合。
- 将视觉意图迁移到当前项目的组件库、路由、状态管理和样式体系中。
- 不要照搬 demo 文案、假数据、内联样式或独立页面结构。

入口与常用页面：

| 参考文件 | 用途 |
|---|---|
| `references/byai-ds-v/index.html` | 全部页面 gallery |
| `references/byai-ds-v/readme.html` | 设计系统说明 |
| `references/byai-ds-v/pages/02-dashboard.html` | Cockpit / dashboard 基准 |
| `references/byai-ds-v/pages/03-table.html` | 高密度表格与批量操作 |
| `references/byai-ds-v/pages/04-chat.html` | Agent chat / tool call / citation |
| `references/byai-ds-v/pages/07-agent-studio.html` | Agent 配置工作台 |
| `references/byai-ds-v/packages/ui/showcase.html` | 组件形态速查 |
