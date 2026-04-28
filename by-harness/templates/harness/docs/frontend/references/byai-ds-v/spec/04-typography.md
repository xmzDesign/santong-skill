# 04 · Typography System
> 9 级字阶 · 中英双语配对 · 数字字体 · Editorial 温度

---

## 0. TL;DR · 三条最重要的规则

1. **中文一律用微软雅黑**，而不是 PingFang（用户偏好 + 高密度界面字重更清晰）
2. **英文正文用 Geist**，**标题点缀用 Fraunces 衬线**（editorial 温度的来源）
3. **数字一律用 tabular-nums**（`font-feature-settings: "tnum"`），表格对齐永远不会错位

---

## 1. 字体堆栈（Font Stacks）

### 1.1 完整堆栈（按语言场景）

```css
/* 1. 英文显示字 · Editorial 衬线 */
--font-display: "Fraunces", "Instrument Serif", "Times New Roman", Georgia, serif;

/* 2. 英文 UI / Body · 现代 Sans */
--font-sans: "Geist", "Söhne", "Inter", ui-sans-serif, system-ui,
             -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif;

/* 3. 等宽 · 代码 / ID / 技术数字 */
--font-mono: "JetBrains Mono", "Geist Mono", ui-monospace,
             "SF Mono", Menlo, Consolas, monospace;

/* 4. 中文全部 · 微软雅黑优先 */
--font-cjk: "Microsoft YaHei", "微软雅黑", "PingFang SC",
            "Source Han Sans CN", "Noto Sans SC", sans-serif;

/* 5. 组合堆栈 · 英文走 Geist 中文回落微软雅黑 */
--font-body: "Geist", -apple-system, BlinkMacSystemFont,
             "Microsoft YaHei", "微软雅黑", "PingFang SC", sans-serif;

/* 6. 组合堆栈 · 英文衬线 中文无衬线（刻意混搭·editorial 风格） */
--font-heading: "Fraunces", "Instrument Serif", Georgia,
                "Microsoft YaHei", "微软雅黑", serif;
```

**设计决策解释**：为什么中文不用衬线（宋体系）？
中文屏幕衬线字体（如思源宋体）在 ≤ 14px 时可读性差，且与 Microsoft YaHei 混排无法对齐基线。
**刻意不统一**——英文走衬线 serif 带来 editorial 气质，中文走无衬线 sans 保障可读性。
这是本规范最有品味的一处取舍。

### 1.2 字体加载

字体文件统一从 CDN 加载（见 `/assets/fonts.css`）：

