# 02 · Design Tokens — Primitives
> 原子层 Token · 物理属性 · **禁止在组件中直接引用**

---

## 使用纪律

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Primitive      │ ──→ │  Semantic       │ ──→ │  Component      │
│  (本文件)       │     │  (03-tokens-    │     │  (06-components)│
│                 │     │   semantic.md)  │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
    color.amber.600           intent.positive         button.primary.bg
```

**硬规**：任何 UI 组件、任何 HTML 样式，**不得直接出现 primitive token 名称或其 hex 值**。
违反等级：🔴 Critical。

**唯一例外**：在 `03-tokens-semantic.md` 里定义语义 token 时，可以引用 primitive。

---

## 1. Color Primitives

所有颜色以 10 阶（50, 100, 200, …, 900, 950）组织。数值越小越浅。

### 1.1 Warm Grey（暖灰·主基调）

| Token | Hex | 用途示例 |
|---|---|---|
| `color.warm-grey.50` | `#FAFAF7` | Canvas 背景（最常用） |
| `color.warm-grey.100` | `#F4F2ED` | Surface 次级面板 |
| `color.warm-grey.200` | `#E8E4DB` | Border subtle |
| `color.warm-grey.300` | `#D4CEC1` | Border default |
| `color.warm-grey.400` | `#A8A093` | Border strong / Icon muted |
| `color.warm-grey.500` | `#7A7366` | Text tertiary |
| `color.warm-grey.600` | `#5C564B` | Text secondary |
| `color.warm-grey.700` | `#3F3A32` | Text primary on light |
| `color.warm-grey.800` | `#2A2620` | Heading ink |
| `color.warm-grey.900` | `#1A1814` | Display ink（近黑） |
| `color.warm-grey.950` | `#0D0C0A` | Reserved for dark mode |

### 1.2 Amber（琥珀·正向 / 品牌）

语义绑定：**intent.positive / brand.primary**

| Token | Hex | 用途 |
|---|---|---|
| `color.amber.50` | `#FDF8EE` | Subtle background |
| `color.amber.100` | `#FAEBCA` | Tint surface |
| `color.amber.200` | `#F5D88F` | Border / low-emphasis accent |
| `color.amber.300` | `#EFC257` | Illustration |
| `color.amber.400` | `#E4A72E` | Hover state |
| `color.amber.500` | `#C88A1A` | Icon / accent |
| `color.amber.600` | `#A36E10` | **主品牌色 · 默认 CTA** |
| `color.amber.700` | `#7E560D` | Hover on dark bg |
| `color.amber.800` | `#5E400B` | Pressed |
| `color.amber.900` | `#402C08` | Text on tint |

### 1.3 Blue（靛青·信息 / 次轴）

语义绑定：**intent.info · 与 Amber 构成二元对比轴**

| Token | Hex | 用途 |
|---|---|---|
| `color.blue.50` | `#EEF4FA` | Subtle info background |
| `color.blue.100` | `#D6E4F3` | Tint surface |
| `color.blue.200` | `#A9C6E6` | Border |
| `color.blue.300` | `#78A5D5` | Illustration |
| `color.blue.400` | `#4784C1` | Hover |
| `color.blue.500` | `#2A69A8` | Icon |
| `color.blue.600` | `#1E5189` | **默认信息强调** |
| `color.blue.700` | `#153E6B` | Pressed |
| `color.blue.800` | `#0F2D4E` | Heading on tint |
| `color.blue.900` | `#0A1E34` | Text on tint |

### 1.4 Red（朱红·警示·唯一危险色）

语义绑定：**intent.danger**
**特殊规则**：所有 red 使用必须伴随图标或文字标签（色觉差异用户保护）

| Token | Hex | 用途 |
|---|---|---|
| `color.red.50` | `#FCF1ED` | Error surface |
| `color.red.100` | `#F8DACF` | Tint |
| `color.red.200` | `#EDB39F` | Border |
| `color.red.300` | `#DD8469` | — |
| `color.red.400` | `#CC5A3A` | — |
| `color.red.500` | `#B03E1E` | Icon |
| `color.red.600` | `#8F2E14` | **Destructive CTA** |
| `color.red.700` | `#6F220E` | Pressed |
| `color.red.800` | `#4F1809` | — |
| `color.red.900` | `#321005` | Text on tint |

### 1.5 Yellow（警告·琥珀的饱和兄弟）

语义绑定：**intent.warning** · 区别于 Amber 更亮、更饱和

| Token | Hex | 用途 |
|---|---|---|
| `color.yellow.50` | `#FEF9E4` | Warning surface |
| `color.yellow.100` | `#FDEDA9` | — |
| `color.yellow.300` | `#F7CE2B` | Accent |
| `color.yellow.500` | `#D69E08` | **Warning icon** |
| `color.yellow.700` | `#8A6402` | Warning text |
| `color.yellow.900` | `#3D2C00` | — |

