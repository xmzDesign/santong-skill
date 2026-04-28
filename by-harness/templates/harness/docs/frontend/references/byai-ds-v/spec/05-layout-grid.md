# 05 · Layout & Grid System
> Shell 骨架 · 12 栏栅格 · 三档密度 · 响应式

---

## 1. 应用壳（Application Shell）

BYAI 规定的 Hybrid SaaS 壳——所有主界面以此为基础。

### 1.1 骨架图

```
┌────────────────────────────────────────────────────────────────────────┐
│  TopBar (48px)                                                          │ ← z.sticky
├────────┬──────────────────────────────────────────────────┬────────────┤
│        │                                                  │            │
│  Nav   │                                                  │   Agent    │
│ (240px)│        Main Content (flex-1)                     │  Copilot   │
│        │                                                  │  (380px)   │
│        │                                                  │ collapsible│
│        │                                                  │            │
├────────┴──────────────────────────────────────────────────┴────────────┤
│  StatusBar (28px · optional)                                            │
└────────────────────────────────────────────────────────────────────────┘
```

### 1.2 各区域规范

| 区域 | 宽度 | 高度 | Background | 必选 |
|---|---|---|---|---|
| **TopBar** | 100% | 48px | `bg.surface` + bottom `border.default` | ✅ |
| **NavSidebar** | 240px (collapsed: 56px) | 100vh - 48px | `bg.canvas` | ✅ |
| **Main** | flex-1 | 100vh - 48px (- 28px if StatusBar) | `bg.canvas` | ✅ |
| **AgentCopilot** | 380px (collapsed: 0, hidden) | 100vh - 48px | `bg.surface` + left `border.default` | ★ 可折叠 |
| **StatusBar** | 100% | 28px | `bg.surface.sunken` + top `border.subtle` | 可选 |

### 1.3 Agent Copilot 的三种状态

| 状态 | 宽度 | 触发 |
|---|---|---|
| Hidden | 0 | 用户关闭 / 首次进入 |
| Docked (默认) | 380px | ⌘J 或 右下 FAB |
| Expanded | 560px | 从 Docked 拖宽 / 用户手动 |

**硬规**：Agent Copilot 的开关状态必须**持久化**到用户偏好，而不是每次会话重置。

### 1.4 TopBar 结构

```
[Logo] [Workspace Switcher]    [Breadcrumb / Search]       [Notifications] [Avatar]
  ↑ 160px           ↑ flex                               ↑ 固定 ~100px
```

- Logo + Workspace Switcher：左对齐，合计 ~240px（与 Nav 宽度对齐，形成锚定线）
- 中间 Breadcrumb：flex-grow，左对齐
- 右侧 Actions：`notifications + avatar`，固定

### 1.5 TopBar 的信息层次

```
TopBar
 ├─ Brand (Logo + 工作区名)        ← 次要强调
 ├─ 主导航 Breadcrumb               ← 让用户知道"我在哪"
 ├─ Global Search (⌘K 入口)         ← 第一 CTA ✨
 └─ User menu + Notifications       ← 右侧 always
```

---

## 2. 栅格系统（Grid）

### 2.1 基础栅格

- **列数**：12
- **Gutter**：`space.6` (24px)
- **Outer padding**：`space.8` (32px) 左右
- **Max content width**：1440px（在 > 1440px 屏上居中）

### 2.2 常用分栏

```
全宽 1 列                  ← 文章、Timeline
6 + 6                     ← 左图右文、数据对比
8 + 4                     ← 主内容 + 侧边 Meta ✨ 最常用
4 + 4 + 4                 ← KPI 三卡
3 + 3 + 3 + 3             ← KPI 四卡 ✨ 标准 Dashboard 顶部
2 + 10                    ← 侧边分类 + 列表
```

### 2.3 Container

```css
.container {
  max-width: 1440px;
  margin-inline: auto;
  padding-inline: var(--space-8);
}

.container-narrow {
  max-width: 960px;    /* 表单 / Settings / Article */
  margin-inline: auto;
  padding-inline: var(--space-8);
}

.container-tight {
  max-width: 640px;    /* Modal 内容 / Step-by-step */
  margin-inline: auto;
}
```

---

## 3. 密度档位（Density Modes）

