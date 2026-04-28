# 09 · Data Visualization
> 图表选型 · 配色铁律 · Table 高级模式

---

## 0. 三条不可违反的配色铁律（色觉差异友好）

1. **禁止用"绿涨红跌"作为唯一区分方式**。即便金融上下文，也用 **Amber ↑ / Blue ↓** + **文字前缀符号**。
2. **所有图表的图例必须带 icon 或 pattern**，不只是色块 + 文字（色觉差异用户无法区分近色）。
3. **多系列分类色最多 6 种**。超过 6 种系列的数据应该改用 small multiples 或 table。

---

## 1. 图表类型选择矩阵

| 目的 | 推荐图表 | 不推荐 |
|---|---|---|
| 单一值对比（时间） | Line chart / Area chart | Pie |
| 多维对比（时间） | Stacked bar / Grouped bar | 3D 图 |
| 比例 / 组成 | Bar（水平） / Stacked bar 100% | Pie（超过 3 类） |
| 两变量关系 | Scatter / Bubble | Table |
| 地理分布 | Choropleth map | 柱图强解地理 |
| 排名 | Horizontal bar（从高到低） | 垂直条形图做排名 |
| 漏斗 | Funnel chart | Pie |
| 热力 / 密度 | Heatmap | 任何 3D |
| 流向 | Sankey diagram | 饼图 |
| 时间事件 | Timeline / Gantt | Table |

### 1.1 关键原则

- **Pie chart 最多 3 片**。多了改 horizontal bar。
- **3D 图表永远禁用**。视觉扭曲、无法精确读数。
- **双 Y 轴慎用**（容易误读）。能拆就拆成两个图。
- **起始点从 0**（除非明确标注截断），避免放大微小差异误导。

---

## 2. 分类色（Categorical Colors）

主要用于**多系列折线图**、**堆叠柱图**、**分组柱图**。

### 2.1 标准 6 色

顺序即优先级——2 系列用前 2 种，3 系列用前 3 种，以此类推。

| # | Token | Hex | 视觉 |
|---|---|---|---|
| 1 | `dataviz.cat.1` | `#A36E10` (amber.600) | 深琥珀 |
| 2 | `dataviz.cat.2` | `#1E5189` (blue.600) | 靛青 |
| 3 | `dataviz.cat.3` | `#1B6F62` (teal.600) | 青绿 |
| 4 | `dataviz.cat.4` | `#5A3F94` (violet.600) | 紫 |
| 5 | `dataviz.cat.5` | `#5C564B` (warm-grey.600) | 暖灰 |
| 6 | `dataviz.cat.6` | `#8A6402` (yellow.700) | 橄榄黄 |

### 2.2 模式 / 纹理（色觉差异友好增强）

当系列 ≥ 3 时，**除了颜色还加 pattern**：

```css
.series-1 { fill: var(--dataviz-cat-1); }
.series-2 { fill: var(--dataviz-cat-2); stroke-dasharray: 4 2; } /* 虚线 */
.series-3 { fill: url(#diagonal-stripes); }                      /* 斜纹 */
.series-4 { fill: url(#dots); }                                   /* 点纹 */
```

SVG pattern 定义：

```html
<svg>
  <defs>
    <pattern id="diagonal-stripes" patternUnits="userSpaceOnUse" width="6" height="6">
      <rect width="6" height="6" fill="var(--dataviz-cat-3)"/>
      <line x1="0" y1="6" x2="6" y2="0" stroke="rgba(255,255,255,0.5)" stroke-width="1"/>
    </pattern>
  </defs>
</svg>
```

---

## 3. 渐变色（Sequential）

用于**热力图**、**单系列强度**（如地图密度）。

### 3.1 Amber 序列（推荐默认）

```css
.seq-amber-0 { fill: var(--color-amber-50); }   /* #FDF8EE */
.seq-amber-1 { fill: var(--color-amber-200); }  /* #F5D88F */
.seq-amber-2 { fill: var(--color-amber-400); }  /* #E4A72E */
.seq-amber-3 { fill: var(--color-amber-600); }  /* #A36E10 */
.seq-amber-4 { fill: var(--color-amber-800); }  /* #5E400B */
```

