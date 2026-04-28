# 前端示范层

示范层回答：“标准代码应该长什么样。”

## 1. 页面结构

简单页面：

```text
pages/<feature>/
  index.tsx
  style.module.scss
```

复杂页面：

```text
pages/<feature>/
  index.tsx
  view.tsx
  hooks/use-<feature>-controller.ts
  components/
  config/
  utils.ts
  types.ts
  style.module.scss
```

约束：

- `index.tsx` 负责路由入口和组合。
- `use-*-controller.ts` 负责请求、状态、派生数据、事件处理、副作用。
- `view.tsx` 负责纯展示，不直接请求接口。
- 私有组件放在当前页面 `components/`。
- 可复用组件才上升到全局 `components/`。

## 2. Controller / View 模式

推荐：

```tsx
export function LeadListPage() {
  const controller = useLeadListController();
  return <LeadListView {...controller} />;
}
```

Controller 输出应包含：

- `data`
- `loading`
- `error`
- `filters`
- `pagination`
- `selectedRowKeys`
- `handlers`

View 只消费 props，不直接调用 service。

## 3. 列表页模板

列表页默认结构：

```text
PageShell
  PageHeader
    title / subtitle / breadcrumb
    primary action（最多一个）
  FilterToolbar
    search / filters / date range / reset
  TablePanel
    batch action bar
    data table
    pagination
  StateLayer
    loading / empty / error
```

实现要求：

- 搜索输入防抖。
- 筛选变化后重置页码。
- 批量操作后刷新列表，并处理选中态。
- 表格列宽按内容类型设计：名称列宽、数字列窄、操作列自适应。
- 表格 loading 用 skeleton 或表格内 loading，不要整页白屏。

## 4. 表单弹层模板

Modal / Drawer 表单默认结构：

```text
Modal or Drawer
  Header: 动作对象 + 简短说明
  Form
    Field group
    Inline errors
  Footer
    Cancel
    Primary action with loading
```

要求：

- 所有字段有 label。
- 必填项有明显标识。
- 错误就近展示。
- 提交中按钮 loading + disabled。
- 关闭前处理未保存内容。
- 破坏性操作使用二次确认，确认按钮文案复述动作和对象。

## 5. 状态视图模板

Loading：

- 短请求可用局部 spinner。
- 首屏和表格用 skeleton。
- 超过 10 秒的任务展示进度、阶段或可取消入口。

Empty：

```text
标题：说明当前为什么为空
说明：给出原因或下一步
动作：创建 / 清空筛选 / 返回上级
```

Error：

```text
标题：发生了什么
说明：为什么失败或如何处理
动作：重试 / 联系管理员 / 返回
```

## 6. Antd 覆盖范式

CSS Modules 中覆盖 Antd：

```scss
.root {
  :global(.ant-btn-primary) {
    background: var(--intent-primary-bg);
    border-color: var(--intent-primary-border);
  }
}
```

不要：

```scss
.ant-btn-primary {
  background: #ff6b00 !important;
}
```

## 7. 图表卡片模板

图表默认放在标准 panel 中：

```text
ChartPanel
  Header
    title
    subtitle: 时间范围 / 更新时间 / 数据口径
    actions: segmented control / export
  Body
    chart
  Legend
    swatch + label + value
```

要求：

- 图例不能只靠颜色；需要文字、符号或纹理。
- 多系列最多 6 种颜色，超过改 small multiples 或 table。
- 禁止 3D 图。
- Pie chart 最多 3 片，超过改 bar。
- 财务涨跌不用绿涨红跌，使用 amber/blue + 上下箭头 + 文字。

## 8. Agent Copilot 模板

Agent 侧栏默认结构：

```text
AgentPanel
  Header: agent name / status / close
  Timeline or Messages
    user message
    agent message
    tool call card
    reasoning trace
    citation
  Composer
    multiline input
    attachments/tools/context
    send by Cmd/Ctrl+Enter
```

要求：

- Agent 消息和用户消息视觉区分。
- Tool call 展示工具名、参数摘要、状态、结果摘要。
- Streaming 时显示停止按钮。
- 涉及外部影响的动作进入 HITL approval。
- 每条关键结论尽可能给 source/citation。

## 9. 注释要求

新增/修改函数、方法必须中文注释，至少包含：

- 用途。
- 关键参数。
- 返回值。
- 副作用，如请求、状态变更、localStorage、事件总线。

示例：

```ts
/**
 * 加载线索列表，并保证只有最后一次请求结果会写入页面状态。
 * @param nextFilters 下一次查询条件。
 * @returns Promise<void>
 * @sideEffect 更新 loading、列表数据、分页和错误状态。
 */
async function loadLeadList(nextFilters: LeadFilters): Promise<void> {
  // ...
}
```

## 10. 自检输出

前端交付报告必须包含：

- 读了哪些前端规范文件。
- 本次选择的页面/组件模式。
- 适用的 token / 视觉约束。
- 状态覆盖情况。
- 构建、测试、截图或无法执行原因。
- 若有例外，说明原因和回收计划。