### 1.6 Teal（青绿·数据可视化第三轴）

仅用于 data-viz 的多系列区分，不作为 UI 语义色

| Token | Hex |
|---|---|
| `color.teal.100` | `#D4EDE8` |
| `color.teal.400` | `#2E9C8A` |
| `color.teal.600` | `#1B6F62` |
| `color.teal.800` | `#0E3D36` |

### 1.7 Violet（紫·Agent 专用辅色）

**唯一用途**：标记 Agent 行为（发言、工具调用、思考过程）与人类行为区分开。
不用于品牌、不用于状态。

| Token | Hex | 用途 |
|---|---|---|
| `color.violet.50` | `#F5F2FA` | Agent message bubble bg |
| `color.violet.100` | `#E4DDF2` | Reasoning trace bg |
| `color.violet.400` | `#7A5DB0` | Agent avatar bg |
| `color.violet.600` | `#5A3F94` | Agent accent text / icon |
| `color.violet.800` | `#32215A` | — |

---

## 2. Typography Primitives

### 2.1 Font Families

| Token | Stack | 用途 |
|---|---|---|
| `font.family.display` | `"Fraunces", "Instrument Serif", Georgia, serif` | 编辑式标题点缀 |
| `font.family.sans` | `"Geist", "Söhne", ui-sans-serif, system-ui, -apple-system, sans-serif` | UI body · 默认 |
| `font.family.mono` | `"JetBrains Mono", "Geist Mono", ui-monospace, "SF Mono", monospace` | 代码 / ID / 数字 |
| `font.family.cjk` | `"Microsoft YaHei", "微软雅黑", "PingFang SC", "Source Han Sans CN", sans-serif` | 中文全部 |

**字体加载策略**：见 `/assets/fonts.css`，使用 `font-display: swap` 保障首屏。

### 2.2 Font Sizes（基线 14px · 模数 1.125）

| Token | px | rem | 用途 |
|---|---|---|---|
| `font.size.micro` | 11 | 0.688 | Badge / Tag / 极密表格 |
| `font.size.caption` | 12 | 0.75 | 辅助说明 · Meta 信息 |
| `font.size.small` | 13 | 0.813 | 次级 body |
| `font.size.body` | 14 | 0.875 | **默认 body · UI 基准** |
| `font.size.body-large` | 16 | 1.0 | 阅读型 body · 长文 |
| `font.size.h3` | 18 | 1.125 | 小节标题 |
| `font.size.h2` | 22 | 1.375 | 章节标题 |
| `font.size.h1` | 28 | 1.75 | 页面标题 |
| `font.size.display-l` | 36 | 2.25 | Landing / Login Hero |
| `font.size.display-xl` | 48 | 3.0 | 登录品牌字 · 保留 |

### 2.3 Font Weights

| Token | Value |
|---|---|
| `font.weight.regular` | 400 |
| `font.weight.medium` | 500 |
| `font.weight.semibold` | 600 |
| `font.weight.bold` | 700 |

**禁用**：light (300) 和 black (900)。前者在浅色背景可读性差，后者与 editorial 调性冲突。

### 2.4 Line Heights（数字 = 行高像素，不是 ratio）

| Token | px | 配对字号 |
|---|---|---|
| `font.line.micro` | 14 | micro (11) |
| `font.line.caption` | 16 | caption (12) |
| `font.line.small` | 18 | small (13) |
| `font.line.body` | 20 | body (14) · 基准 |
| `font.line.body-large` | 24 | body-large (16) |
| `font.line.h3` | 24 | h3 (18) |
| `font.line.h2` | 28 | h2 (22) |
| `font.line.h1` | 34 | h1 (28) |
| `font.line.display-l` | 40 | display-l (36) |
| `font.line.display-xl` | 52 | display-xl (48) |

### 2.5 Letter Spacing

| Token | Value | 用途 |
|---|---|---|
| `font.tracking.tight` | -0.02em | Display (36+) |
| `font.tracking.snug` | -0.01em | Headings (18–28) |
| `font.tracking.normal` | 0 | Body |
| `font.tracking.wide` | 0.02em | Caps / Tag (11–12) |
| `font.tracking.wider` | 0.06em | 全大写徽标 |

---

## 3. Space Primitives（4px base grid）

**唯一间距来源**。任何 padding / margin / gap 必须来自此表。

| Token | px | 使用频次 |
|---|---|---|
| `space.0` | 0 | — |
| `space.0-5` | 2 | 仅用于 icon 内部微调 |
| `space.1` | 4 | 极紧 inline |
| `space.2` | 8 | 紧凑 inline · Tag 内 padding |
| `space.3` | 12 | 紧凑元素间距 |
| `space.4` | 16 | **默认 ✨** |
| `space.5` | 20 | 中等段落间 |
| `space.6` | 24 | 段落 / 卡片间距 |
| `space.8` | 32 | 章节间距 |
| `space.10` | 40 | 大区块 |
| `space.12` | 48 | 页面章节 |
| `space.16` | 64 | 页面大 section |
| `space.20` | 80 | Hero padding |
| `space.24` | 96 | 极端大间距（罕用） |