### 3.2 Blue 序列（次选）

```css
.seq-blue-0 { fill: var(--color-blue-50); }
.seq-blue-1 { fill: var(--color-blue-200); }
.seq-blue-2 { fill: var(--color-blue-400); }
.seq-blue-3 { fill: var(--color-blue-600); }
.seq-blue-4 { fill: var(--color-blue-800); }
```

---

## 4. 双向发散色（Diverging）

用于**盈亏**、**好坏**、**高于/低于平均** 等双向对比。

```
负 ←────── 0 ──────→ 正
Blue     Neutral    Amber
```

```css
.div--3 { fill: var(--color-blue-700); }
.div--2 { fill: var(--color-blue-500); }
.div--1 { fill: var(--color-blue-200); }
.div-0  { fill: var(--color-warm-grey-200); }
.div-+1 { fill: var(--color-amber-200); }
.div-+2 { fill: var(--color-amber-500); }
.div-+3 { fill: var(--color-amber-700); }
```

---

## 5. 图表组件规范

### 5.1 图表卡片（Chart Card）

所有图表应该放在一个**标准卡片**里：

```html
<section class="chart-card">
  <header class="chart-header">
    <div>
      <h3 class="chart-title">Revenue by month</h3>
      <p class="chart-subtitle">Last 12 months · Updated 2 hours ago</p>
    </div>
    <div class="chart-actions">
      <div class="segmented-control">
        <button aria-pressed="false">6M</button>
        <button aria-pressed="true">12M</button>
        <button aria-pressed="false">24M</button>
      </div>
      <button class="btn-ghost btn-sm">⋯</button>
    </div>
  </header>

  <div class="chart-body">
    <!-- SVG chart here -->
  </div>

  <footer class="chart-legend">
    <div class="legend-item">
      <span class="legend-swatch" style="background:var(--dataviz-cat-1)"></span>
      <span>Enterprise</span>
      <span class="legend-value">¥4.56M</span>
    </div>
    <div class="legend-item">
      <span class="legend-swatch" style="background:var(--dataviz-cat-2)"></span>
      <span>SMB</span>
      <span class="legend-value">¥2.34M</span>
    </div>
  </footer>
</section>
```

```css
.chart-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
}

.chart-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--space-4);
  gap: var(--space-4);
}

.chart-title {
  font-size: 16px;
  line-height: 24px;
  font-weight: 600;
  color: var(--fg-strong);
}

.chart-subtitle {
  font-size: 12px;
  color: var(--fg-muted);
  margin-top: var(--space-1);
}

.chart-body {
  height: 320px;       /* 默认 · 可调 */
  width: 100%;
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4) var(--space-6);
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-subtle);
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 12px;
  color: var(--fg-muted);
}

.legend-swatch {
  width: 10px;
  height: 10px;
  border-radius: var(--radius-xs);
  flex-shrink: 0;
}

.legend-value {
  margin-left: var(--space-1);
  font-variant-numeric: tabular-nums;
  color: var(--fg-default);
  font-weight: 500;
}
```

### 5.2 Axis 轴线

```css
.axis-line  { stroke: var(--dataviz-axis); stroke-width: 1; }
.axis-tick  { stroke: var(--dataviz-axis); stroke-width: 1; }
.axis-label { fill: var(--dataviz-label); font-size: 11px; font-family: var(--font-body); }
.grid-line  { stroke: var(--dataviz-grid); stroke-width: 1; stroke-dasharray: 2 3; }
```

**硬规**：
- Y 轴 grid line 用 **虚线**（不干扰主数据）
- X 轴不画 grid line（避免过密）
- Label 用 11px, tabular-nums

### 5.3 Tooltip（图表悬停）

```
┌─────────────────────────┐
│ Jan 2026                │ ← 日期标题
│ ─────                   │
│ ● Enterprise   ¥456K    │ ← tabular-nums · 右对齐
│ ● SMB          ¥234K    │
│ ─────                   │
│ Total          ¥690K    │ ← bold
└─────────────────────────┘
```