三档密度是 BYAI 的**核心可配特性**，专业用户可在 Settings 里切换。

### 3.1 三档定义

| 属性 | Compact | **Comfortable (默认)** | Spacious |
|---|---|---|---|
| Table row height | 28px | **36px** | 44px |
| Table cell padding | 6px / 8px | **8px / 12px** | 12px / 16px |
| Button height (md) | 28px | **32px** | 36px |
| Input height (md) | 28px | **32px** | 36px |
| List item padding | 6px / 12px | **8px / 16px** | 12px / 20px |
| Card padding | 16px | **24px** | 32px |
| Nav item height | 28px | **32px** | 40px |

### 3.2 实现方式

在 `<html>` 或 `<body>` 上加类名，通过 CSS 变量级联：

```html
<html class="density-comfortable"> <!-- default -->
<html class="density-compact">
<html class="density-spacious">
```

```css
:root { /* Comfortable · default */
  --row-h: 36px;
  --cell-py: 8px;
  --cell-px: 12px;
  --btn-h-md: 32px;
  --card-p: 24px;
}
.density-compact {
  --row-h: 28px;
  --cell-py: 6px;
  --cell-px: 8px;
  --btn-h-md: 28px;
  --card-p: 16px;
}
.density-spacious {
  --row-h: 44px;
  --cell-py: 12px;
  --cell-px: 16px;
  --btn-h-md: 36px;
  --card-p: 32px;
}
```

### 3.3 密度切换动画

密度切换必须加 `transition` 避免突兀：

```css
.table,
.button,
.list-item {
  transition:
    padding var(--motion-duration-base) var(--motion-ease-out),
    min-height var(--motion-duration-base) var(--motion-ease-out);
}
```

---

## 4. 间距系统应用（Spacing in Practice）

### 4.1 常见模式

| 场景 | Spacing Token |
|---|---|
| Icon + 文字 | `space.2` (8px) gap |
| Button 内 icon + label | `space.2` (8px) gap |
| Form field 之间垂直 | `space.4` (16px) |
| Card 内部 padding | `space.6` (24px) |
| Section 之间垂直 | `space.12` (48px) |
| 页面顶部 padding-top | `space.8` (32px) |
| 页面底部 padding-bottom | `space.16` (64px) |

### 4.2 八倍规则

**所有间距必须是 4 的倍数**，但优先从 Token 表里挑。非 token 值（如 13px、18px）绝对禁止。

### 4.3 Stack / Inline / Grid utilities

推荐使用 flex / grid 的 gap 属性，而不是 margin：

```css
.stack-4 { display: flex; flex-direction: column; gap: var(--space-4); }
.inline-2 { display: flex; flex-direction: row; gap: var(--space-2); align-items: center; }
.grid-cols-12 { display: grid; grid-template-columns: repeat(12, 1fr); gap: var(--space-6); }
```

---

## 5. 响应式（Responsive）

**设计基准：1440 × 900**。B2B 产品不以移动端为主，但要保障以下场景可用：

### 5.1 移动场景

| 页面 | 移动端处理 |
|---|---|
| Login | 完整支持（单栏） |
| Dashboard | 只读只查（Nav 折叠为 top drawer） |
| Table | 水平滚动 + 首列 sticky |
| Settings | 完整支持（单栏堆叠） |
| Chat / Agent | 全屏单栏 |

### 5.2 断点应用

```css
/* 默认样式 = 桌面 */
.layout-shell {
  display: grid;
  grid-template-columns: 240px 1fr 380px;
}

/* 中屏：Agent Copilot 折叠 */
@media (max-width: 1280px) {
  .layout-shell { grid-template-columns: 240px 1fr 0; }
  .agent-copilot { display: none; }
}

/* 小屏：Nav 也折叠 */
@media (max-width: 1024px) {
  .layout-shell { grid-template-columns: 56px 1fr 0; }
  .nav-sidebar { width: 56px; }
  .nav-sidebar .label { display: none; }
}

/* 移动：单栏 + drawer 导航 */
@media (max-width: 768px) {
  .layout-shell { grid-template-columns: 1fr; }
  .nav-sidebar { position: fixed; transform: translateX(-100%); z-index: var(--z-drawer); }
  .nav-sidebar.open { transform: translateX(0); }
}
```

---

## 6. Page Shell 组件模板