```html
<link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Geist:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

Geist 的回退方案（若 CDN 失败）：使用系统 `-apple-system` 或 `BlinkMacSystemFont`——视觉差距可接受。
微软雅黑通常系统自带，不需额外加载。

---

## 2. 字阶（Type Scale）

### 2.1 九级字阶 + Display 扩展

| Level | Token | Size | Line | Weight | Tracking | Family | 用途 |
|---|---|---|---|---|---|---|---|
| D-XL | `type.display.xl` | 48 | 52 | 500 | -0.02em | display | Login / 纪念页 Hero（罕用） |
| D-L | `type.display.l` | 36 | 40 | 500 | -0.02em | display | Landing / 大空标题 |
| H1 | `type.heading.h1` | 28 | 34 | 600 | -0.015em | sans | 页面主标题 |
| H2 | `type.heading.h2` | 22 | 28 | 600 | -0.01em | sans | 章节标题 |
| H3 | `type.heading.h3` | 18 | 24 | 600 | -0.005em | sans | 卡片标题 / 小节 |
| BodyL | `type.body.large` | 16 | 24 | 400 | 0 | sans | 长文阅读 |
| Body | `type.body.default` | 14 | 20 | 400 | 0 | sans | **UI 默认 ✨** |
| BodyS | `type.body.small` | 13 | 18 | 400 | 0 | sans | 次级 body |
| Cap | `type.caption` | 12 | 16 | 400 | 0 | sans | 辅助说明 / Meta |
| Micro | `type.micro` | 11 | 14 | 500 | 0.02em | sans | Badge / 极密表格 |

### 2.2 强调变体（Emphasis Variants）

每个字阶都有 **Regular / Medium / Semibold** 三档权重：

- **Regular (400)** — 默认
- **Medium (500)** — 轻强调 / 表格列名 / Label
- **Semibold (600)** — 标题默认 / 强强调

**禁止**使用 `font-weight: bold` （会渲染为 700）——强调层级需要可控，始终在 400 / 500 / 600 三档选。

### 2.3 Editorial 点缀（衬线混搭）

以下场景**可选**用 Fraunces 衬线，增加 editorial 温度：

1. 登录页品牌 display 字
2. 空状态的插画标题
3. Dashboard 上的欢迎语 "Good morning, Wang."
4. Error 404 / 500 页面的大数字

**不要**在常规 UI 组件（Button / Tag / 表头）里用衬线——影响可读性且稍显矫情。

---

## 3. 数字（Numbers · 最容易犯错的地方）

### 3.1 Tabular Numbers

**所有会出现在表格、KPI、列表里的数字必须启用 tabular-nums**：

```css
.numeric {
  font-feature-settings: "tnum" 1, "cv01" 1;
  font-variant-numeric: tabular-nums;
}
```

不开 tabular 的后果：`1,234` 和 `9,876` 宽度不同，竖向表格里数字无法对齐——专业工具最大的视觉灾难。

### 3.2 Fraction Separators

- 千分位：英文用 `,` (e.g., `12,450`)；中文上下文可用 `,` 或不加（如 `¥12450`）——**团队内需统一**
- 小数：一律 `.`（全球惯例）
- 负号：`-12` 不要 `–12` 或 `(12)`；但会计场景允许 `(12.00)`

### 3.3 Unit 规则

**硬规**：任何数字旁必须有单位 / 前缀 / 上下文标签。裸数字是 Tenet 1 违反。

| 场景 | 正确写法 |
|---|---|
| 金额 | `¥12,450` `$1,234.56` `HK$ 9,800` |
| 百分比 | `12.5%` `+8.3%` `-2.1%` |
| 时长 | `1.2 s` `340 ms` `2 h 15 min` |
| 大小 | `1.2 GB` `845 MB` `3,240 rows` |
| 日期 | `2026-04-21` 或 `Apr 21, 2026`（ISO 优先） |
| 时间 | `14:30` / `2:30 PM` |
| 人数 | `12 users` / `12 位用户` |

### 3.4 大数字缩写

| 区间 | 缩写 | 示例 |
|---|---|---|
| < 1,000 | 原值 | `847` |
| 1K – 999K | `K` | `12.3K` `847K` |
| 1M – 999M | `M` | `1.2M` `234.5M` |
| ≥ 1B | `B` | `1.23B` |
| 中文场景 | 万 / 亿 | `1.24万` `3.5亿` |

**Tooltip 规则**：缩写数字 hover 时必须显示精确值，如 `12.3K` → tooltip: `12,345`

---

## 4. 段落与行长

### 4.1 行长上限

| 场景 | 最大字符数 | 说明 |
|---|---|---|
| 长文阅读（文章 / 文档） | 70 ch | 约 600px |
| UI 说明文字 | 60 ch | 约 480px |
| 表格单元格 | 40 ch | 约 320px，超出截断 + tooltip |
| Tag / Badge | 20 ch | 超出省略号 |

```css
.prose { max-width: 65ch; }
.description { max-width: 60ch; }
```

### 4.2 段间距

- 正文段落间距：`margin-bottom: var(--space-4)` (16px)
- 标题下到内容：`margin-top: var(--space-6)` (24px)（视觉呼吸）
- 章节间距：`margin-top: var(--space-12)` (48px)

---

## 5. 文本颜色使用规则

| 场景 | Token | 应用 |
|---|---|---|
| 主文字（H1–H3, Body） | `fg.default` | warm-grey.800 |
| 页面主标题 | `fg.strong` | warm-grey.900 |
| 辅助信息 / 时间戳 | `fg.muted` | warm-grey.600 |
| Placeholder | `fg.subtle` | warm-grey.500 |
| 禁用 | `fg.disabled` | warm-grey.400 |
| 链接 | `fg.link` | blue.600 |
| Agent 标识 | `fg.agent` | violet.600 |

**三条禁令**：
1. **禁止** `fg.muted` 用在 H1–H3 标题上（层级颠倒）
2. **禁止**在 `bg.canvas` / `bg.surface` 上用纯黑 `#000`（过硬·用 warm-grey.900）
3. **禁止**同一段里出现 3 种以上颜色（视觉噪音）

---

## 6. 中英混排规则

### 6.1 标点

- 中文内用中文标点：`，。；：「」`
- 英文内用英文标点：`,.;: " "`
- **中英混排时**：以主语言的标点为准。如 `打开 Settings，然后…`（中文主导，用中文逗号）

### 6.2 间距

中英混排时，CSS 不自动加空格，需**手动加**：

```
✅ 使用 API 调用
✅ 支持 Claude Opus 模型
✅ 共 1,234 条记录

❌ 使用API调用
❌ 支持ClaudeOpus模型
```

### 6.3 字号

中英混排时，**相同视觉大小的中文字号比英文略小**（中文字身更方正，视觉更大）：

```css
.mixed-text {
  font-size: 14px;  /* 英文 14px */
}
.mixed-text-cjk {
  font-size: 13px;  /* 中文稍小，视觉对齐 */
}
```

但这种微调容易复杂化，**默认情况下不做区分**，让两者都用 14px——只有在极高密度场景（表格密度 compact）才启用。

