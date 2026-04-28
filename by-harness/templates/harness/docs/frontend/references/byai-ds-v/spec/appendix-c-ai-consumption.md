# Appendix C · AI Consumption ★
> 把本规范喂给 AI 的正确姿势 · Prompt 模板 · Few-shot examples

---

## 0. 为什么有这个附录？

Design System 的传统受众是**人类设计师和工程师**。
BYAI v1 的受众包括**AI Agent**——它可能是 Claude、GPT-4o、Cursor、v0、Bolt，或任何未来的 Coding AI。

AI 消费 spec 的特点与人不同：
- **容易跳过长篇幅章节** → 需要结构化、重点前置
- **喜欢即时对照示例** → 需要 few-shot
- **会幻觉 token 名** → 需要明确禁令清单
- **容易做出风格偏移** → 需要铁规执行

本附录就是解决这些问题。

---

## 1. 三种喂 Spec 的策略

### Strategy A · Full Dump（全量喂入）

**适用**：首次会话、任务复杂、模型上下文容量大（Claude Opus / GPT-4 Turbo）

把以下全部拼接为 system prompt：

```
[README.md]
[spec/01-philosophy.md]
...
[spec/10-voice-microcopy.md]
[spec/appendix-a ~ d]
[tokens/tokens.json]
```

**预估 token 量**：~60–80K。Claude Opus / GPT-4o 轻松消化。

### Strategy B · Progressive Loading（按需加载）★ 推荐

**适用**：多轮对话、任务具体、节省 token

**第一轮 system prompt**：

```
[README.md]
[spec/01-philosophy.md]
[tokens/tokens.json]
[spec/appendix-c-ai-consumption.md]  ← 本文件
```

每当 AI 需要具体模块，引导它 fetch：

```
User: 画一个 Dashboard 顶部的 4 张 KPI 卡。
AI:   [读入 06-components.md 关于 Stat card 的章节]
      [读入 09-data-viz.md 关于 KPI 规范的章节]
      [生成代码]
```

### Strategy C · Ground Truth First（视觉范本优先）

**适用**：追求视觉像素级一致

**第一轮**：直接把 `/pages/02-dashboard.html`（或其他基线页）作为范本喂入。

AI 会**照猫画虎**，一致性最高。Spec 文档作为补充。

---

## 2. Prompt 模板（可直接复用）

### 2.1 System Prompt（固定部分）

```
You are implementing UI for a B2B SaaS AI-native product following the BYAI Design System v1.

## Hard rules (never violate)

1. ONLY use semantic tokens (bg.*, fg.*, intent.*, agent.*, etc.) in component code.
   NEVER use primitive tokens (color.amber.600) or hex literals (#A36E10) directly.

2. ALL spacing must come from space.* tokens (4px grid). No arbitrary pixel values.

3. ALL radii from radius.* tokens. Default is radius.md (6px).

4. Typography: 9-level scale only. No other font sizes.

5. Binary states (up/down, success/warning, active/inactive) must use amber/blue,
   NEVER red/green. The user has red-green color weakness.

6. Every interactive element must cover 5 states:
   default, hover, active, focus-visible, disabled.

7. Agent actions use violet.* semantic tokens; human actions do not.

8. Red is reserved for danger/destructive and MUST be paired with ⚠ / ✕ icon + text.

9. Send shortcut is Cmd+Enter (not Enter alone).

10. Chinese text uses 'Microsoft YaHei' / 微软雅黑, never serif.

## Tenets (for design tradeoffs)

1. Clarity over Cleverness
2. Density as Respect
3. Agent Transparency
4. Keyboard First
5. Editorial Warmth

When in doubt, choose the option that better serves the tenet with lower number.

## Output format

- Use semantic HTML5 + CSS custom properties (CSS variables)
- Add aria-* attributes for accessibility
- Include all 5 interaction states
- Comment any non-obvious tenet-driven decisions, e.g.
  /* Tenet 2: Density — compact row for high info ratio */

You have access to the following token files: [attach tokens.json or tokens.css]
```

### 2.2 Task Prompt 模板

**模板 · 画具象组件**：

```
Implement a <组件名> following BYAI Design System v1.

Context:
- This goes in [哪个页面 / 哪个位置]
- Purpose: [解决什么问题]
- Data shape: [字段 / 类型]

Required states: [default / hover / loading / empty / error]
Density: [compact / comfortable / spacious]
Language: [zh-CN / en]

Output: single HTML file using CSS variables from tokens.css.
```

**模板 · 画完整页面**：

```
Design a [页面用途] page following BYAI Design System v1.

Page structure:
- TopBar with [...]
- Left nav: [...]
- Main content:
  - Section 1: [...]
  - Section 2: [...]
- Agent Copilot: [shown / hidden by default]

Reference pages:
- /pages/02-dashboard.html (for KPI card layout)
- /pages/03-table.html (for data table)

Output: single HTML file with <head>, <body>, and embedded <style>.
```

---

## 3. Few-Shot Examples（few-shot 学习范例）

**BYAI 风格的"对"vs"错"对比对 AI 最有效**。以下是可放入 prompt 的典型范例。