任何主界面应符合此结构。AI 生成新页面时，直接套用：

```html
<body class="density-comfortable">
  <div class="app-shell">

    <!-- TopBar -->
    <header class="topbar">
      <div class="topbar-left">
        <a class="logo">BYAI</a>
        <button class="workspace-switcher">BYAI Production</button>
      </div>
      <nav class="topbar-center" aria-label="Breadcrumb">
        <!-- breadcrumb items -->
      </nav>
      <div class="topbar-right">
        <button class="cmd-k-trigger" aria-keyshortcuts="Meta+K">
          <kbd>⌘K</kbd> Search
        </button>
        <button class="notifications" aria-label="Notifications">…</button>
        <button class="user-avatar">…</button>
      </div>
    </header>

    <!-- Main Layout -->
    <div class="shell-body">
      <!-- Nav Sidebar -->
      <aside class="nav-sidebar" aria-label="Primary Navigation">
        <!-- nav items -->
      </aside>

      <!-- Main Content -->
      <main class="main-content">
        <div class="page-header">
          <h1 class="type-h1">Page Title</h1>
          <div class="page-actions">…</div>
        </div>
        <div class="page-body">
          <!-- content -->
        </div>
      </main>

      <!-- Agent Copilot Sidebar (toggleable) -->
      <aside class="agent-copilot" data-state="docked">
        <!-- chat interface -->
      </aside>
    </div>

  </div>
</body>
```

---

## 7. Page Header 规范

每个主页面顶部的 header block 严格遵循：

```
┌──────────────────────────────────────────────────────────────┐
│  Breadcrumb                                                   │  ← type.caption · fg.muted
│  ┌───────────────────────────────────────┐  ┌─────────┐      │
│  │ Page Title (H1)                      │  │ Actions │      │
│  │ Subtitle / Description (body-lg, muted)│  │  …      │      │
│  └───────────────────────────────────────┘  └─────────┘      │
│                                                               │
│  [Tab1] [Tab2] [Tab3]         <- optional                    │
└──────────────────────────────────────────────────────────────┘
   padding: space.8 (top) space.8 (x) space.6 (bottom)
   border-bottom: border.subtle
```

### 7.1 Page Header HTML

```html
<header class="page-header">
  <nav class="breadcrumb">
    <a href="/customers">Customers</a>
    <span class="separator">/</span>
    <span aria-current="page">Alice Chen</span>
  </nav>

  <div class="page-title-row">
    <div>
      <h1 class="type-h1">Alice Chen</h1>
      <p class="page-subtitle type-body-lg text-muted">
        Enterprise customer · Onboarded 12 Mar 2024
      </p>
    </div>
    <div class="page-actions">
      <button class="btn-secondary">Edit</button>
      <button class="btn-primary">Start workflow</button>
    </div>
  </div>

  <nav class="page-tabs">
    <a class="tab active">Overview</a>
    <a class="tab">Activity</a>
    <a class="tab">Integrations</a>
  </nav>
</header>
```

---

## 8. 垂直节奏（Vertical Rhythm）

页面垂直方向的节奏由**四个"基线"**构成，视觉上稳定：

```
┌── page-header.padding-top = space.8 ────
│   Breadcrumb
│   ↓ space.2
│   Title + Actions
│   ↓ space.2
│   Subtitle
├── page-header.border-bottom + space.8 ──  ← Section 起点 A
│   Section 1
│   ↓ space.12
├── ────────────────────────────────────── ← Section 起点 B
│   Section 2
│   ↓ space.12
├── ────────────────────────────────────── ← Section 起点 C
│   ...
│   ↓ space.16 (底部留白)
└───────────────────────────────────────── ← Page 结束
```

---

## 9. 反例

| ❌ | ✅ |
|---|---|
| Nav 和 TopBar 之间有 border（重复分割） | Nav 无 top-border，靠 TopBar 的 bottom-border 统一 |
| Nav item 高度 48px 导致导航占屏太多 | 32px（Comfortable）或 28px（Compact） |
| 每个 Card 都带 shadow-lg | Card 默认无 shadow，只用 `border.subtle` 分割 |
| Page padding 18px / 22px / 30px 随意 | 严格来自 space token |
| Agent 侧栏固定不可关 | 必须可关且持久化偏好 |