### 6.4 行高

中文字身大，需要更大的行高获得呼吸感：

```css
.en { line-height: 1.5; }      /* 英文可以更紧 */
.cn { line-height: 1.7; }      /* 中文需更松 */
.mixed { line-height: 1.6; }   /* 折中值 */
```

本规范 `type.body.default` 的 line-height = 20 / 14 = 1.43，对纯英文略紧、对纯中文偏紧。
**实践建议**：body 文字如果预期大量中文，override 到 `line-height: 1.6`。

---

## 7. 实现范式（HTML / CSS / Tailwind）

### 7.1 HTML

```html
<h1 class="type-h1">启动您的首个 Agent Workflow</h1>
<p class="type-body">选择一个模板，或从头创建。</p>
<span class="type-caption text-muted">最近编辑：2 hours ago</span>
<span class="type-micro badge">BETA</span>
```

### 7.2 CSS（规范推荐做法）

```css
.type-display-xl { font-family: var(--font-display); font-size: 48px; line-height: 52px; font-weight: 500; letter-spacing: -0.02em; }
.type-display-l  { font-family: var(--font-display); font-size: 36px; line-height: 40px; font-weight: 500; letter-spacing: -0.02em; }
.type-h1         { font-family: var(--font-body);    font-size: 28px; line-height: 34px; font-weight: 600; letter-spacing: -0.015em; }
.type-h2         { font-family: var(--font-body);    font-size: 22px; line-height: 28px; font-weight: 600; letter-spacing: -0.01em; }
.type-h3         { font-family: var(--font-body);    font-size: 18px; line-height: 24px; font-weight: 600; }
.type-body-large { font-family: var(--font-body);    font-size: 16px; line-height: 24px; }
.type-body       { font-family: var(--font-body);    font-size: 14px; line-height: 20px; }
.type-body-small { font-family: var(--font-body);    font-size: 13px; line-height: 18px; }
.type-caption    { font-family: var(--font-body);    font-size: 12px; line-height: 16px; }
.type-micro      { font-family: var(--font-body);    font-size: 11px; line-height: 14px; font-weight: 500; letter-spacing: 0.02em; }

.numeric         { font-variant-numeric: tabular-nums; font-feature-settings: "tnum" 1; }
.code            { font-family: var(--font-mono); font-size: 13px; line-height: 18px; }
```

### 7.3 Tailwind（自定义 utility）

```js
// tailwind.config.js (excerpt)
fontSize: {
  'display-xl': ['48px', { lineHeight: '52px', letterSpacing: '-0.02em', fontWeight: '500' }],
  'display-l':  ['36px', { lineHeight: '40px', letterSpacing: '-0.02em', fontWeight: '500' }],
  'h1':         ['28px', { lineHeight: '34px', letterSpacing: '-0.015em', fontWeight: '600' }],
  'h2':         ['22px', { lineHeight: '28px', letterSpacing: '-0.01em', fontWeight: '600' }],
  'h3':         ['18px', { lineHeight: '24px', fontWeight: '600' }],
  'body-lg':    ['16px', { lineHeight: '24px' }],
  'body':       ['14px', { lineHeight: '20px' }],
  'body-sm':    ['13px', { lineHeight: '18px' }],
  'caption':    ['12px', { lineHeight: '16px' }],
  'micro':      ['11px', { lineHeight: '14px', letterSpacing: '0.02em', fontWeight: '500' }],
}
```

---

## 8. 字体特性（OpenType Features）

高质量 UI 的细节来自这几个特性：

```css
.geist-features {
  font-feature-settings:
    "ss01" 1,  /* Geist 单层 a（美观） */
    "cv11" 1,  /* 单层 l（避免与 1 混淆） */
    "tnum" 1,  /* Tabular figures */
    "calt" 1,  /* Contextual alternates */
    "kern" 1;  /* Kerning */
}
```

Fraunces 尤其值得打开：

```css
.fraunces-features {
  font-feature-settings:
    "ss01" 1,  /* 更 editorial 的 g */
    "kern" 1;
  font-variation-settings:
    "opsz" 72, /* Optical size 适配大字 */
    "SOFT" 50; /* 柔度 0-100 */
}
```

---

## 9. 反例 · Anti-patterns

| ❌ | ✅ |
|---|---|
| 页面混用 5 种字号（14/15/16/17/18…） | 严格 9 档字阶 |
| 表格列对不齐 | 启用 `tabular-nums` |
| H1 用 `font-weight: 900` | H1 = 600 |
| 链接不加下划线且和正文同色 | `fg.link` + `text-decoration: underline` on hover |
| 全大写英文不加 letter-spacing | 全大写必配 `tracking-wide` 0.06em |
| 中文正文 `font-family: Arial` | 中文回落到 `微软雅黑` |
