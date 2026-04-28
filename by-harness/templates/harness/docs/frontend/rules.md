# 前端约束层

约束层回答：“AI 不能做什么，必须怎样做。”

## 1. 设计系统优先级

1. 用户当前明确要求。
2. 当前仓库已有设计系统、主题 token、组件库。
3. `.harness/docs/frontend-dev-conventions.md` 与本目录规则。
4. 通用前端经验。

如果项目没有明确设计系统，使用本文件内置的 BYAI 风格默认值。

## 2. Token 纪律

业务代码必须引用 semantic token 或项目已有主题变量，不能直接散落 primitive 值。

禁止：

```css
.button {
  background: #ff6b00;
  padding: 13px 18px;
  border-radius: 5px;
}
```

推荐：

```css
.button {
  background: var(--intent-primary-bg);
  color: var(--intent-primary-fg);
  padding: 0 var(--space-3);
  border-radius: var(--radius-md);
}
```

规则：

- 颜色必须来自语义 token：`bg.*`、`fg.*`、`border.*`、`intent.*`、`agent.*`、`dataviz.*`。
- 间距必须来自 spacing token 或项目既有 spacing 变量。
- 圆角必须来自 radius token。
- 字号必须来自项目字阶或本文建议字阶。
- 动效必须来自 motion token 或项目统一变量。
- token 文件、主题映射文件可以定义 hex；业务样式不可以。

## 3. 默认视觉基线

默认服务对象是 B2B SaaS / AI-native Agent 产品。

- 背景使用暖调 off-white，不使用纯白 + 纯黑的硬对比。
- 主色使用 amber/orange 方向；信息色使用 blue。
- 正向状态不要依赖绿色；使用 amber + 图标 + 文案。
- Danger 只用于危险/破坏性操作，必须有图标和明确动作文字。
- Agent 专属视觉应与人类操作区分，可使用 violet/agent token，但不能滥用为品牌色。
- 默认密度为 comfortable；表格默认行高约 36px，不使用 56px 大行高。

## 4. 禁止的视觉反例

以下模式默认禁止：

- 紫色渐变 + 磨玻璃作为 AI 产品默认风格。
- 大面积 hero、宣传页式首屏、装饰插画占据业务页面关键空间。
- Card 套 Card，浮层套浮层，阴影层层叠加。
- 所有按钮都是 primary。
- 表格所有列平均分宽度。
- Input 只有 placeholder，没有 label。
- Tooltip 内放链接或按钮。
- Modal 嵌套 Modal。
- Enter 单击发送多行 Agent prompt；应使用 Cmd/Ctrl+Enter 发送。
- Loading 白屏，没有 skeleton 或结构占位。
- Empty state 只有“暂无数据”，没有下一步动作或原因。

## 5. 状态覆盖

所有可交互控件必须覆盖：

- default
- hover
- active
- focus-visible
- disabled

所有请求链路必须覆盖：

- loading
- empty
- error
- retry（关键链路）
- success feedback（保存/删除/更新/切换）

## 6. 可访问性

- 文本对比度达到 WCAG 2.2 AA。
- 所有可交互元素可键盘访问。
- Focus ring 清晰可见，不被 sticky header 或浮层遮挡。
- Icon-only button 必须有 `aria-label`。
- 颜色不能作为唯一信息编码。
- 表单 label 与 input 必须关联。
- 字段错误必须就近展示，并用 `role="alert"` 或项目等价能力宣告。
- Modal/Drawer 打开后焦点进入弹层；关闭后焦点回到触发器。
- 支持 `prefers-reduced-motion`。

## 7. 样式代码约束

- 业务页面样式优先使用项目既有方式：CSS Modules、Less、SCSS、styled-components。
- 禁止新增裸全局样式污染。
- 覆盖第三方组件时必须局部化。
- 禁止滥用 `!important`；只有兼容第三方不可控样式时可例外，并说明原因。
- 禁止无解释的 inline style；动态尺寸、虚拟列表、图表坐标可例外。
- 禁止在页面层重复定义 token 常量。

## 8. Antd 规则

- 基础控件优先使用 Antd 或项目已有基础组件。
- Antd 样式覆盖必须收敛在模块根类下。
- Primary CTA 每页最多一个主要动作。
- Danger 按钮必须使用 danger 语义，不要把 primary 染红。
- Modal/Drawer 表单关闭前必须处理未保存提醒。

## 9. Agent UI 规则

凡涉及 AI/Agent：

- Agent 调用工具、读写数据、外部请求必须可见。
- Agent 决策应展示可折叠 reasoning trace 或操作依据。
- 不可逆或外部影响操作必须 HITL 二次确认。
- Streaming 必须可中断。
- 输出结论必须尽可能有 citation/source。
- Agent 视觉与人类消息区分，但不使用拟人化头像作为默认方案。

## 10. 提交前检查

前端变更完成前，至少检查：

- 无新增硬编码品牌/语义色。
- 无新增无解释 inline style。
- 无新增裸全局覆盖。
- 交互 5 态完整。
- loading / empty / error 覆盖完整。
- 键盘与 focus 可用。
- 桌面和窄屏没有文本溢出或重叠。
- 若涉及 Agent，工具调用、来源、停止入口、HITL 已覆盖。
