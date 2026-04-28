# 06 · Component Library
> 40+ 组件完整 API · States · Do/Don't · 代码片段

---

## 组件分类

1. **Foundations**：Button / Link / Icon / Badge / Tag / Kbd / Avatar
2. **Form Inputs**：Input / Textarea / Select / Combobox / Checkbox / Radio / Switch / Slider / DatePicker / FileUpload
3. **Data Display**：Table / List / Tree / Empty / Stat / Progress / Spinner / Skeleton
4. **Overlays**：Modal / Drawer / Popover / Tooltip / Toast / ContextMenu / CommandPalette
5. **Navigation**：Tabs / Breadcrumb / Pagination / Stepper / Sidebar / MenuItem
6. **Feedback**：Alert / Banner / InlineMessage / ConfirmDialog
7. **Structure**：Card / Divider / Panel / Section / Accordion
8. **Agent-Specific**：见 `07-agent-patterns.md`

---

## 通用组件契约

### 必备 Props（所有组件）

| Prop | Type | 必需 | 说明 |
|---|---|---|---|
| `id` | string | 推荐 | 可访问性 / testing 锚点 |
| `className` | string | 否 | 外部扩展 |
| `data-testid` | string | 推荐 | 测试钩子 |
| `aria-*` | string | 按需 | 无障碍 |

### 必覆盖 5 态

每个交互组件必须覆盖：
1. **default** — 常态
2. **hover** — 鼠标悬停
3. **active** — 鼠标按下 / `:active`
4. **focus-visible** — 键盘聚焦 · 用 `shadow.focus-ring` 而非浏览器默认
5. **disabled** — 禁用 · `cursor: not-allowed; opacity: 0.5;`

---

# 1. Foundations

## 1.1 Button

### 1.1.1 Variants

| Variant | 视觉 | 用途 |
|---|---|---|
| `primary` | Amber 实心 | 页面最主要 CTA · 每页 ≤ 1 个 |
| `secondary` | 边框 + 透明填充 | 次级操作 · 多个 |
| `tertiary` / `ghost` | 无边框纯文字 | 第三级 · 辅助 |
| `danger` | Red 实心 | 破坏性操作 · 删除 / 撤销 |
| `danger-ghost` | Red 文字无底 | 破坏性操作的轻量版 |
| `link` | 蓝色文字下划线 | inline 链接型按钮 |

### 1.1.2 Sizes

| Size | Height | Padding | Font | Icon |
|---|---|---|---|---|
| `xs` | 24px | 0 8px | 12px/16 | 14px |
| `sm` | 28px | 0 10px | 13px/18 | 14px |
| `md` (default) | 32px | 0 12px | 14px/20 | 16px |
| `lg` | 40px | 0 16px | 14px/20 | 16px |
| `xl` | 48px | 0 20px | 16px/24 | 20px |

### 1.1.3 完整 CSS

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  height: var(--btn-h-md, 32px);
  padding-inline: var(--space-3);
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: 14px;
  line-height: 20px;
  font-weight: 500;
  border: 1px solid transparent;
  cursor: pointer;
  transition:
    background var(--motion-duration-fast) var(--motion-ease-out),
    border-color var(--motion-duration-fast) var(--motion-ease-out),
    box-shadow var(--motion-duration-fast) var(--motion-ease-out),
    transform var(--motion-duration-fast) var(--motion-ease-out);
  user-select: none;
  white-space: nowrap;
}
.btn:focus-visible {
  outline: none;
  box-shadow: var(--shadow-focus-ring);
}
.btn:active:not(:disabled) {
  transform: translateY(0.5px);
}
.btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

/* Primary */
.btn-primary {
  background: var(--intent-primary-bg);
  color: var(--intent-primary-fg);
}
.btn-primary:hover:not(:disabled) { background: var(--intent-primary-bg-hover); }
.btn-primary:active:not(:disabled) { background: var(--intent-primary-bg-active); }

/* Secondary */
.btn-secondary {
  background: var(--bg-surface);
  color: var(--fg-default);
  border-color: var(--border-default);
}
.btn-secondary:hover:not(:disabled) {
  background: var(--bg-hover);
  border-color: var(--border-strong);
}
.btn-secondary:active:not(:disabled) { background: var(--bg-active); }

/* Tertiary / Ghost */
.btn-ghost {
  background: transparent;
  color: var(--fg-default);
}
.btn-ghost:hover:not(:disabled) { background: var(--bg-hover); }
.btn-ghost:active:not(:disabled) { background: var(--bg-active); }

/* Danger */
.btn-danger {
  background: var(--intent-danger-bg);
  color: var(--intent-danger-fg);
}
.btn-danger:hover:not(:disabled) { background: var(--intent-danger-bg-hover); }
.btn-danger:focus-visible { box-shadow: var(--shadow-focus-ring-danger); }

