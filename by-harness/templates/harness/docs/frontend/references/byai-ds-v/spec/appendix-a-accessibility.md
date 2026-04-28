# Appendix A · Accessibility
> WCAG 2.2 AA 合规 · 键盘导航 · 色觉差异

---

## 1. Target Standard

BYAI 目标合规等级：**WCAG 2.2 Level AA**。

部分 AAA 条目是 nice-to-have（如对比度 ≥ 7:1），但核心实现必须达 AA。

---

## 2. 对比度要求

### 2.1 对比度阈值

| 内容 | AA | AAA |
|---|---|---|
| 正文文字 | ≥ 4.5:1 | ≥ 7:1 |
| 大字 (≥18px 或 ≥14px bold) | ≥ 3:1 | ≥ 4.5:1 |
| 非文字 UI 元素（icon / border / input） | ≥ 3:1 | — |

### 2.2 已验证的 Token 组合

| 场景 | Foreground | Background | 对比度 | 结论 |
|---|---|---|---|---|
| 正文 | `warm-grey.800` #2A2620 | `warm-grey.50` #FAFAF7 | 13.8:1 | ✅ AAA |
| 次级 | `warm-grey.600` #5C564B | `warm-grey.50` #FAFAF7 | 7.3:1 | ✅ AAA |
| 辅助 | `warm-grey.500` #7A7366 | `warm-grey.50` #FAFAF7 | 4.6:1 | ✅ AA |
| 禁用 | `warm-grey.400` #A8A093 | `warm-grey.50` #FAFAF7 | 2.9:1 | ⚠️ 仅用于禁用态 |
| Primary 按钮 | `#FFFFFF` | `amber.600` #A36E10 | 4.6:1 | ✅ AA |
| Danger 按钮 | `#FFFFFF` | `red.600` #8F2E14 | 6.4:1 | ✅ AA |
| Link | `blue.600` #1E5189 | `warm-grey.50` #FAFAF7 | 7.3:1 | ✅ AAA |
| Link hover | `blue.700` #153E6B | `warm-grey.50` #FAFAF7 | 10.3:1 | ✅ AAA |
| Agent | `violet.600` #5A3F94 | `bg.agent.surface` #F5F2FA | 6.7:1 | ✅ AAA |

**硬规**：自定义组合必须通过 [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/) 验证后才能加入 token。

### 2.3 禁用态的特殊处理

禁用文字对比度通常不达标（这是 WCAG 允许的），但必须辅以：
- `cursor: not-allowed`
- 禁用态 tooltip 说明"为什么不可用"

---

## 3. 键盘导航

### 3.1 Tab 顺序

所有可交互元素必须可通过 `Tab` / `Shift+Tab` 到达。

- Tab 顺序应符合**视觉顺序**（从左到右、从上到下）
- 跳过的区域必须提供"Skip to main content"链接
- 不要用 `tabindex="1"`（破坏自然顺序）

### 3.2 Focus Visible

**硬规**：所有 focusable 元素必须有**清晰的 focus ring**。

不允许 `outline: none` 孤立出现——必须用 `box-shadow` 替代：

```css
:focus-visible {
  outline: none;
  box-shadow: var(--shadow-focus-ring);
}
```

### 3.3 快捷键（全局）

| Shortcut | Action |
|---|---|
| `⌘K` / `Ctrl+K` | Open Command Palette |
| `⌘J` / `Ctrl+J` | Toggle Agent Copilot |
| `⌘/` / `Ctrl+/` | Show keyboard shortcuts help |
| `⌘,` / `Ctrl+,` | Open Settings |
| `Esc` | Close modal / popover / cancel |
| `?` | Keyboard shortcuts overlay |

### 3.4 快捷键（表格）

| Shortcut | Action |
|---|---|
| `↑ ↓` | Move between rows |
| `← →` | Move between cells (when in edit mode) |
| `Space` | Select / deselect row |
| `⌘A` | Select all |
| `Enter` | Open row detail |
| `Delete` | Delete selected (confirm) |