### 3.1 Button 范例

```html
<!-- ❌ Wrong: 直接 hex、间距错、状态不全、冷色调 -->
<button style="background:#4F46E5; padding:10px 18px; border-radius:4px">
  Submit
</button>

<!-- ✅ Right: 语义 token、space grid、完整状态、暖调 -->
<button class="btn btn-primary">
  Save changes
</button>
<style>
.btn-primary {
  background: var(--intent-primary-bg);
  color: var(--intent-primary-fg);
  padding: 0 var(--space-3);
  height: 32px;
  border-radius: var(--radius-md);
  transition: background var(--motion-duration-fast) var(--motion-ease-out);
}
.btn-primary:hover:not(:disabled)  { background: var(--intent-primary-bg-hover); }
.btn-primary:active:not(:disabled) { background: var(--intent-primary-bg-active); }
.btn-primary:focus-visible         { outline: none; box-shadow: var(--shadow-focus-ring); }
.btn-primary:disabled              { opacity: 0.5; cursor: not-allowed; }
</style>
```

### 3.2 KPI Card 范例

```html
<!-- ❌ Wrong: 裸数字、色觉不友好、硬编码 -->
<div class="card">
  <div>Revenue</div>
  <div style="font-size:40px; color:#22C55E">
    1245800
    <span style="color:red">↓ 12%</span>
  </div>
</div>

<!-- ✅ Right: 有单位、amber 正向、tabular-nums、带对比说明 -->
<div class="stat-card">
  <div class="stat-label">Total revenue</div>
  <div class="stat-value">¥1,245,800</div>
  <div class="stat-delta" data-trend="up">
    <span>↑ 12.3%</span>
    <span class="stat-delta-comparison">vs. last month</span>
  </div>
</div>
```

### 3.3 Agent Message 范例

```html
<!-- ❌ Wrong: 和人类消息无区分、缺 avatar、缺 citation、缺 actions -->
<div class="message">
  Revenue grew 12.3% YoY.
</div>

<!-- ✅ Right: violet bg 区分、avatar + 名称、citation chip、meta actions -->
<div class="message message-agent">
  <div class="message-header">
    <span class="avatar avatar-agent">✨</span>
    <span class="agent-name">BYAI Copilot</span>
  </div>
  <div class="message-bubble">
    <p>Revenue grew <strong>12.3%</strong> YoY
      <button class="citation-chip">1</button>,
      driven by Enterprise
      <button class="citation-chip">2</button>.
    </p>
  </div>
  <div class="message-meta">
    <time>14:33</time>
    <span>8.2s · 234 tokens</span>
    <button class="btn-ghost btn-xs">Copy</button>
    <button class="btn-ghost btn-xs">↻ Regenerate</button>
  </div>
</div>
```

### 3.4 Tool Call 范例

```html
<!-- ❌ Wrong: Agent 直接给结论，无 tool call 可见性 -->
<p>I found 1,234 enterprise customers with overdue payments.</p>

<!-- ✅ Right: 显式展示 tool call 过程 -->
<div class="tool-call">
  <div class="tool-call-header">
    <span class="tool-call-name">query_database</span>
    <span class="tool-call-status" data-state="success">✓ 240ms</span>
  </div>
  <div class="tool-call-body">
    <div class="tool-call-section-label">Input</div>
    <pre>{ "filter": "segment=Enterprise AND overdue=true" }</pre>
    <div class="tool-call-section-label">Output</div>
    <div>Returned 1,234 rows</div>
  </div>
</div>
<p>I found 1,234 enterprise customers with overdue payments.</p>
```

---

## 4. Forbidden List（明令禁止清单）

喂给 AI 的 prompt 可以直接加入此段作为 "Never do:"：

```
NEVER:
- Use hex colors directly (e.g., #FAFAF7) — use var(--bg-canvas)
- Use hardcoded pixel values for spacing not on the 4px grid
- Use Red/Green to encode up/down, success/warning, active/inactive
- Use 'bold' or 'italic' on body text without reason
- Use purple gradients on white backgrounds ("generic AI look")
- Center-align body text paragraphs
- Use Inter, Roboto, or system-ui for Chinese — always Microsoft YaHei
- Use 'Enter' alone to send in composer — use Cmd+Enter
- Create modals without Esc close, focus trap, and backdrop
- Generate emoji-heavy copy ("🎉 Yay!")
- Center text inside buttons without a verb ("OK", "Submit", "Confirm")
- Skip empty/error/loading states in a design
- Use <div> when a semantic element (<nav>, <header>, <main>, <aside>) exists
- Forget aria-label on icon-only buttons
- Use dashes/pills radius on buttons (we use 6px)
```

---

## 5. Token Cheat Sheet（给 AI 的 token 速查）

AI 在没吃完整 token 文件时的救急参考：

### 常用语义 Token