/* Loading state */
.btn[aria-busy="true"] {
  pointer-events: none;
  position: relative;
}
.btn[aria-busy="true"] .btn-label { opacity: 0; }
.btn[aria-busy="true"]::after {
  content: "";
  position: absolute;
  width: 14px;
  height: 14px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
```

### 1.1.4 HTML

```html
<button class="btn btn-primary">
  <span class="btn-label">Start workflow</span>
</button>

<button class="btn btn-secondary" aria-busy="true">
  <span class="btn-label">Saving...</span>
</button>

<button class="btn btn-danger" aria-keyshortcuts="Meta+Backspace">
  <svg class="icon" aria-hidden="true">...</svg>
  <span class="btn-label">Delete</span>
</button>

<button class="btn btn-ghost btn-sm" aria-label="Add filter">
  <svg class="icon" aria-hidden="true">+</svg>
</button>
```

### 1.1.5 Do / Don't

| ✅ Do | ❌ Don't |
|---|---|
| 动词短语（Start workflow / Delete account） | 名词（Workflow / Account） |
| 每页只有 1 个 primary | 多个 primary（"Save" + "Submit" + "OK"） |
| 危险操作用 `danger` variant | 用红色 `primary` 代替 `danger` |
| Icon-only 按钮必须有 `aria-label` | 只靠 icon 没有文字说明 |
| Loading 时保持按钮宽度 | Loading 时按钮塌陷宽度变化 |

---

## 1.2 Icon

### 1.2.1 规则

- **图标库**：推荐 [Lucide](https://lucide.dev) 或 [Phosphor Regular](https://phosphoricons.com)
- **尺寸**：`14 / 16 / 20 / 24px`（对齐字号）
- **Stroke 宽度**：1.5px（editorial 温度，不用 2px 的硬朗）
- **颜色**：继承 `currentColor`，不要硬编码

### 1.2.2 尺寸 ↔ 字号 对应

| 字号 | 图标尺寸 |
|---|---|
| body (14) | 16 |
| body-small (13) | 14 |
| body-large (16) | 20 |
| h3 (18) | 20 |
| h2 (22) | 24 |

### 1.2.3 HTML

```html
<svg class="icon" width="16" height="16" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="1.5" aria-hidden="true">
  <path d="..."/>
</svg>
```

---

## 1.3 Badge / Tag / Pill

### 1.3.1 Variants

| Variant | 用途 | 视觉 |
|---|---|---|
| `neutral` | 通用标签 | warm-grey 底 |
| `info` | 信息标签 | blue tint |
| `positive` | 正向状态 | amber tint |
| `warning` | 警告状态 | yellow tint |
| `danger` | 危险状态 | red tint |
| `agent` | Agent 相关 | violet tint |

### 1.3.2 Sizes

| Size | Height | Padding | Font |
|---|---|---|---|
| `sm` | 18px | 0 6px | 11px/14 medium |
| `md` (default) | 22px | 0 8px | 12px/16 medium |
| `lg` | 26px | 0 10px | 13px/18 medium |

### 1.3.3 CSS

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  height: 22px;
  padding-inline: var(--space-2);
  border-radius: var(--radius-xs);
  font-size: 12px;
  line-height: 16px;
  font-weight: 500;
  letter-spacing: 0.02em;
  white-space: nowrap;
}

.badge-neutral  { background: var(--intent-neutral-bg); color: var(--intent-neutral-fg); }
.badge-info     { background: var(--intent-info-surface); color: var(--intent-info-text); }
.badge-positive { background: var(--intent-positive-surface); color: var(--intent-positive-text); }
.badge-warning  { background: var(--intent-warning-surface); color: var(--intent-warning-text); }
.badge-danger   { background: var(--intent-danger-surface); color: var(--intent-danger-text); }
.badge-agent    { background: var(--bg-agent-surface); color: var(--fg-agent); }

.badge-dot::before {
  content: "";
  width: 6px;
  height: 6px;
  border-radius: 9999px;
  background: currentColor;
}
```

### 1.3.4 HTML

```html
<span class="badge badge-positive badge-dot">Active</span>
<span class="badge badge-warning">Pending review</span>
<span class="badge badge-agent">AI-generated</span>
<span class="badge badge-neutral">v1.2.0</span>
```

---

## 1.4 Kbd（键盘按键）

```css
.kbd {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding-inline: var(--space-1);
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 500;
  background: var(--bg-surface);
  color: var(--fg-muted);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xs);
  box-shadow: 0 1px 0 var(--border-default);
}
```

```html
<kbd class="kbd">⌘</kbd>
<kbd class="kbd">K</kbd>
```

---

## 1.5 Avatar

### 1.5.1 Sizes

| Size | Dimension | Font (initials) |
|---|---|---|
| `xs` | 20px | 10px |
| `sm` | 24px | 11px |
| `md` | 32px | 13px |
| `lg` | 40px | 15px |
| `xl` | 48px | 18px |
| `2xl` | 64px | 24px |

### 1.5.2 CSS

```css
.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 9999px;
  background: var(--bg-surface-sunken);
  color: var(--fg-default);
  font-size: 13px;
  font-weight: 500;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Agent avatar · violet ring */
.avatar-agent {
  background: var(--bg-agent-surface);
  color: var(--fg-agent);
  box-shadow: 0 0 0 1.5px var(--border-agent);
}

/* Avatar group · 重叠排布 */
.avatar-group { display: flex; }
.avatar-group .avatar:not(:first-child) { margin-left: -8px; border: 2px solid var(--bg-surface); }
```

---

# 2. Form Inputs

## 2.1 Input

### 2.1.1 结构

```
┌─────────────────────────────────────────┐
│  Label *  (type.body-small, medium)     │  ← 与 input 间距 space.2
├─────────────────────────────────────────┤
│  ┌──────────────────────────────────┐   │
│  │ [icon] [placeholder]    [suffix] │   │  ← height 32 (md)
│  └──────────────────────────────────┘   │
├─────────────────────────────────────────┤
│  Helper text / Error  (type.caption)    │  ← fg.muted / intent.danger.text
└─────────────────────────────────────────┘
```

### 2.1.2 CSS

```css
.input-field {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.input-label {
  font-size: 13px;
  line-height: 18px;
  font-weight: 500;
  color: var(--fg-default);
}
.input-label[data-required]::after {
  content: " *";
  color: var(--intent-danger-text);
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  height: 32px;
  padding-inline: var(--space-3);
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  transition: border-color var(--motion-duration-fast) var(--motion-ease-out),
              box-shadow var(--motion-duration-fast) var(--motion-ease-out);
}

.input-wrapper:hover {
  border-color: var(--border-strong);
}

.input-wrapper:focus-within {
  border-color: var(--border-focus);
  box-shadow: var(--shadow-focus-ring);
}

.input-wrapper[data-invalid="true"] {
  border-color: var(--border-danger);
}
.input-wrapper[data-invalid="true"]:focus-within {
  box-shadow: var(--shadow-focus-ring-danger);
}

.input-wrapper input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--fg-default);
  padding: 0;
  min-width: 0;  /* flex bug fix */
}

.input-wrapper input::placeholder {
  color: var(--fg-subtle);
}

.input-helper {
  font-size: 12px;
  line-height: 16px;
  color: var(--fg-muted);
}
.input-helper[data-error="true"] {
  color: var(--intent-danger-text);
}
```

### 2.1.3 HTML

```html
<div class="input-field">
  <label class="input-label" data-required for="email">Work email</label>
  <div class="input-wrapper">
    <svg class="icon" aria-hidden="true">...</svg>
    <input id="email" type="email" placeholder="you@company.com" />
  </div>
  <span class="input-helper">We'll send a verification link.</span>
</div>

<!-- Error state -->
<div class="input-field">
  <label class="input-label" for="api-key">API key</label>
  <div class="input-wrapper" data-invalid="true">
    <input id="api-key" value="sk-..." aria-invalid="true" aria-describedby="api-key-err" />
  </div>
  <span id="api-key-err" class="input-helper" data-error="true">
    <svg class="icon icon-xs" aria-hidden="true">⚠</svg>
    This key is invalid or revoked.
  </span>
</div>
```

### 2.1.4 Input Variants

- **Text**（默认）
- **Password**（带 show/hide toggle）
- **Number**（带 increment/decrement）
- **Search**（左侧放大镜 icon · 右侧 ⌘K / Esc kbd）
- **With prefix/suffix**（如 `$ 123.45` / `42 USD`）

---

## 2.2 Textarea

```css
.textarea-wrapper {
  /* 同 input-wrapper，但 height 可变 */
  min-height: 80px;
  padding: var(--space-2) var(--space-3);
  align-items: stretch;
}

.textarea-wrapper textarea {
  resize: vertical;
  min-height: 60px;
  line-height: 20px;
  font-family: var(--font-body);
  font-size: 14px;
  border: none;
  outline: none;
  background: transparent;
  width: 100%;
}

/* Character count */
.textarea-count {
  align-self: flex-end;
  font-size: 11px;
  color: var(--fg-muted);
}
```

---

## 2.3 Select / Combobox

### 2.3.1 Select（单选下拉）

视觉与 Input 完全一致，右端添加 `▾` chevron icon。
下拉列表使用 Popover 容器。

```html
<div class="input-field">
  <label class="input-label" for="region">Region</label>
  <button class="select-trigger" aria-haspopup="listbox" aria-expanded="false">
    <span class="select-value">Asia Pacific</span>
    <svg class="icon">▾</svg>
  </button>
</div>
```

### 2.3.2 Combobox（可输入搜索 + 下拉）

```
┌────────────────────────────────────┐
│  🔍 Type to search...          ▾   │
├────────────────────────────────────┤
│  Alice Chen       alice@acme.co    │ ← hover: bg.hover
│  Bob Ng           bob@acme.co      │
│  Carol Lin        carol@acme.co    │ ← selected: bg.selected + checkmark
│  ────────────────                  │
│  + Create new contact              │
└────────────────────────────────────┘
```

**必备**：
- 键盘 `↑↓` 导航
- `Enter` 选中
- `Esc` 关闭
- 搜索高亮：`<mark class="highlight">` 使用 `amber.100` 底

---

## 2.4 Checkbox

### 2.4.1 States

| State | Visual |
|---|---|
| unchecked | 空心方框 |
| checked | Amber 填充 + 白 ✓ |
| indeterminate | Amber 填充 + 白横线 |
| disabled | 半透明 |

### 2.4.2 CSS

```css
.checkbox {
  appearance: none;
  width: 16px;
  height: 16px;
  border: 1.5px solid var(--border-default);
  border-radius: var(--radius-xs);
  background: var(--bg-surface);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all var(--motion-duration-fast) var(--motion-ease-out);
}
.checkbox:hover:not(:disabled) { border-color: var(--border-strong); }
.checkbox:focus-visible { box-shadow: var(--shadow-focus-ring); outline: none; }
.checkbox:checked {
  background: var(--intent-primary-bg);
  border-color: var(--intent-primary-bg);
}
.checkbox:checked::after {
  content: "";
  width: 10px;
  height: 10px;
  background-image: url("data:image/svg+xml,..."); /* white checkmark */
}
.checkbox:indeterminate {
  background: var(--intent-primary-bg);
  border-color: var(--intent-primary-bg);
}
.checkbox:indeterminate::after {
  content: "";
  width: 8px;
  height: 2px;
  background: white;
  border-radius: 1px;
}
```

---

## 2.5 Radio

视觉与 Checkbox 类似但**圆形**，选中时中心一个小圆点。

---

## 2.6 Switch（Toggle）

```
OFF:   ○●────         ON:    ────●○
       灰底           Amber 底
```

```css
.switch {
  appearance: none;
  position: relative;
  width: 32px;
  height: 18px;
  border-radius: 9999px;
  background: var(--bg-surface-sunken);
  border: 1px solid var(--border-default);
  cursor: pointer;
  transition: background var(--motion-duration-base) var(--motion-ease-out);
}
.switch::after {
  content: "";
  position: absolute;
  top: 1px;
  left: 1px;
  width: 14px;
  height: 14px;
  border-radius: 9999px;
  background: white;
  box-shadow: var(--shadow-sm);
  transition: transform var(--motion-duration-base) var(--motion-ease-out);
}
.switch:checked {
  background: var(--intent-primary-bg);
  border-color: var(--intent-primary-bg);
}
.switch:checked::after { transform: translateX(14px); }
```

---

## 2.7 DatePicker（简述）

- 触发器视觉同 Input + calendar icon
- Popover 弹出日历面板
- 今日高亮：`intent.primary.surface` 底 + `intent.primary.text` 字
- 选中：`intent.primary.bg` 填充 + 白字
- Range：起止之间 `intent.primary.surface` 底（色觉差异友好 — 不用颜色本身，用填充度区分）

---

# 3. Data Display

## 3.1 Table（最重要·最常用）

### 3.1.1 Anatomy

```
┌────────────────────────────────────────────────────────────────┐
│  Toolbar (48px): [Filters] [Search] [Columns] ──── [Density]   │
├────────────────────────────────────────────────────────────────┤
│  Header (36px)                                                  │
│  ┌──┬──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │☐ │ Name ↓   │ Email    │ Role     │ Status   │   …      │  │
│  ├──┴──────────┴──────────┴──────────┴──────────┴──────────┤  │
│  │ Row (36px)                                              ← hover: bg.hover
│  │ Row                                                     ← selected: bg.selected
│  │ ...                                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────────┤
│  Footer (40px): 1–25 of 1,240 · [Prev] [Next]                 │
└────────────────────────────────────────────────────────────────┘
```

### 3.1.2 Table CSS（严格规范）

```css
.table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 14px;
  line-height: 20px;
}

.table thead th {
  position: sticky;
  top: 0;
  height: var(--row-h, 36px);
  padding: 0 var(--cell-px, 12px);
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-default);
  font-weight: 500;
  font-size: 12px;
  color: var(--fg-muted);
  text-align: left;
  white-space: nowrap;
  z-index: var(--z-sticky);
  user-select: none;
}

.table thead th[aria-sort] { cursor: pointer; }
.table thead th[aria-sort]:hover { color: var(--fg-default); }
.table thead th[aria-sort="ascending"]::after,
.table thead th[aria-sort="descending"]::after {
  margin-left: var(--space-1);
  color: var(--fg-brand);
}
.table thead th[aria-sort="ascending"]::after  { content: "↑"; }
.table thead th[aria-sort="descending"]::after { content: "↓"; }

.table tbody td {
  height: var(--row-h, 36px);
  padding: 0 var(--cell-px, 12px);
  border-bottom: 1px solid var(--border-subtle);
  color: var(--fg-default);
  vertical-align: middle;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.table tbody tr:hover td { background: var(--bg-hover); }
.table tbody tr[aria-selected="true"] td { background: var(--bg-selected); }
.table tbody tr[aria-selected="true"]:hover td { background: var(--bg-selected-strong); }

/* Row actions: 右端悬停出现 */
.table .row-actions {
  opacity: 0;
  transition: opacity var(--motion-duration-fast) var(--motion-ease-out);
}
.table tbody tr:hover .row-actions { opacity: 1; }

/* Sticky first column for wide tables */
.table .col-sticky-left {
  position: sticky;
  left: 0;
  background: inherit;
  z-index: 1;
  border-right: 1px solid var(--border-subtle);
}

/* Numeric columns — right align + tabular */
.table .col-numeric {
  text-align: right;
  font-variant-numeric: tabular-nums;
}
```

### 3.1.3 Table 交互规范

| 交互 | 键盘 | 视觉反馈 |
|---|---|---|
| 单选行 | `Space` on row | `bg.selected` |
| 全选 | `Ctrl+A` / header checkbox | 全部 `bg.selected` |
| 排序 | click header | 箭头 + `aria-sort` |
| 打开详情 | `Enter` / dblclick | 新 Drawer / 新页面 |
| 上下导航 | `↑↓` | Row focus ring |
| 批量操作 | 选中多行 → 出现 floating action bar | |

### 3.1.4 Floating Action Bar（批量操作）

选中任意行后，**底部浮出 48px 高操作条**：

```
┌──────────────────────────────────────────────────────────┐
│  3 items selected  │  [Export] [Assign] [...]  │  ✕      │
└──────────────────────────────────────────────────────────┘
```

```css
.action-bar {
  position: fixed;
  bottom: var(--space-6);
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  height: 48px;
  padding: 0 var(--space-4);
  background: var(--bg-inverse);
  color: var(--fg-on-inverse);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: var(--z-toast);
  animation: slideUp 200ms var(--motion-ease-spring);
}
```

### 3.1.5 Empty State（表格无数据）

见 `08-states.md`。关键：**不展示空表头**，直接替换整个 table-body 为 empty state。

---

## 3.2 List（简单列表）

相比 Table，List 更适合**非结构化数据**或**单列信息**（如通知、活动流）。

```css
.list { list-style: none; padding: 0; margin: 0; }
.list-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
  cursor: pointer;
  transition: background var(--motion-duration-fast) var(--motion-ease-out);
}
.list-item:hover { background: var(--bg-hover); }
.list-item:last-child { border-bottom: none; }
.list-item[aria-current="true"] {
  background: var(--bg-selected);
  border-left: 2px solid var(--border-focus);
  padding-left: calc(var(--space-4) - 2px);
}
```

---

## 3.3 Stat（KPI 卡）

Dashboard 顶部标配。结构：

```
┌────────────────────────────────────┐
│  Label (caption, muted)            │
│  ──────                            │
│  ¥1,245,800                        │  ← Display L (36/40, tabular)
│                                    │
│  ↑ 12.3%  vs. last month           │  ← Amber ↑ / Blue ↓
└────────────────────────────────────┘
  padding: space.6
  background: bg.surface
  border: 1px solid border.subtle
  border-radius: radius.lg
```

### 3.3.1 CSS

```css
.stat-card {
  padding: var(--space-6);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
}
.stat-label {
  font-size: 12px;
  color: var(--fg-muted);
  margin-bottom: var(--space-2);
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
.stat-value {
  font-family: var(--font-body);
  font-size: 36px;
  line-height: 40px;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  color: var(--fg-strong);
  letter-spacing: -0.02em;
}
.stat-delta {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  margin-top: var(--space-3);
  font-size: 13px;
  font-variant-numeric: tabular-nums;
}
.stat-delta[data-trend="up"]   { color: var(--fg-brand); }
.stat-delta[data-trend="down"] { color: var(--intent-info-text); }
.stat-delta[data-trend="flat"] { color: var(--fg-muted); }
.stat-delta-comparison {
  margin-left: var(--space-2);
  color: var(--fg-muted);
  font-variant-numeric: normal;
}
```

**色觉差异硬规**：trend-up = amber，trend-down = blue。**且必须带 ↑/↓ 符号**。

### 3.3.2 HTML

```html
<div class="stat-card">
  <div class="stat-label">Total revenue</div>
  <div class="stat-value">¥1,245,800</div>
  <div class="stat-delta" data-trend="up">
    <span>↑ 12.3%</span>
    <span class="stat-delta-comparison">vs. last month</span>
  </div>
</div>
```

---

## 3.4 Progress

### 3.4.1 Linear Progress

```css
.progress-track {
  width: 100%;
  height: 4px;
  background: var(--bg-surface-sunken);
  border-radius: 9999px;
  overflow: hidden;
}
.progress-bar {
  height: 100%;
  background: var(--intent-primary-bg);
  border-radius: 9999px;
  transition: width var(--motion-duration-base) var(--motion-ease-out);
}
.progress-indeterminate .progress-bar {
  width: 30%;
  animation: progress-slide 1.5s var(--motion-ease-in-out) infinite;
}
@keyframes progress-slide {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(333%); }
}
```

### 3.4.2 Circular Progress（Spinner）

```html
<svg class="spinner" width="16" height="16" viewBox="0 0 16 16">
  <circle cx="8" cy="8" r="6" fill="none" stroke="var(--border-default)" stroke-width="2"/>
  <circle cx="8" cy="8" r="6" fill="none" stroke="var(--intent-primary-bg)" stroke-width="2"
          stroke-dasharray="30" stroke-dashoffset="20" stroke-linecap="round">
    <animateTransform attributeName="transform" type="rotate" from="0 8 8" to="360 8 8" dur="0.8s" repeatCount="indefinite"/>
  </circle>
</svg>
```

---

## 3.5 Skeleton（骨架屏）

```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--bg-surface-sunken) 0%,
    var(--bg-hover) 50%,
    var(--bg-surface-sunken) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s var(--motion-ease-in-out) infinite;
  border-radius: var(--radius-sm);
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
.skeleton-line { height: 14px; margin-bottom: var(--space-2); }
.skeleton-line:last-child { width: 60%; }
.skeleton-circle { border-radius: 9999px; }
.skeleton-rect { /* 自定义 width/height */ }
```

**使用规则**：
- 加载 > 300ms 才显示 skeleton（< 300ms 不显示，避免闪烁）
- Skeleton 形状必须**匹配真实内容形状**（位置、数量、高度近似）
- 一旦加载完成，**淡入真实内容**（`fadeIn 200ms`），不要 abrupt replace

---

# 4. Overlays

## 4.1 Modal / Dialog

### 4.1.1 尺寸

| Size | Width | 用途 |
|---|---|---|
| `sm` | 400px | Confirm / Alert |
| `md` | 560px | **默认** · 普通表单 |
| `lg` | 720px | 复杂表单 / 向导 |
| `xl` | 960px | 数据详情 / 多栏 |
| `fullscreen` | 100vw | 沉浸式编辑 |

### 4.1.2 Anatomy

```
┌──────────────────────────────────────┐
│ Header                               │
│   Title (H2)              [✕ close]  │ ← padding: space.6 space.6 space.4
│   Subtitle (optional, muted)         │
├──────────────────────────────────────┤
│                                      │
│ Body                                 │
│   Form / Content                     │ ← padding: space.6
│                                      │
├──────────────────────────────────────┤
│ Footer                               │
│     [Cancel]  [Primary action]       │ ← padding: space.4 space.6
└──────────────────────────────────────┘
  border-radius: radius.xl (12px)
  shadow: shadow.xl
  backdrop: bg.overlay
```

### 4.1.3 CSS

```css
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: var(--bg-overlay);
  z-index: var(--z-modal);
  backdrop-filter: blur(2px);
  animation: fadeIn 200ms var(--motion-ease-out);
}

.modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 560px;
  max-width: calc(100vw - var(--space-8));
  max-height: calc(100vh - var(--space-16));
  background: var(--bg-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  z-index: var(--z-modal);
  display: flex;
  flex-direction: column;
  animation: modalIn 300ms var(--motion-ease-spring);
}

@keyframes modalIn {
  from { opacity: 0; transform: translate(-50%, -48%) scale(0.96); }
  to   { opacity: 1; transform: translate(-50%, -50%) scale(1); }
}

.modal-header {
  padding: var(--space-6) var(--space-6) var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
}
.modal-title { font-size: 22px; line-height: 28px; font-weight: 600; }
.modal-subtitle { margin-top: var(--space-1); color: var(--fg-muted); }

.modal-body {
  padding: var(--space-6);
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--border-subtle);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}
```

### 4.1.4 键盘

- `Esc` 关闭
- `Tab` 循环聚焦内部元素（focus trap）
- 打开时自动聚焦第一个 input 或 primary button
- 关闭后 focus 回到触发按钮

### 4.1.5 反例

| ❌ | ✅ |
|---|---|
| Modal 叠开 Modal | 最多 1 层，嵌套改用 Step |
| Modal 用 `x` 关闭但无 `Esc` | 必须支持 `Esc` |
| 主要 CTA 在左、Cancel 在右 | **主 CTA 在右**（按阅读顺序） |
| Modal 全屏高度固定 | 内容超长时 body 滚动，header/footer 不动 |

---

## 4.2 Drawer

侧边抽屉，从右侧滑入。用于**详情视图、次级表单**。

```
Drawer.md: 480px (默认)
Drawer.lg: 640px
Drawer.xl: 800px
```

结构与 Modal 相同（Header / Body / Footer），但：
- 从右侧滑入（`translateX(100%) → 0`）
- **不遮罩**内容（可以同时看背后列表）— 除非显式标记 modal 属性
- 支持**嵌套 Drawer**（第二层宽度 = 第一层 - 80px）

---

## 4.3 Popover / Tooltip

### 4.3.1 Popover（交互式悬浮面板）

```css
.popover {
  background: var(--bg-surface-raised);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  padding: var(--space-3);
  min-width: 200px;
  max-width: 320px;
  z-index: var(--z-popover);
  animation: popoverIn 150ms var(--motion-ease-out);
}

@keyframes popoverIn {
  from { opacity: 0; transform: translateY(-4px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

### 4.3.2 Tooltip（只读提示）

```css
.tooltip {
  background: var(--bg-inverse);
  color: var(--fg-on-inverse);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: 12px;
  line-height: 16px;
  max-width: 240px;
  z-index: var(--z-popover);
  box-shadow: var(--shadow-md);
  opacity: 0;
  animation: tooltipIn 150ms 500ms var(--motion-ease-out) forwards;
}
@keyframes tooltipIn { to { opacity: 1; } }
```

**硬规**：
- Tooltip 必须有 **500ms delay**（避免悬停噪音）
- Tooltip 内文字 ≤ 12 词 / 30 个中文字（超过用 Popover）
- Icon-only 按钮必须有 Tooltip（不是 title 属性，是 Tooltip 组件）

---

## 4.4 Toast（全局通知）

```
Position: 右下角 / 右上角 / 底部居中（按产品选，整个产品统一）
最大同时显示: 3 条
Auto-dismiss: 默认 5s，可手动关闭
```

### 4.4.1 Toast 类型

| Type | Icon | Color |
|---|---|---|
| `neutral` | ℹ | warm-grey |
| `positive` | ✓ | amber |
| `info` | ℹ | blue |
| `warning` | ⚠ | yellow |
| `danger` | ✕ | red |
| `agent` | ✨ | violet |

### 4.4.2 CSS

```css
.toast-container {
  position: fixed;
  bottom: var(--space-6);
  right: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  z-index: var(--z-toast);
}
.toast {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  min-width: 320px;
  max-width: 420px;
  padding: var(--space-4);
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-left: 3px solid currentColor;  /* accent left bar */
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  animation: toastIn 300ms var(--motion-ease-spring);
}
.toast-icon { flex-shrink: 0; margin-top: 2px; }
.toast-body { flex: 1; min-width: 0; }
.toast-title { font-weight: 500; margin-bottom: var(--space-1); }
.toast-desc { color: var(--fg-muted); font-size: 13px; }
.toast-actions { margin-top: var(--space-2); display: flex; gap: var(--space-2); }
.toast-close { flex-shrink: 0; }

.toast-positive { color: var(--intent-positive-icon); border-left-color: var(--intent-positive-icon); }
.toast-info     { color: var(--intent-info-icon); border-left-color: var(--intent-info-icon); }
.toast-warning  { color: var(--intent-warning-icon); border-left-color: var(--intent-warning-icon); }
.toast-danger   { color: var(--intent-danger-icon); border-left-color: var(--intent-danger-icon); }
```

---

## 4.5 Command Palette ⌘K（一等公民）

### 4.5.1 结构

```
            ┌─────────────────────────────────────────┐
  ┌──┐      │  🔍  Search or run a command...    [esc]│
  │⌘K│   →  ├─────────────────────────────────────────┤
  └──┘      │  Quick actions                          │
            │  ▸ Create customer               [⌘N]   │ ← arrow = current focus
            │  ▸ Invite teammate               [⌘I]   │
            │  ▸ Open settings                 [⌘,]   │
            │  ─────────────────────                  │
            │  Recent                                 │
            │  ▸ Alice Chen · Customer                │
            │  ▸ Q1 Revenue Report                    │
            │  ─────────────────────                  │
            │  Ask AI                                 │
            │  ▸ "find all overdue invoices" ★        │ ← agent indicator
            └─────────────────────────────────────────┘
              width: 640px · max-height: 480px
```

### 4.5.2 交互规范

| 交互 | 行为 |
|---|---|
| 打开 | `⌘K` / `Ctrl+K` · 任何页面可用 |
| 输入 | 实时 fuzzy filter |
| 上下导航 | `↑↓` |
| 选中 | `Enter` |
| 关闭 | `Esc` / click outside |
| 返回 | 输入中按 `Backspace` 清空后再按 `Esc` 退出 |
| Agent 查询 | 输入非命令文字按 `Enter`，路由到 Agent 处理 ✨ |

### 4.5.3 Agent 融合（BYAI 独有）

Command Palette 的最后一组永远是 **"Ask AI"** — 用户输入任何自然语言问题，按 Enter 后直接提交给 Agent Copilot，Copilot 自动展开侧栏并开始回答。

这是 BYAI 和普通 B2B Command Palette 最大的差异。**必须实现**。

---

# 5. Navigation

## 5.1 Tabs

```css
.tabs {
  display: flex;
  gap: var(--space-6);
  border-bottom: 1px solid var(--border-default);
}
.tab {
  padding: var(--space-3) 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--fg-muted);
  cursor: pointer;
  position: relative;
  transition: color var(--motion-duration-fast) var(--motion-ease-out);
}
.tab:hover:not([aria-selected="true"]) { color: var(--fg-default); }
.tab[aria-selected="true"] {
  color: var(--fg-strong);
}
.tab[aria-selected="true"]::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: -1px;
  height: 2px;
  background: var(--border-focus);
}
.tab-count {
  margin-left: var(--space-2);
  padding: 1px 6px;
  background: var(--bg-surface-sunken);
  border-radius: 9999px;
  font-size: 11px;
  color: var(--fg-muted);
}
```

```html
<nav class="tabs" role="tablist">
  <button class="tab" role="tab" aria-selected="true">
    Overview <span class="tab-count">24</span>
  </button>
  <button class="tab" role="tab" aria-selected="false">Activity</button>
  <button class="tab" role="tab" aria-selected="false">Settings</button>