### 3.5 快捷键（表单）

| Shortcut | Action |
|---|---|
| `Tab` | Next field |
| `Shift+Tab` | Previous field |
| `⌘Enter` | Submit form |
| `Esc` | Cancel / close |

---

## 4. 屏幕阅读器（Screen Reader）

### 4.1 Landmark Roles

所有页面使用语义 HTML5：

```html
<header>        <!-- 或 role="banner" -->
<nav>           <!-- 或 role="navigation" -->
<main>          <!-- 或 role="main" -->
<aside>         <!-- 或 role="complementary" -->
<footer>        <!-- 或 role="contentinfo" -->
```

### 4.2 Headings 层级

```html
<h1>              <!-- 页面唯一 -->
  <h2>            <!-- 章节 -->
    <h3>          <!-- 小节 -->
```

不跳级（`<h2>` 后不直接 `<h4>`）。

### 4.3 ARIA Labels

Icon-only 按钮必须有 label：

```html
<button aria-label="Close dialog">
  <svg aria-hidden="true">✕</svg>
</button>
```

表单字段关联：

```html
<label for="email">Email</label>
<input id="email" aria-describedby="email-help email-err" />
<span id="email-help">We'll verify this address.</span>
<span id="email-err" aria-live="polite">Invalid format.</span>
```

### 4.4 Live Regions

动态更新区域（toast, streaming, loading）：

```html
<!-- Streaming message -->
<div role="log" aria-live="polite" aria-atomic="false">
  <p>Agent response streaming here...</p>
</div>

<!-- Toast container -->
<div role="status" aria-live="polite">
  <div class="toast">Settings saved.</div>
</div>

<!-- Error announcement -->
<div role="alert" aria-live="assertive">
  Connection lost.
</div>
```

**区分**：
- `role="status"` / `aria-live="polite"` — 非紧急（toast）
- `role="alert"` / `aria-live="assertive"` — 紧急（error）

---

## 5. 色觉差异友好（Color Vision Deficiency）

这部分**特别重要**——BYAI 的 creator 本人即红绿色弱。

### 5.1 基本规则

1. **颜色绝不是唯一区分手段**——必须辅以图标 / pattern / 文字
2. **二元对比用 Amber / Blue**，不用 Red / Green
3. **涨跌 / 好坏用符号前缀**：`↑ +12%` / `↓ -8%`
4. **图表系列 ≥ 3 时用 pattern**（点、斜纹、虚线）

### 5.2 常见错误

| ❌ | ✅ |
|---|---|
| 红色"跌"、绿色"涨" | Amber "涨" + `↑`，Blue "跌" + `↓` |
| 状态只靠色块区分（必选 / 必填） | 色 + 图标 + 文字 |
| 图例只靠色块 | 色块 + pattern + 文字 |
| 单色散点图标色散 | 色 + 形状（● ◆ ▲ ■） |

### 5.3 仿真工具

设计审查时，用以下工具模拟不同色觉类型：

- Figma：Able 插件 / Stark 插件
- Chrome：DevTools → Rendering → Emulate vision deficiencies
- macOS：系统偏好设置 → 辅助功能 → 显示 → 色彩滤镜

所有主要界面必须通过以下三种模拟：
- Protanopia（红色盲）
- Deuteranopia（绿色盲）
- Tritanopia（蓝色盲，罕见）

---

## 6. Motion & Animation 敏感

### 6.1 Respect prefers-reduced-motion

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### 6.2 避免触发癫痫的模式

- 不要每秒闪烁 > 3 次
- 不要大面积红绿闪烁
- 不要视差滚动过强

---

## 7. Focus 管理（Focus Management）

### 7.1 Modal / Drawer 打开

- 自动聚焦第一个 focusable 元素（input > primary button）
- **Focus trap**：Tab 循环在 modal 内部，不逸出
- 关闭后 focus 回到**触发按钮**