---

## 4. Border Radius Primitives

| Token | px | 用途 |
|---|---|---|
| `radius.none` | 0 | 完全直角（极少用，仅 editorial 装饰） |
| `radius.xs` | 2 | Tag / Badge inner |
| `radius.sm` | 4 | Input 小尺寸 |
| `radius.md` | 6 | **默认 ✨** · Button / Input / Select |
| `radius.lg` | 8 | Card / Panel |
| `radius.xl` | 12 | Modal / Dialog |
| `radius.2xl` | 16 | Large card / Feature tile |
| `radius.3xl` | 24 | 装饰性大卡片（罕用） |
| `radius.full` | 9999 | Pill / Avatar |

---

## 5. Border Widths

| Token | px |
|---|---|
| `border.width.none` | 0 |
| `border.width.thin` | 1 |
| `border.width.default` | 1 |
| `border.width.thick` | 2 |
| `border.width.focus` | 2 |

---

## 6. Shadow Primitives（暖调阴影）

所有阴影使用 `rgba(26,24,20,…)`（warm-grey.900 for opacity）——与纯黑 shadow 比更柔和。

| Token | Value |
|---|---|
| `shadow.xs` | `0 1px 2px rgba(26, 24, 20, 0.04)` |
| `shadow.sm` | `0 1px 3px rgba(26, 24, 20, 0.06), 0 1px 2px rgba(26, 24, 20, 0.04)` |
| `shadow.md` | `0 4px 8px rgba(26, 24, 20, 0.06), 0 2px 4px rgba(26, 24, 20, 0.04)` |
| `shadow.lg` | `0 12px 24px rgba(26, 24, 20, 0.08), 0 4px 8px rgba(26, 24, 20, 0.04)` |
| `shadow.xl` | `0 24px 48px rgba(26, 24, 20, 0.10), 0 8px 16px rgba(26, 24, 20, 0.06)` |
| `shadow.focus-ring` | `0 0 0 3px rgba(163, 110, 16, 0.25)` （Amber 600 · 25%） |
| `shadow.focus-ring-danger` | `0 0 0 3px rgba(143, 46, 20, 0.25)` |
| `shadow.inset-subtle` | `inset 0 1px 0 rgba(255, 255, 255, 0.08)` |

---

## 7. Motion Primitives

### 7.1 Durations

| Token | ms |
|---|---|
| `motion.duration.instant` | 0 |
| `motion.duration.fast` | 120 |
| `motion.duration.base` | 200 |
| `motion.duration.slow` | 320 |
| `motion.duration.slower` | 500 |
| `motion.duration.slowest` | 800 |

### 7.2 Easing

| Token | Curve |
|---|---|
| `motion.ease.linear` | `linear` |
| `motion.ease.out` | `cubic-bezier(0.25, 1, 0.5, 1)` · **默认 ✨** |
| `motion.ease.in-out` | `cubic-bezier(0.65, 0, 0.35, 1)` |
| `motion.ease.spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` · 入场用 |
| `motion.ease.anticipate` | `cubic-bezier(0.87, 0, 0.13, 1)` · 退场用 |

---

## 8. Z-Index Primitives

| Token | Value | 用途 |
|---|---|---|
| `z.base` | 0 | Normal flow |
| `z.raised` | 10 | 悬浮卡片 |
| `z.dropdown` | 100 | Select / Menu |
| `z.sticky` | 200 | Sticky header / 表头 |
| `z.drawer` | 300 | 侧边抽屉 |
| `z.modal` | 400 | Modal backdrop + content |
| `z.popover` | 500 | Popover / Tooltip |
| `z.toast` | 600 | 全局通知 |
| `z.command-palette` | 700 | ⌘K |
| `z.top` | 9999 | 仅用于 debug overlay |

**规则**：不得在代码中硬编码 z-index 数字，必须使用 token。

---

## 9. Breakpoints

B2B 产品以桌面为主，但保留基础响应式断点（主要用于 Settings / Login 等次要页面的移动端可用性）。

| Token | min-width | 典型设备 |
|---|---|---|
| `bp.sm` | 640px | 大手机 |
| `bp.md` | 768px | 平板 |
| `bp.lg` | 1024px | 小笔记本 |
| `bp.xl` | 1280px | **设计基准 ✨** |
| `bp.2xl` | 1536px | 大屏 |
| `bp.3xl` | 1920px | 4K / 超宽 |

**设计基准**：所有主要界面以 1440×900 视口为基准做视觉决策。

---

## 10. 完整的 JSON 表达

见 `/tokens/tokens.json`（W3C DTCG 格式）。
CSS 变量版见 `/tokens/tokens.css`。