</nav>
```

---

## 5.2 Breadcrumb

```css
.breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 12px;
  color: var(--fg-muted);
  margin-bottom: var(--space-2);
}
.breadcrumb a { color: inherit; text-decoration: none; }
.breadcrumb a:hover { color: var(--fg-default); text-decoration: underline; }
.breadcrumb [aria-current="page"] { color: var(--fg-default); font-weight: 500; }
.breadcrumb .separator { color: var(--fg-subtle); }
```

---

## 5.3 Sidebar Nav Item

```css
.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: 32px;
  padding: 0 var(--space-3);
  border-radius: var(--radius-md);
  color: var(--fg-muted);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--motion-duration-fast) var(--motion-ease-out);
}
.nav-item:hover { background: var(--bg-hover); color: var(--fg-default); }
.nav-item[aria-current="page"] {
  background: var(--bg-selected);
  color: var(--fg-brand);
}
.nav-item .icon { flex-shrink: 0; color: inherit; }
.nav-item .badge { margin-left: auto; }
.nav-group-label {
  padding: var(--space-4) var(--space-3) var(--space-2);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--fg-subtle);
  font-weight: 600;
}
```

---

## 5.4 Pagination

```
┌──────────────────────────────────────────────┐
│  1–25 of 1,240        [‹] 1 2 3 … 50 [›]    │
│  ↑ fg.muted          ↑ 当前页 bg.selected    │
└──────────────────────────────────────────────┘
```

---

## 5.5 Stepper（向导步骤）

```
┌───────────────────────────────────────────────────┐
│  (1)────(2)────(●)────(4)────(5)                 │
│  Done   Done  Active   ○      ○                  │
│  Setup  Plan  Config  Review  Launch             │
└───────────────────────────────────────────────────┘
```

- 已完成：amber 圈 + ✓
- 当前：amber 实心圈 + 白数字 + **下方文字加粗**
- 未来：灰空心圈
- 连接线：subtle grey，完成段为 amber

---

# 6. Feedback

## 6.1 Alert / Banner

Page 顶部横幅式通知。

### 6.1.1 Variants

| Variant | Background | Border-Left |
|---|---|---|
| `neutral` | warm-grey tint | warm-grey.400 |
| `info` | blue.50 | blue.600 |
| `positive` | amber.50 | amber.600 |
| `warning` | yellow.50 | yellow.500 |
| `danger` | red.50 | red.600 |

```css
.alert {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  border-left: 3px solid currentColor;
}
.alert-icon { flex-shrink: 0; margin-top: 2px; }
.alert-body { flex: 1; }
.alert-title { font-weight: 600; margin-bottom: var(--space-1); }
.alert-actions { margin-top: var(--space-3); display: flex; gap: var(--space-2); }
```

### 6.1.2 反例
- **❌** Alert 一直悬在页面顶部（占空间 + 用户盲视）
- **✅** Alert 可被关闭；重要 alert 用 Modal 代替

---

## 6.2 Inline Message

嵌入在 form、card 内部的轻量反馈：

```
✓  Settings saved automatically
⚠  This field must be unique
✕  Failed to connect. Retry →
```

```css
.inline-message {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 12px;
  line-height: 16px;
}
.inline-message-positive { color: var(--intent-positive-text); }
.inline-message-danger   { color: var(--intent-danger-text); }
.inline-message-warning  { color: var(--intent-warning-text); }
```

---

## 6.3 Confirm Dialog（破坏性操作二次确认）

Modal 的特化版本：

```
┌─────────────────────────────────────────┐
│  ⚠  Delete "Alice Chen"?                │
│  ─────────────────────────────          │
│  This action cannot be undone.           │
│  All associated records will be purged   │
│  after 30 days.                          │
│                                          │
│  Type alice to confirm:                  │
│  [____________________________]          │
│                                          │
│         [Cancel]  [🗑 Delete]           │
└─────────────────────────────────────────┘
```

**硬规**（Destructive confirmation）：
1. 标题必须**包含具体对象名**（不能只是 "Confirm delete"）
2. **输入对象名才能启用 Delete 按钮**（防误点，最重要的这条）
3. Primary button 必须是 `danger` variant
4. Cancel 在左、Delete 在右
5. 说明后果（"cannot be undone" / "30 days purge"）

---

# 7. Structure

## 7.1 Card

```css
.card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--card-p, 24px);
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}
.card-title { font-size: 16px; line-height: 24px; font-weight: 600; }
.card-subtitle { font-size: 13px; color: var(--fg-muted); margin-top: var(--space-1); }
.card-actions { display: flex; gap: var(--space-2); }