### 7.2 Popover

- 打开时不自动抢焦（避免跳跃感）
- `Tab` 进入 popover 内容
- `Esc` 关闭并返回触发元素

### 7.3 Toast

- **不抢焦**（Toast 非阻塞）
- 但需 `aria-live` 宣告
- 有 action 时，可通过快捷键聚焦（如 `Ctrl+.`）

---

## 8. Form Accessibility

### 8.1 Label / Input 关联

```html
<!-- ✅ 显式 label -->
<label for="email">Email</label>
<input id="email" />

<!-- ✅ aria-label -->
<input aria-label="Search" />

<!-- ❌ 仅 placeholder -->
<input placeholder="Email" />  <!-- 用户开始输入后消失 -->
```

### 8.2 错误 inline 宣告

```html
<div class="input-field">
  <label for="email">Email</label>
  <input id="email" aria-invalid="true" aria-describedby="email-err" />
  <span id="email-err" role="alert">
    Enter a valid email address.
  </span>
</div>
```

### 8.3 Fieldset + Legend

相关字段用 fieldset 包裹：

```html
<fieldset>
  <legend>Billing address</legend>
  <label for="street">Street</label>
  <input id="street" />
  <label for="city">City</label>
  <input id="city" />
</fieldset>
```

---

## 9. Table Accessibility

```html
<table>
  <caption>Q1 2026 sales by customer</caption>
  <thead>
    <tr>
      <th scope="col">Customer</th>
      <th scope="col">Revenue</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">Alice Chen</th>
      <td>¥120,000</td>
    </tr>
  </tbody>
</table>
```

- `<caption>` 描述表格用途（可视觉隐藏）
- `scope="col"` / `scope="row"` 关联
- 可排序列：`<th aria-sort="ascending">`

---

## 10. Agent UI Accessibility

### 10.1 Streaming content

```html
<div role="log" aria-live="polite" aria-label="Agent response">
  <p>Streaming content...</p>
</div>
```

使用 `aria-live="polite"` 避免打断用户。

### 10.2 Tool call

```html
<div role="region" aria-label="Tool call: query_database" aria-live="polite">
  <!-- tool input / output -->
</div>
```

### 10.3 Approval dialog

```html
<div role="alertdialog" aria-labelledby="approval-title" aria-describedby="approval-body">
  <h2 id="approval-title">Confirm before proceeding</h2>
  <div id="approval-body">...</div>
  <button>Approve</button>
  <button>Edit</button>
  <button>Decline</button>
</div>
```

用 `alertdialog` 而非普通 `dialog`，强调需要关注。

---

## 11. 测试清单

### 11.1 键盘测试

- [ ] Tab 遍历所有可交互元素
- [ ] Focus ring 始终可见
- [ ] Esc 关闭 modal / popover
- [ ] 无鼠标可完成核心任务

### 11.2 屏幕阅读器测试

- [ ] 使用 NVDA (Win) / VoiceOver (Mac) 遍历
- [ ] 所有图标按钮有 aria-label
- [ ] 表单错误被宣告
- [ ] 动态内容被宣告

### 11.3 色觉测试

- [ ] DevTools 模拟三种色盲
- [ ] 状态不仅靠颜色
- [ ] 图表图例含 pattern

### 11.4 自动化

```bash
# 集成到 CI
npm install -D @axe-core/react pa11y-ci

# pa11y-ci 配置
pa11y-ci --sitemap https://byai.local/sitemap.xml
```

---

## 12. 工具推荐

| 工具 | 用途 |
|---|---|
| WebAIM Contrast Checker | 对比度验证 |
| axe DevTools | 自动化 a11y 扫描 |
| Pa11y | CLI 扫描 |
| VoiceOver (macOS) | 屏幕阅读器测试 |
| NVDA (Windows) | 屏幕阅读器测试（开源） |
| Stark (Figma) | 设计阶段 a11y 检查 |
| WAVE | 浏览器插件实时扫描 |