```css
.chart-tooltip {
  background: var(--dataviz-tooltip-bg);
  color: var(--dataviz-tooltip-fg);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  font-size: 12px;
  line-height: 16px;
  box-shadow: var(--shadow-lg);
  pointer-events: none;
  font-variant-numeric: tabular-nums;
  min-width: 140px;
}
.chart-tooltip-title {
  font-weight: 500;
  padding-bottom: var(--space-1);
  border-bottom: 1px solid rgba(255,255,255,0.1);
  margin-bottom: var(--space-1);
}
.chart-tooltip-row {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
}
.chart-tooltip-row .swatch {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: var(--space-1);
}
```

### 5.4 空状态 & 加载态

```
┌────────────────────────────────┐
│ Revenue by month               │
├────────────────────────────────┤
│                                │
│       📊                       │
│    No data yet                 │
│    Start tracking to see        │
│    your trends here.            │
│                                │
└────────────────────────────────┘
```

Loading state: skeleton 覆盖 chart area，高度匹配：

```html
<div class="chart-body">
  <div class="skeleton skeleton-rect" style="width:100%;height:100%"></div>
</div>
```

---

## 6. Data Table 高级模式

基础 Table 见 `06-components.md`。这里补充高密度数据场景的进阶模式。

### 6.1 Frozen Columns（冻结列）

长宽表格中，首列（通常是 name / ID）应该 **sticky left**：

```css
.table .col-sticky-left {
  position: sticky;
  left: 0;
  background: inherit;
  z-index: 1;
  box-shadow: 1px 0 0 var(--border-subtle);
}
.table tbody tr:hover .col-sticky-left { background: var(--bg-hover); }
.table tbody tr[aria-selected="true"] .col-sticky-left { background: var(--bg-selected); }
```

### 6.2 Column Groups（列分组）

```
┌─────────────┬──────────────────────┬────────────────────┐
│             │      Revenue         │     Cost            │
│  Customer   ├────────┬────────┬────┼────────┬────────┬──┤
│             │  Q1    │  Q2    │ Q3 │  Q1    │  Q2    │..│
├─────────────┼────────┼────────┼────┼────────┼────────┼──┤
│ Alice Chen  │ ¥120K  │ ¥135K  │ …  │  ¥45K  │  ¥50K  │..│
```

```html
<thead>
  <tr class="table-group-header">
    <th rowspan="2">Customer</th>
    <th colspan="3" class="group-revenue">Revenue</th>
    <th colspan="3" class="group-cost">Cost</th>
  </tr>
  <tr>
    <th class="col-numeric">Q1</th>
    <th class="col-numeric">Q2</th>
    <th class="col-numeric">Q3</th>
    <th class="col-numeric">Q1</th>
    <th class="col-numeric">Q2</th>
    <th class="col-numeric">Q3</th>
  </tr>
</thead>
```

### 6.3 Inline 编辑

双击单元格直接进入编辑模式：

```
Default:        [1,234]
dblclick →      [┌───────┐]
                [│ 1234  │]   ← input
                [└───────┘]
                [Enter] save / [Esc] cancel
```

```css
.table td[contenteditable="true"] {
  outline: 2px solid var(--border-focus);
  outline-offset: -2px;
  background: var(--bg-surface);
  padding: 0 var(--space-3);
}
```

### 6.4 Cell Types（单元格类型）

| 类型 | 对齐 | 特殊样式 |
|---|---|---|
| text | left | — |
| numeric | **right** | `tabular-nums` + monospaced 可选 |
| currency | right | tabular-nums + 前缀符号 |
| date | left | ISO 或 locale |
| status | left | badge |
| action | right | icon button |
| checkbox | center | width: 40px fixed |