/* 可交互卡片 */
.card-interactive {
  cursor: pointer;
  transition: all var(--motion-duration-fast) var(--motion-ease-out);
}
.card-interactive:hover {
  border-color: var(--border-default);
  box-shadow: var(--shadow-sm);
}
```

---

## 7.2 Divider

```css
.divider {
  height: 1px;
  background: var(--border-subtle);
  margin: var(--space-6) 0;
}
.divider-vertical {
  width: 1px;
  height: auto;
  margin: 0 var(--space-4);
}
.divider-with-label {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin: var(--space-6) 0;
  color: var(--fg-muted);
  font-size: 12px;
  letter-spacing: 0.02em;
}
.divider-with-label::before,
.divider-with-label::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--border-subtle);
}
```

---

## 7.3 Accordion

```css
.accordion-item {
  border-bottom: 1px solid var(--border-subtle);
}
.accordion-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) 0;
  background: none;
  border: none;
  font-size: 14px;
  font-weight: 500;
  color: var(--fg-default);
  cursor: pointer;
  text-align: left;
}
.accordion-trigger .chevron {
  transition: transform var(--motion-duration-fast) var(--motion-ease-out);
}
.accordion-trigger[aria-expanded="true"] .chevron {
  transform: rotate(180deg);
}
.accordion-content {
  padding-bottom: var(--space-4);
  color: var(--fg-muted);
}
```

---

# 组件检查清单（AI 实现后自检）

每个组件都应满足：

- [ ] 覆盖 5 态（default / hover / active / focus-visible / disabled）
- [ ] 使用 semantic token 而非 primitive
- [ ] 间距值来自 `space.*` token
- [ ] 圆角值来自 `radius.*` token
- [ ] 阴影值来自 `shadow.*` token
- [ ] 颜色支持 amber/blue 二元而不是 red/green
- [ ] 动画时长来自 `motion.duration.*`
- [ ] 交互元素都有 focus ring
- [ ] 图标 + 文字双编码
- [ ] Icon-only button 有 `aria-label`
- [ ] 支持 3 档密度
- [ ] 中英文字号差异已考虑
