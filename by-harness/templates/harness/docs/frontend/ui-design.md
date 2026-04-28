# 前端视觉层

视觉层回答：“页面应该呈现什么气质。”

## 1. 默认设计方向

默认面向 B2B SaaS / AI-native Agent 产品：

- 像 cockpit，不像 landing page。
- 信息密度优先，不用大面积无意义留白。
- 暖调、克制、可信，不追求炫技。
- 数据、操作、状态清晰可扫读。
- Agent 行为透明，可见、可解释、可中断。

五条取舍原则：

1. Clarity over Cleverness：清晰高于聪明。
2. Density as Respect：专业工具尊重用户时间。
3. Agent Transparency：AI 行为必须透明。
4. Keyboard First：高频操作优先键盘。
5. Editorial Warmth：严肃但可读，有温度但不花哨。

当原则冲突时，编号小的优先。

## 2. 页面类型参考

新增页面时先选类型：

| 页面类型 | 适用场景 | 视觉重点 |
|---|---|---|
| Login | 登录、认证、租户选择 | 品牌露出、简洁、安全感 |
| Dashboard | 概览、运营看板 | KPI、趋势、Agent 侧栏、一屏关键信息 |
| Table | 列表、收件箱、任务池 | 高密度筛选、批量操作、行状态 |
| Chat / Agent | Copilot、会话、AI 助手 | streaming、tool call、citation、HITL |
| Settings | 设置、配置、权限 | 分组表单、危险区、保存反馈 |
| Detail | 详情页、客户/订单/线索详情 | 主信息、时间线、侧栏 meta |
| Studio | Agent 配置、规则编辑 | 多区块配置、预览、工具/知识/护栏 |
| Billing | 订阅、用量、账单 | 用量图表、计划、风险提醒 |
| Team | 成员、角色、权限矩阵 | 表格、权限对照、邀请流 |
| Audit Log | 审计、日志、合规 | 可追溯、差异、导出 |
| Integrations | 连接器市场/API | 卡片网格、连接状态、配置入口 |
| Onboarding | 首次使用、引导 | checklist、下一步、低阻力开始 |

对应 HTML 参考位于 `references/byai-ds-v/pages/`：

| 页面类型 | 参考文件 |
|---|---|
| Login | `01-login.html` |
| Dashboard | `02-dashboard.html` |
| Table | `03-table.html` |
| Chat / Agent | `04-chat.html` |
| Settings | `05-settings.html` |
| Detail | `06-lead-detail.html` |
| Studio | `07-agent-studio.html` |
| Billing | `08-billing.html` |
| Team | `09-team.html` |
| Audit Log | `10-audit-log.html` |
| Integrations | `11-integrations.html` |
| Onboarding | `12-onboarding.html` |

参考方式：优先抽取页面骨架、信息密度、层级关系、状态表达与 token 用法；不要把 HTML demo 当成业务组件源码直接复制。

## 3. 布局基线

默认 App Shell：

```text
TopBar 48px
Left Nav 240px / collapsed 56px
Main flex
Agent Copilot 380px / hidden / expanded 560px
StatusBar 28px optional
```

常用布局：

- Dashboard：4 KPI + 主图表 + 右侧/底部动态。
- Table：Header + Toolbar + Table + Pagination。
- Settings：左侧分组导航 + 右侧表单内容。
- Detail：主内容 8 栏 + 侧边信息 4 栏。
- Agent：消息主区 + 工具/来源/上下文辅助区。

响应式：

- 1440x900 为设计基准。
- 1280 以下优先折叠 Agent。
- 1024 以下折叠左侧导航。
- 768 以下单栏，表格可横滚但必须显式容器化。

## 4. 色彩与字体气质

默认颜色方向：

- Canvas：暖灰 / 米白。
- Surface：白或轻微暖白。
- Primary：深琥珀 / 橙色。
- Info：深蓝。
- Warning：黄。
- Danger：红，但只用于危险。
- Agent：紫色只用于 Agent 行为标识。

字体方向：

- 中文优先清晰无衬线，如 Microsoft YaHei / PingFang SC。
- 英文 UI 用清晰 sans。
- 标题可少量 editorial display，但中文不使用小字号衬线。
- 数字使用 tabular numbers，金额、百分比、时长必须有单位。

## 5. 密度规则

默认 comfortable：

| 元素 | 默认 |
|---|---|
| Table row | 36px |
| Button md | 32-40px，按项目组件库对齐 |
| Input md | 32-40px，按项目组件库对齐 |
| Card padding | 16-24px |
| Nav item | 32px |

禁止：

- 业务后台首屏 70% 是大标题和装饰。
- 表格行高默认 56px。
- 列表关键元数据藏在 tooltip 里。

## 6. 文案规则

- 按钮是动作，不是标签：用“保存配置”“删除客户”“导出 CSV”，不要用“OK”“Submit”“Confirm”。
- 错误文案包含：发生了什么、为什么、用户能做什么。
- Empty 文案包含：当前状态、原因或下一步。
- 删除确认按钮复述对象：`删除客户`，不要只写 `Yes`。
- Agent 文案专业、直接、可解释，不使用“我只是 AI”式免责声明。

## 7. Data Viz

- 二系列对比优先 amber + blue。
- 多系列最多 6 色，超过改 small multiples 或 table。
- 图例需要符号/纹理/文字，不只靠色块。
- 禁止 3D 图。
- 双 Y 轴谨慎，能拆成两个图就拆。
- 默认显示关键数值，不强迫 hover 才能理解。

## 8. 视觉验收清单

完成 UI 任务前，至少检查：

- 页面第一屏是否直接呈现业务核心，而不是宣传页。
- 标题、工具栏、主要内容、状态反馈是否有清晰层级。
- 是否只出现一个主要 CTA。
- 文本是否在桌面和窄屏都不溢出、不重叠。
- 表格是否可扫读，列宽是否符合信息类型。
- 图表是否有标题、口径、时间范围、图例。
- loading / empty / error 是否和真实布局匹配。
- Agent 行为是否可见、可解释、可中断、可追溯。
- 是否避免紫色渐变、玻璃拟态、装饰 orb、重阴影、卡片套卡片。
