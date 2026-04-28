# 03 · Design Tokens — Semantic
> 语义层 Token · 意图映射 · **组件唯一可引用的 token 层**

---

## 为什么分两层？

- **Primitive** 只回答"这是什么颜色/尺寸"（物理属性）
- **Semantic** 回答"这个东西在产品里代表什么意思"（意图）

组件应该说 `background: var(--bg-canvas)`，而不是 `background: #FAFAF7` 或 `color.warm-grey.50`。
这样未来切换 dark mode，或者品牌色微调，**只需改一处**——改 semantic 的定义，不改组件。

---

## 1. Background（背景）

| Token | 映射 Primitive (Light) | 用途 |
|---|---|---|
| `bg.canvas` | `warm-grey.50` (#FAFAF7) | 页面最底层背景 |
| `bg.surface` | `#FFFFFF` | 一级面板 / Card |
| `bg.surface.raised` | `#FFFFFF` + `shadow.sm` | 悬浮面板 / Popover |
| `bg.surface.sunken` | `warm-grey.100` (#F4F2ED) | 凹陷区域 / Input 背景 |
| `bg.surface.subtle` | `warm-grey.50` (#FAFAF7) | 非强调区域 |
| `bg.hover` | `warm-grey.100` (#F4F2ED) | 可交互元素 hover |
| `bg.active` | `warm-grey.200` (#E8E4DB) | 可交互元素 pressed |
| `bg.selected` | `amber.50` (#FDF8EE) | 选中行 / 标签 |
| `bg.selected.strong` | `amber.100` (#FAEBCA) | 强选中 |
| `bg.disabled` | `warm-grey.100` (#F4F2ED) | 禁用元素 |
| `bg.overlay` | `rgba(26, 24, 20, 0.48)` | Modal backdrop |
| `bg.scrim` | `rgba(26, 24, 20, 0.08)` | 轻遮罩 |
| `bg.inverse` | `warm-grey.900` (#1A1814) | 反色区域 / Tooltip |

### Agent 专用背景

| Token | 映射 | 用途 |
|---|---|---|
| `bg.agent.surface` | `violet.50` (#F5F2FA) | Agent 消息气泡底色 |
| `bg.agent.trace` | `violet.100` (#E4DDF2) | Reasoning trace 折叠区底 |
| `bg.agent.highlight` | `violet.50` with 1px `violet.400` border | Agent 高亮引用 |

---

## 2. Foreground（前景 / 文字 / 图标）

| Token | 映射 Primitive | 用途 |
|---|---|---|
| `fg.default` | `warm-grey.800` (#2A2620) | **正文默认 ✨** |
| `fg.strong` | `warm-grey.900` (#1A1814) | 加粗 / Display |
| `fg.muted` | `warm-grey.600` (#5C564B) | 次级信息 / 说明 |
| `fg.subtle` | `warm-grey.500` (#7A7366) | 辅助信息 / placeholder |
| `fg.disabled` | `warm-grey.400` (#A8A093) | 禁用文字 |
| `fg.on-primary` | `#FFFFFF` | Primary CTA 文字 |
| `fg.on-danger` | `#FFFFFF` | Destructive CTA 文字 |
| `fg.on-inverse` | `warm-grey.50` (#FAFAF7) | 反色区域文字 |
| `fg.link` | `blue.600` (#1E5189) | 链接默认 |
| `fg.link.hover` | `blue.700` (#153E6B) | 链接 hover |
| `fg.brand` | `amber.600` (#A36E10) | 品牌强调文字 |
| `fg.agent` | `violet.600` (#5A3F94) | Agent 署名 · 区别于人类 |

---

## 3. Border（边框）

| Token | 映射 | 用途 |
|---|---|---|
| `border.subtle` | `warm-grey.200` (#E8E4DB) | 极弱分割 |
| `border.default` | `warm-grey.300` (#D4CEC1) | **默认 ✨** |
| `border.strong` | `warm-grey.400` (#A8A093) | 强调边框 / Hover |
| `border.inverse` | `warm-grey.900` (#1A1814) | 反色边框 |
| `border.focus` | `amber.600` (#A36E10) | Focus ring 外边 |
| `border.selected` | `amber.600` (#A36E10) | 选中态 |
| `border.danger` | `red.600` (#8F2E14) | 错误态输入框 |
| `border.agent` | `violet.400` (#7A5DB0) | Agent 高亮卡片边框 |

---

## 4. Intent Colors（意图色·状态系统）

### 4.1 Primary / Brand (Amber)

| Token | 映射 | 用途 |
|---|---|---|
| `intent.primary.bg` | `amber.600` (#A36E10) | Primary CTA 背景 |
| `intent.primary.bg.hover` | `amber.700` (#7E560D) | Hover |
| `intent.primary.bg.active` | `amber.800` (#5E400B) | Pressed |
| `intent.primary.fg` | `#FFFFFF` | CTA 文字 |
| `intent.primary.border` | `amber.700` (#7E560D) | CTA 边框（幽灵按钮） |
| `intent.primary.surface` | `amber.50` (#FDF8EE) | Tint 背景 |
| `intent.primary.surface.hover` | `amber.100` (#FAEBCA) | Tint hover |
| `intent.primary.text-on-surface` | `amber.800` (#5E400B) | Tint 上的文字 |

### 4.2 Positive（正向结果·也映射 Amber·因为 Amber 是我们的"正轴"）

**色觉差异友好说明**：由于用户红绿色弱，我们**不把绿色用作"正向"**。而是把**Amber 作为正向轴**，
与 **Blue 信息轴**构成安全对比。成功状态必须带 ✓ 图标。

| Token | 映射 |
|---|---|
| `intent.positive.bg` | `amber.600` |
| `intent.positive.fg` | `#FFFFFF` |
| `intent.positive.surface` | `amber.50` |
| `intent.positive.text` | `amber.800` |
| `intent.positive.icon` | `amber.600` |

### 4.3 Info（信息·Blue）

| Token | 映射 |
|---|---|
| `intent.info.bg` | `blue.600` (#1E5189) |
| `intent.info.fg` | `#FFFFFF` |
| `intent.info.surface` | `blue.50` (#EEF4FA) |
| `intent.info.text` | `blue.800` (#0F2D4E) |
| `intent.info.icon` | `blue.600` |
| `intent.info.border` | `blue.200` (#A9C6E6) |

### 4.4 Warning（警告·Yellow）

| Token | 映射 |
|---|---|
| `intent.warning.bg` | `yellow.500` (#D69E08) |
| `intent.warning.fg` | `warm-grey.900` (#1A1814) |
| `intent.warning.surface` | `yellow.50` (#FEF9E4) |
| `intent.warning.text` | `yellow.700` (#8A6402) |
| `intent.warning.icon` | `yellow.500` |

### 4.5 Danger（危险·Red·唯一红色用法）

**硬规**：任何使用 danger 色的元素必须伴随 ⚠ / ✕ / 🗑 等图标 + 明确文字。

| Token | 映射 |
|---|---|
| `intent.danger.bg` | `red.600` (#8F2E14) |
| `intent.danger.bg.hover` | `red.700` (#6F220E) |
| `intent.danger.fg` | `#FFFFFF` |
| `intent.danger.surface` | `red.50` (#FCF1ED) |
| `intent.danger.text` | `red.800` (#4F1809) |
| `intent.danger.icon` | `red.600` |
| `intent.danger.border` | `red.200` (#EDB39F) |

### 4.6 Neutral（中性·用于"无特殊状态"的标签、按钮）

| Token | 映射 |
|---|---|
| `intent.neutral.bg` | `warm-grey.100` (#F4F2ED) |
| `intent.neutral.fg` | `warm-grey.700` (#3F3A32) |
| `intent.neutral.border` | `warm-grey.300` (#D4CEC1) |

---

## 5. Agent-Specific Semantic Tokens（★ Agent 产品独有）

| Token | 映射 | 用途 |
|---|---|---|
| `agent.bg.message` | `violet.50` | Agent 气泡背景 |
| `agent.bg.trace` | `violet.100` | 思考过程展开区 |
| `agent.fg.primary` | `violet.600` | Agent 署名 / 标识 |
| `agent.fg.secondary` | `violet.400` | Agent metadata |
| `agent.border.default` | `violet.200` (#C4B6DE 通过 alpha 生成) | Agent 卡片边框 |
| `agent.indicator.streaming` | `amber.500` (#C88A1A) | 流式指示光标 |
| `agent.indicator.thinking` | `violet.400` | 思考中呼吸光 |
| `agent.indicator.tool` | `blue.500` (#2A69A8) | 工具调用指示 |
| `agent.indicator.error` | `red.500` (#B03E1E) | Agent 出错 |
| `agent.citation.bg` | `warm-grey.100` | Citation hover 背景 |
| `agent.citation.border` | `warm-grey.300` | Citation 左侧引注条 |

---

## 6. Data Viz Semantic Tokens（图表）

**配色铁律**（色觉差异友好）：

- 二系列对比 → `dataviz.series.primary` (Amber) + `dataviz.series.secondary` (Blue)
- 多系列 → 增加 Teal, Violet, Warm-grey
- **禁止使用**"绿涨红跌"做财务涨跌（即便金融行业）。改用 **Amber 涨 / Blue 跌** 或 `↑ +12%` / `↓ -8%` 文字前缀

### 6.1 分类色（最多 6 系列）

| Token | 映射 |
|---|---|
| `dataviz.cat.1` | `amber.600` (#A36E10) |
| `dataviz.cat.2` | `blue.600` (#1E5189) |
| `dataviz.cat.3` | `teal.600` (#1B6F62) |
| `dataviz.cat.4` | `violet.600` (#5A3F94) |
| `dataviz.cat.5` | `warm-grey.600` (#5C564B) |
| `dataviz.cat.6` | `yellow.700` (#8A6402) |

### 6.2 渐变 / 热力（单系列强度）

| Token | 映射（低 → 高） |
|---|---|
| `dataviz.sequential.amber.0` | `amber.50` |
| `dataviz.sequential.amber.1` | `amber.200` |
| `dataviz.sequential.amber.2` | `amber.400` |
| `dataviz.sequential.amber.3` | `amber.600` |
| `dataviz.sequential.amber.4` | `amber.800` |

### 6.3 双向发散（如盈亏、好坏）

| Token | 映射 |
|---|---|
| `dataviz.diverging.negative` | `blue.600` |
| `dataviz.diverging.neutral` | `warm-grey.200` |
| `dataviz.diverging.positive` | `amber.600` |

### 6.4 辅助元素

| Token | 映射 |
|---|---|
| `dataviz.grid` | `warm-grey.200` (#E8E4DB) |
| `dataviz.axis` | `warm-grey.400` (#A8A093) |
| `dataviz.label` | `warm-grey.600` (#5C564B) |
| `dataviz.tooltip.bg` | `warm-grey.900` (#1A1814) |
| `dataviz.tooltip.fg` | `warm-grey.50` (#FAFAF7) |

---

## 7. 组件特化语义（可选第三层）

某些组件有稳定特化需求，可在此层声明。如：

| Token | 映射 |
|---|---|
| `component.button.height.sm` | 28px |
| `component.button.height.md` | 32px |
| `component.button.height.lg` | 40px |
| `component.input.height.sm` | 28px |
| `component.input.height.md` | 32px |
| `component.input.height.lg` | 40px |
| `component.table.row.compact` | 28px |
| `component.table.row.comfortable` | 36px |
| `component.table.row.spacious` | 44px |

---

## 8. Dark Mode 预留映射（本期不展开·仅声明契约）

Dark mode 时，**语义 token 名不变**，只是对应的 primitive 切换：

```
Light:  bg.canvas       → warm-grey.50
Dark:   bg.canvas       → warm-grey.950

Light:  fg.default      → warm-grey.800
Dark:   fg.default      → warm-grey.100
```

这意味着**所有组件代码无需改动**即可支持 dark mode。本期只需保证所有组件严格使用语义 token。

---

## 9. 获取语义 token 的正确姿势

### CSS
```css
.card {
  background: var(--bg-surface);
  color: var(--fg-default);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--space-6);
}
```

### Tailwind (v4 custom config)
```html
<div class="bg-surface text-fg-default border border-default rounded-lg shadow-sm p-6">
</div>
```

### React + CSS-in-JS
```jsx
<Card sx={{
  bg: 'bg.surface',
  color: 'fg.default',
  borderColor: 'border.default',
}} />
```

---

**违反例（AI 常犯）**：

```css
/* ❌ 直接引用 primitive */
.card { background: var(--color-warm-grey-50); }

/* ❌ hex 字面值 */
.card { background: #FAFAF7; }

/* ❌ 任意色值 */
.card { background: #FDFDFD; }

/* ✅ 正确 */
.card { background: var(--bg-surface); }
```