```css
.cell-numeric    { text-align: right; font-variant-numeric: tabular-nums; }
.cell-currency   { text-align: right; font-variant-numeric: tabular-nums; }
.cell-currency .currency-symbol { color: var(--fg-muted); margin-right: 2px; }
.cell-date       { font-variant-numeric: tabular-nums; color: var(--fg-default); }
.cell-date-rel   { color: var(--fg-muted); font-size: 12px; }  /* "2 days ago" */
.cell-action     { text-align: right; width: 1%; white-space: nowrap; }
.cell-checkbox   { width: 40px; padding-left: var(--space-3); }
```

### 6.5 Row States（行状态）

```css
.row-selected        { background: var(--bg-selected); }
.row-dimmed          { opacity: 0.5; }            /* 筛选外 */
.row-highlighted     {
  background: var(--bg-agent-surface);            /* Agent 高亮 */
  border-left: 2px solid var(--border-agent);
}
.row-new { animation: rowFadeIn 400ms var(--motion-ease-out); }
@keyframes rowFadeIn {
  from { background: var(--intent-positive-surface); }
  to   { background: transparent; }
}
```

### 6.6 Sorting & Filtering UI

排序箭头显示在 header 右侧，**使用 Amber 色**而非绿色：

```
┌──────────────────┐
│ Customer Name ↑  │  ← 升序
│ Amount ↓         │  ← 降序
│ Date             │  ← 未排序
└──────────────────┘
```

Filter 图标在 header 右侧显示，激活后填充：

```
┌──────────────────┐
│ Status    ⊗      │  ← 已过滤 · amber filled
│ Region    ▽      │  ← 未过滤 · 灰空心
└──────────────────┘
```

---

## 7. Sparkline（微型趋势图）

在表格单元格内嵌入小趋势图：

```
┌─────────┬──────────────┬─────────┐
│ Product │ Trend (30d)  │ Change  │
├─────────┼──────────────┼─────────┤
│ Plan A  │ ▁▂▄▅▇█▆▄▂   │ ↑ 12%  │
│ Plan B  │ █▇▆▇█▅▃▂▁   │ ↓  8%  │
└─────────┴──────────────┴─────────┘
  sparkline height: 20px
  color: dataviz.cat.1 (amber)
```

```html
<svg class="sparkline" width="80" height="20" viewBox="0 0 80 20">
  <polyline points="0,18 10,14 20,10 ... 80,4"
            fill="none"
            stroke="var(--dataviz-cat-1)"
            stroke-width="1.5"
            stroke-linecap="round"/>
</svg>
```

---

## 8. 数字格式化规则

### 8.1 千分位

| Locale | Format |
|---|---|
| `en-US` | `12,345.67` |
| `zh-CN` | `12,345.67` （本规范统一用英文习惯） |

### 8.2 货币

| Scenario | Format |
|---|---|
| 人民币 | `¥12,345.67` |
| 美元 | `$12,345.67` |
| 港币 | `HK$ 12,345` |
| 万 | `¥1.23 万` 或 `¥12,345` |
| 亿 | `¥1.23 亿` 或 `¥123.45M` |

### 8.3 百分比

| Scenario | Format |
|---|---|
| 增长 | `+12.3%` |
| 下降 | `-8.1%` |
| 持平 | `0.0%` 或 `—` |

### 8.4 时间

| Scenario | Format |
|---|---|
| 绝对日期 | `Apr 21, 2026` / `2026-04-21` |
| 时间戳 | `14:32` / `2:32 PM` |
| 相对 | `2 hours ago` / `2 天前` |
| 持续时长 | `2.4s` / `1 min 35s` / `2h 15min` |

---

## 9. 反例

| ❌ | ✅ |
|---|---|
| 饼图 8 片 | 水平条形图 |
| 3D 柱图 | 2D 柱图 |
| 股价默认红跌绿涨（色盲无法区分） | 前缀符号 ↑↓ + Amber/Blue |
| 图表标题超过 1 行 | 简洁名词短语 |
| 数值显示 `1234567` 无千分位 | `1,234,567` |
| Y 轴从 500 开始（视觉放大） | 从 0 开始或明确标注 truncated axis |
| 图例只有色块 + 文字 | 色块 + pattern + 文字 |