```
Backgrounds:
  bg-canvas              主背景
  bg-surface             卡片底
  bg-surface-sunken      凹陷底
  bg-hover               悬停
  bg-selected            选中
  bg-agent-surface       Agent 气泡

Foregrounds:
  fg-default             正文
  fg-strong              加粗
  fg-muted               次级
  fg-subtle              辅助 / placeholder
  fg-disabled            禁用
  fg-link                链接 (blue)
  fg-brand               品牌 (amber)
  fg-agent               agent (violet)

Borders:
  border-subtle          极弱
  border-default         默认
  border-strong          强
  border-focus           聚焦 (amber)
  border-danger          错误 (red)

Intents:
  intent-primary-*       主 CTA (amber)
  intent-danger-*        危险 (red)
  intent-info-*          信息 (blue)
  intent-warning-*       警告 (yellow)
  intent-positive-*      正向 (amber)
```

### 常用间距

```
space-1   = 4px
space-2   = 8px
space-3   = 12px
space-4   = 16px  ← 默认
space-6   = 24px  ← 卡片内 padding
space-8   = 32px  ← 页面边距
space-12  = 48px  ← 大分隔
```

### 常用圆角

```
radius-xs = 2px
radius-sm = 4px
radius-md = 6px    ← 按钮/输入框默认
radius-lg = 8px    ← 卡片
radius-xl = 12px   ← Modal
```

---

## 6. 生成后自检 Prompt（给 AI 让它自查）

AI 生成完代码后，追加一个 checker prompt：

```
Before finalizing, verify your output:

[ ] All colors via var(--...) — no hex literals in component styles
[ ] All spacing is 4/8/12/16/24/32/48/64px (from space.*)
[ ] All border-radius from radius.* tokens
[ ] Every interactive element has :hover, :active, :focus-visible, :disabled
[ ] No red/green binary encoding — only amber/blue
[ ] Any icon-only button has aria-label
[ ] Any red danger color is paired with icon + text
[ ] Agent messages use violet (bg-agent-surface), human does not
[ ] Font family is Geist + Microsoft YaHei (not Inter / Arial / system-ui alone)
[ ] Numbers inside tables use font-variant-numeric: tabular-nums
[ ] No Enter-to-send (use Cmd+Enter) in composer

If any check fails, rewrite before outputting.
```

---

## 7. Token 映射表（Primitive → Semantic 速查）

给 AI 看完整映射：

```
warm-grey.50  → bg.canvas / bg.surface.subtle
warm-grey.100 → bg.surface.sunken / bg.hover
warm-grey.200 → bg.active / border.subtle
warm-grey.300 → border.default
warm-grey.400 → border.strong / fg.disabled
warm-grey.500 → fg.subtle
warm-grey.600 → fg.muted
warm-grey.800 → fg.default
warm-grey.900 → fg.strong / bg.inverse

amber.50      → intent.primary.surface / bg.selected
amber.100     → intent.primary.surface.hover / bg.selected.strong
amber.600     → intent.primary.bg / border.focus / fg.brand
amber.700     → intent.primary.bg.hover
amber.800     → intent.primary.text-on-surface

blue.50       → intent.info.surface
blue.600      → intent.info.bg / fg.link
blue.700      → fg.link.hover
blue.800      → intent.info.text

red.50        → intent.danger.surface
red.600       → intent.danger.bg / border.danger
red.800       → intent.danger.text

violet.50     → bg.agent.surface / agent.bg.message
violet.100    → bg.agent.trace / agent.bg.trace
violet.600    → fg.agent / agent.fg.primary
```

---

## 8. Multi-Turn 对话策略

当 AI 设计规范驱动的长对话开始时，每 5–10 轮 AI 可能开始"漂移"：
- 开始用 hex 字面值
- 加不在 spec 里的组件
- 忘记 density 模式

**解决方法**：

1. 每隔 3–5 轮，用户插入一条 "Stay in spec check"：
   > "Review your last output against the BYAI hard rules. List any violations and fix them."

2. 保留一个 **anchor message**（system prompt 的最后一轮），定期 re-inject：
   > "Reminder: Always use semantic tokens. Chinese in YaHei. Binary states in amber/blue, not red/green."

---

## 9. 交付物的可追溯性

AI 生成 UI 后，在 HTML comment 中留下 trace：

```html
<!-- Generated with BYAI Design System v1 -->
<!-- Spec: 06-components.md § Button, 03-tokens-semantic.md -->
<!-- Tenets applied: 1 (Clarity), 4 (Keyboard) -->
<!-- Deviations from spec: none -->
```

这让**下一个 AI** 读到这段代码时能理解设计意图、不做冲突修改。

---

## 10. 常见误解澄清

| AI 常犯的误解 | 真相 |
|---|---|
| "BYAI 是浅色模式，所以不用深色 token" | 浅色优先，但代码必须用 semantic token，这样未来切 dark 零成本 |
| "Agent 消息就是聊天 bubble" | 还要 avatar、citation、tool call、metadata、5+ actions |
| "中文界面全用微软雅黑一字体" | 英文部分仍用 Geist，混排效果最佳 |
| "Table 行高 48px 才舒服" | 默认 36px（Comfortable），28px（Compact）才是高密度 |
| "加动效让产品更活泼" | BYAI 动效是功能性的，装饰性动效删除 |
