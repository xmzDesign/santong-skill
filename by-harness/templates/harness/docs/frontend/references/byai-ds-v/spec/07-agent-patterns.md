# 07 · Agent-Native Patterns ★
> Streaming · Tool Call · Reasoning Trace · HITL · Citation · Artifact · Context · Orchestration

---

## 这份文档是全规范最重要的模块

传统 B2B 设计系统（Material, Polaris, Carbon）几乎不涉及 Agent 交互——它们诞生在 Agent 成为主流之前。
BYAI 的独特性在于：**把 Agent 的不确定性与专业工具的信息严谨性调和**。

---

## 核心契约（读这一段就是半壁江山）

### 1. 一切 Agent 行为必须可见

任何非用户触发的变化——工具调用、数据读写、外部请求、状态决策——必须在 UI 上有可见痕迹。
用户的预设是"AI 在偷偷做事"，我们的设计目的是**消除这种不信任**。

### 2. 一切 Agent 决策必须可解释

Agent 产生的每一个结论、每一段输出，都要能追溯到**数据来源或推理链条**。Citation 不是锦上添花，是必需品。

### 3. 一切不可逆操作必须 HITL（Human-in-the-Loop）

发邮件、改客户数据、扣款、删除——任何会产生外部影响或数据丢失的动作，Agent 只能**提议**，不能**执行**。
由用户明确点击"Approve"后才执行。

### 4. 一切流式输出必须可中断

Streaming 过程中，"Stop" 按钮必须始终可见且可点击。中断后保留已产生的内容。

### 5. Agent 视觉语言必须与人类行为视觉区分

**Violet 专属 Agent**。人类的行为继续使用 amber / blue / neutral。这是色彩编码的公共合约。

---

## 1. Message Bubble（对话气泡）

### 1.1 结构

```
User message:                              AI / Agent message:
┌──────────────────────────────┐           ┌──────────────────────────────────┐
│                              │           │ [✨] BYAI Copilot              │
│       ┌─────────────────────┐│           │ ─────────────────────────────    │
│       │ Help me analyze the ││           │ Based on your Q1 data, revenue    │
│       │ Q1 revenue.         ││           │ grew 12.3% YoY, driven primarily  │
│       └─────────────────────┘│           │ by the Enterprise segment...      │
│                  — You · 14:32│           │                                  │
└──────────────────────────────┘           │ [1] [2] [3]                       │
                                           │ — 14:33 · 8.2s · 234 tokens      │
                                           └──────────────────────────────────┘

Alignment: right (user)                    Alignment: left (agent), full-width friendly
Background: bg.surface (neutral)           Background: bg.agent.surface (violet.50)
Border-radius: 12px (both)
```

### 1.2 CSS

```css
/* Message item */
.message {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  max-width: 100%;
  padding: var(--space-4) 0;
}

/* User message */
.message-user {
  align-items: flex-end;
}
.message-user .message-bubble {
  background: var(--bg-surface);
  color: var(--fg-default);
  border: 1px solid var(--border-subtle);
  max-width: 70%;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-xl);
  border-bottom-right-radius: var(--radius-xs); /* tail */
}

/* Agent message */
.message-agent {
  align-items: flex-start;
}
.message-agent .message-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}
.message-agent .avatar {
  width: 24px;
  height: 24px;
  background: var(--bg-agent-surface);
  color: var(--fg-agent);
  border-radius: 9999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}
.message-agent .agent-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--fg-agent);
}
.message-agent .message-bubble {
  width: 100%;
  padding: var(--space-4);
  background: var(--bg-agent-surface);
  color: var(--fg-default);
  border: 1px solid var(--agent-border-default);
  border-radius: var(--radius-lg);
  line-height: 1.6;
}

/* Metadata below bubble */
.message-meta {
  display: flex;
  gap: var(--space-2);
  font-size: 11px;
  color: var(--fg-muted);
  font-variant-numeric: tabular-nums;
  margin-top: var(--space-2);
}
.message-meta > * + *::before {
  content: "·";
  margin-right: var(--space-2);
}
```

### 1.3 HTML（Agent message 完整示例）

```html
<div class="message message-agent">
  <div class="message-header">
    <span class="avatar" aria-label="Agent avatar">✨</span>
    <span class="agent-name">BYAI Copilot</span>
    <span class="badge badge-agent badge-sm">GPT-4o</span>
  </div>

  <div class="message-bubble">
    <p>Based on your Q1 data, revenue grew <strong>12.3% YoY</strong>, driven primarily by the Enterprise segment.</p>

    <ul class="citation-refs">
      <li>
        <button class="citation-chip" aria-label="View source 1">
          <span class="citation-num">1</span>
          <span class="citation-title">Q1_Revenue_Report.xlsx</span>
        </button>
      </li>
      <li>
        <button class="citation-chip" aria-label="View source 2">
          <span class="citation-num">2</span>
          <span class="citation-title">Sales_Dashboard</span>
        </button>
      </li>
    </ul>
  </div>

  <div class="message-meta">
    <time datetime="2026-04-21T14:33">14:33</time>
    <span>8.2s</span>
    <span>234 tokens</span>
    <button class="btn-ghost btn-xs" aria-label="Copy message">📋 Copy</button>
    <button class="btn-ghost btn-xs" aria-label="Regenerate">↻ Regenerate</button>
    <button class="btn-ghost btn-xs" aria-label="Helpful">👍</button>
    <button class="btn-ghost btn-xs" aria-label="Not helpful">👎</button>
  </div>
</div>
```

### 1.4 Agent Avatar 规范

**重要**：不用拟人化头像（不要设计成一个"小机器人脸"或拟真照片）。
推荐：抽象几何（如 Claude 的扭结 glyph）或符号（✨、◆、●）。

**为什么**：拟人化会抬高用户对 Agent 能力的预期，一旦失败更挫败。抽象符号反而传达"这是工具"的准确预期。

---

## 2. Streaming（流式输出）

### 2.1 光标指示

流式 token 输出时，末尾有一个**呼吸光标**：

```
...driven primarily by the Enterprise segment▊
                                              ↑ 闪烁 amber 光标
```

```css
.streaming-cursor {
  display: inline-block;
  width: 2px;
  height: 1.1em;
  background: var(--agent-indicator-streaming);
  vertical-align: text-bottom;
  margin-left: 2px;
  animation: cursor-blink 1s var(--motion-ease-in-out) infinite;
}
@keyframes cursor-blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.3; }
}
```

### 2.2 Stop 按钮（最重要）

**硬规**：流式进行中，每个 Agent message 下方必须有 **"Stop" 按钮**。

```html
<div class="message-bubble" data-streaming="true">
  <p>...driven primarily by the Enterprise<span class="streaming-cursor"></span></p>
</div>
<div class="streaming-actions">
  <button class="btn btn-secondary btn-sm" aria-keyshortcuts="Escape">
    <svg aria-hidden="true">■</svg>
    Stop generating
    <kbd class="kbd">Esc</kbd>
  </button>
</div>
```

### 2.3 流式完成过渡

流式结束时：
1. 光标消失
2. 出现 metadata（时长、token 数、citation chips）
3. 如果内容有 code / table / artifact，淡入渲染增强版

**反例**：流式结束后突然"跳"到完成态（内容闪烁）。**应该**：
- 用 `animation: fadeIn 200ms` 渐入 metadata 和 actions
- 保留已有文字不重绘

---

## 3. Thinking / Reasoning Trace（思考过程）

Agent 有两种呈现模式：
- **Default**：仅展示结论
- **With trace**：结论前展示折叠的"思考过程"

### 3.1 视觉结构

```
┌────────────────────────────────────────────────────┐
│ [✨] BYAI Copilot                               │
│                                                    │
│ ┌────────────────────────────────────────────────┐│
│ │ ▸ Thinking...  4s                              ││  ← 折叠状态 · bg.agent.trace
│ └────────────────────────────────────────────────┘│
│                                                    │
│ Based on your data, the revenue grew...            │
└────────────────────────────────────────────────────┘

  展开后：
┌────────────────────────────────────────────────────┐
│ ▼ Reasoning  8 steps · 12s                         │
│ ────────────────────────────────────               │
│  1. I need to query the Q1 revenue table...       │
│  2. The user is asking about YoY growth...        │
│  3. Let me use the analyze_revenue tool...        │
│  4. The result shows enterprise segment at 45%... │
│  ...                                               │
└────────────────────────────────────────────────────┘
```

### 3.2 CSS

```css
.reasoning-trace {
  background: var(--bg-agent-trace);
  border: 1px solid var(--agent-border-default);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-3);
  overflow: hidden;
}

.reasoning-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  font-size: 12px;
  color: var(--fg-agent);
  font-weight: 500;
}

.reasoning-trigger .chevron {
  transition: transform var(--motion-duration-fast) var(--motion-ease-out);
}

.reasoning-trigger[aria-expanded="true"] .chevron {
  transform: rotate(90deg);
}

.reasoning-content {
  padding: var(--space-2) var(--space-4) var(--space-4) var(--space-8);
  border-top: 1px solid var(--agent-border-default);
  font-family: var(--font-mono);
  font-size: 12px;
  line-height: 1.6;
  color: var(--fg-muted);
  max-height: 240px;
  overflow-y: auto;
}

.reasoning-step {
  position: relative;
  padding-left: var(--space-5);
  margin-bottom: var(--space-2);
}
.reasoning-step::before {
  content: attr(data-step);
  position: absolute;
  left: 0;
  top: 0;
  color: var(--fg-agent);
  font-weight: 500;
}
```

### 3.3 Streaming thinking

思考阶段 streaming 时，trigger 显示 **"Thinking..."** + 呼吸动画 + elapsed time：

```
▸ Thinking... ● 4s
           ↑ 小点呼吸 · violet
```

---

## 4. Tool Call（工具调用展示）★

这是本规范最有价值的原创模式——当 Agent 调用外部工具（数据库查询、API、代码执行）时，UI 必须显式展示。

### 4.1 三种形态

| 形态 | 何时使用 |
|---|---|
| **Inline card**（默认） | Tool 快速返回 < 2s |
| **Live log**（展开） | Tool 需要较长时间 / 多步骤 |
| **Collapsible summary** | Tool 已完成 · 折叠进 message |

### 4.2 Inline Card 结构

```
┌─────────────────────────────────────────────────────────┐
│ 🔧 query_database                           Status ✓    │
│ ────────────────────────────────────                    │
│ Input:                                                  │
│   table: sales_2026_q1                                  │
│   filter: segment = "Enterprise"                        │
│                                                         │
│ Output:                                                 │
│   Returned 1,234 rows in 240ms                          │
│   [▸ View results]                                      │
└─────────────────────────────────────────────────────────┘
```

### 4.3 CSS

```css
.tool-call {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-left: 3px solid var(--agent-indicator-tool);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-3);
  overflow: hidden;
  font-family: var(--font-mono);
  font-size: 12px;
}

.tool-call-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--bg-surface-sunken);
  border-bottom: 1px solid var(--border-subtle);
}

.tool-call-name {
  color: var(--agent-indicator-tool);
  font-weight: 500;
  flex: 1;
}

.tool-call-status {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: 11px;
}
.tool-call-status[data-state="running"] { color: var(--fg-muted); }
.tool-call-status[data-state="success"] { color: var(--fg-brand); }
.tool-call-status[data-state="error"]   { color: var(--intent-danger-text); }

.tool-call-body {
  padding: var(--space-3);
  display: grid;
  gap: var(--space-3);
}

.tool-call-section-label {
  color: var(--fg-muted);
  font-size: 10px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.tool-call-content {
  color: var(--fg-default);
  white-space: pre-wrap;
  word-break: break-word;
}
```

### 4.4 HTML

```html
<div class="tool-call" role="region" aria-label="Tool call: query_database">
  <div class="tool-call-header">
    <svg class="icon" aria-hidden="true">🔧</svg>
    <span class="tool-call-name">query_database</span>
    <span class="tool-call-status" data-state="success">
      <svg aria-hidden="true">✓</svg>
      <span>240ms</span>
    </span>
  </div>
  <div class="tool-call-body">
    <div>
      <div class="tool-call-section-label">Input</div>
      <pre class="tool-call-content">{
  "table": "sales_2026_q1",
  "filter": "segment = 'Enterprise'"
}</pre>
    </div>
    <div>
      <div class="tool-call-section-label">Output</div>
      <div class="tool-call-content">Returned 1,234 rows</div>
      <button class="btn btn-ghost btn-sm">▸ View results</button>
    </div>
  </div>
</div>
```

### 4.5 状态规范

| Status | Color | Icon | Label |
|---|---|---|---|
| pending | warm-grey | ○ | Waiting |
| running | blue + spinner | ⏵ | Running... |
| success | amber | ✓ | 完成 · 耗时 |
| error | red | ✕ | Failed |
| cancelled | warm-grey | ■ | Cancelled |

---

## 5. HITL Approval（人在环中审批）★

Agent 提出**产生外部影响**的操作时，必须阻塞等待用户批准。

### 5.1 什么场景触发 HITL？

- 发送邮件 / 短信 / 站内通知给其他用户
- 创建 / 修改 / 删除 客户、订单、付款等业务记录
- 执行 API 调用（尤其 mutation 型）
- 支付 / 扣费 / 资金转移
- 代码部署 / 运行生产脚本
- 授权 / 权限变更

**简单检查**："如果 Agent 做错了这件事，用户会 5 分钟内感到痛苦吗？" 如是，上 HITL。

### 5.2 Approval Card 结构

```
┌─────────────────────────────────────────────────────────────┐
│  ⚠  Confirm before proceeding                               │
│  ──────────────────────────────────────                     │
│                                                             │
│  I'd like to send the following email to 3 customers:      │
│                                                             │
│  ┌─────────────────────────────────────────────┐           │
│  │ To: Alice, Bob, Carol                       │           │
│  │ Subject: Your Q1 report is ready            │           │
│  │ ───────────                                 │           │
│  │ Hi [name],                                  │  ← preview │
│  │ Your Q1 financial report is attached.       │           │
│  │ ...                                         │           │
│  └─────────────────────────────────────────────┘           │
│                                                             │
│  ▸ Show 2 more recipients                                   │
│                                                             │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐      │
│  │ ✕ Decline    │  │ ✎ Edit      │  │ ✓ Approve    │      │
│  └──────────────┘  └─────────────┘  └──────────────┘      │
│                                         Primary CTA         │
└─────────────────────────────────────────────────────────────┘
  background: bg.surface
  border: 2px solid intent.warning.border (yellow.300)
  border-radius: radius.lg
```

### 5.3 CSS

```css
.approval-card {
  background: var(--bg-surface);
  border: 2px solid var(--intent-warning-surface); /* warmer yellow border */
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  margin-bottom: var(--space-3);
}

.approval-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
  font-weight: 600;
  color: var(--intent-warning-text);
}

.approval-preview {
  background: var(--bg-surface-sunken);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  font-size: 13px;
  margin-block: var(--space-3);
  max-height: 200px;
  overflow-y: auto;
}

.approval-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
}
```

### 5.4 三态强制

**硬规**：HITL approval 必须提供三个选项：

1. **Approve**（主按钮）— 允许执行
2. **Edit**（次按钮）— 修改后再执行
3. **Decline**（幽灵按钮）— 拒绝并告诉 Agent 原因

绝对不能只有 "Approve / Decline" 两态——用户经常"大致对但差一点"，必须给 Edit 出口。

### 5.5 多步审批（批量操作）

对于"给 50 个客户发邮件"这类：

```
┌────────────────────────────────────┐
│  ⚠  Approve 50 operations?         │
│  ────────────────                  │
│  ☑  Review all individually (~5min)│
│  ☐  Sample 3 and apply to all      │
│  ☐  Approve all without review     │ ← 禁用此项直到用户打字确认理解风险
└────────────────────────────────────┘
```

---

## 6. Citation（引用）

### 6.1 Inline Chip

Agent 文字中引用来源，嵌入编号 chip：

```
Revenue grew 12.3% YoY [1], driven primarily by Enterprise [2][3].
```

```css
.citation-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 18px;
  padding: 0 4px;
  background: var(--agent-citation-bg);
  color: var(--fg-agent);
  border-radius: var(--radius-xs);
  font-size: 10px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  vertical-align: baseline;
  border: none;
  cursor: pointer;
  margin-inline: 2px;
  transition: background var(--motion-duration-fast);
}
.citation-chip:hover {
  background: var(--intent-neutral-bg);
}
```

### 6.2 Citation Tooltip

Hover chip 展示源文档 preview：

```
┌────────────────────────────────────────┐
│  📄 Q1_Revenue_Report.xlsx             │
│  Sheet 2, Row 14                       │
│  ────────────────                      │
│  "Enterprise segment generated         │
│   ¥456,320 in Q1, up 12.3% YoY."      │
│  ────────────────                      │
│  [Open source] [Copy link]             │
└────────────────────────────────────────┘
```

### 6.3 Citation Panel（底部面板）

消息底部列出所有引用：

```
────────────────────────────
Sources
[1]  Q1_Revenue_Report.xlsx     Updated 2 days ago
[2]  Sales_Dashboard            Live
[3]  Enterprise_Contracts.md    Updated 1 week ago
```

**硬规**：任何基于数据 / 文档 / 搜索的结论必须有 citation。**无 citation 的数字或断言是未经验证的，Agent 应该提醒用户**。

---

## 7. Artifact（生成物 / 长内容）

当 Agent 生成的内容超过消息气泡（代码、文档、表格、图表），应该拆分到 **Artifact Canvas**——独立的编辑 / 预览区域。

### 7.1 触发条件

- 代码 > 20 行
- 文档 > 200 字 / 10 段落
- 表格 > 10 行
- 图表 / SVG / HTML 可视化
- 用户明确说 "write a doc" / "create a..."

### 7.2 布局

```
┌─────────────┬──────────────────────────────────────┐
│             │  Artifact: Q1_Report.md              │
│             │  ─────────────────                   │
│  Chat       │  [Preview] [Code] [History]          │
│  messages   │  ───────────────                     │
│  (左侧)     │                                      │
│             │  # Q1 Revenue Report                 │
│             │                                      │
│             │  Revenue reached ¥1,245,800...       │
│             │                                      │
│             │  ...                                 │
│             │                                      │
│             │  [Download .md] [Download .pdf]      │
└─────────────┴──────────────────────────────────────┘
  Chat: 400px     Canvas: flex-1
```

### 7.3 Artifact Header

```html
<header class="artifact-header">
  <div class="artifact-title">
    <svg class="icon">📄</svg>
    <span>Q1_Report.md</span>
    <span class="badge badge-agent badge-sm">v3</span>
  </div>
  <div class="artifact-tabs">
    <button class="tab" aria-selected="true">Preview</button>
    <button class="tab">Code</button>
    <button class="tab">History</button>
  </div>
  <div class="artifact-actions">
    <button class="btn btn-ghost btn-sm">📋 Copy</button>
    <button class="btn btn-ghost btn-sm">⬇ Download</button>
    <button class="btn btn-secondary btn-sm">✎ Edit</button>
  </div>
</header>
```

### 7.4 Artifact Version History

Agent 每次修改 artifact，保留历史版本——用户可对比和回滚：

```
Artifact history:
  v3  ← 当前       2 minutes ago    "Add Enterprise breakdown"
  v2                10 minutes ago   "Fix currency format"
  v1                1 hour ago       "Initial draft"
```

---

## 8. Context Window 可视化 ★

Agent 的上下文窗口有限，让用户能看见"记住了什么 / 塞入了什么 / 快满了吗"。

### 8.1 Context Bar

在 Agent Copilot 顶部展示上下文状态：

```
┌──────────────────────────────────────────────────────────┐
│ Context: 34,280 / 200,000 tokens  ████░░░░░░░░ 17%  ℹ    │
└──────────────────────────────────────────────────────────┘
   border-bottom: border.subtle
   padding: space.2 space.4
   font-size: 11px
```

### 8.2 Context Drawer（点击 ℹ 打开）

```
┌──────────────────────────────────────────┐
│ What's in context                   [✕]  │
│ ───────────────────────                  │
│                                          │
│ 📎 Attached files                        │
│   ▸ Q1_Revenue.xlsx      12,400 tokens  │
│   ▸ Sales_Rules.md        2,300 tokens  │
│                                          │
│ 🔧 Connected tools                       │
│   ▸ query_database                       │
│   ▸ send_email                           │
│                                          │
│ 💬 Messages this session: 14             │
│   (14,800 tokens)                        │
│                                          │
│ 🧠 System prompt         4,780 tokens   │
│                                          │
│ ────────                                 │
│ Total 34,280 / 200,000 · 17% used       │
│ [Remove files] [Clear chat]              │
└──────────────────────────────────────────┘
```

### 8.3 警告阈值

| 使用率 | 视觉 | Action |
|---|---|---|
| 0–70% | amber bar | 无 |
| 70–90% | yellow bar + ⚠ | 显示 "Context filling up" hint |
| > 90% | red-ish | 弹 banner 建议清理或新开会话 |

---

## 9. Multi-Agent Orchestration（多 Agent 编排）

BYAI 支持多个 Agent 协作（如 Planner + Coder + Reviewer）。UI 规范：

### 9.1 Agent Chip 标识

每条消息左侧 avatar 显示不同 Agent 的**颜色 / 图标组合**（都在 violet 色系里变化）：

| Agent | Avatar | 颜色变体 |
|---|---|---|
| Orchestrator | ✨ | violet.600 |
| Analyst | 📊 | violet.500 + amber ring |
| Coder | ⌘ | violet.500 + blue ring |
| Reviewer | ✓ | violet.500 + warm-grey ring |

### 9.2 Handoff 显示

当一个 Agent 把任务交给另一个时，显示 handoff bar：

```
────────────────────────────────
  Planner → Coder
  Task: Implement the filter logic
────────────────────────────────
```

```css
.handoff {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-2);
  margin-block: var(--space-4);
  font-size: 11px;
  color: var(--fg-agent);
  letter-spacing: 0.02em;
}
.handoff::before, .handoff::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--agent-border-default);
}
```

### 9.3 Parallel Agents（并行视图）

多个 Agent 同时工作时，用 **分栏 progress**（不是顺序消息流）：

```
┌──────────────────────────────────────────────┐
│ 3 agents working in parallel                  │
├───────────────┬───────────────┬──────────────┤
│ 📊 Analyst    │ ⌘ Coder       │ ✓ Reviewer  │
│ ▓▓▓▓░░░ 40%   │ ▓▓▓▓▓▓▓ 80%   │ ░░░░░░ pend │
│ Pulling data  │ Writing API   │ Waiting     │
└───────────────┴───────────────┴──────────────┘
```

---

## 10. Composer（输入框·比普通 chat 复杂）

Agent Copilot 底部的输入框不是简单 textarea，而是**多模态 composer**：

### 10.1 结构

```
┌────────────────────────────────────────────────────────────┐
│ [📎] 2 files attached                                       │ ← 附件条 · 条件显示
│  ┌─────────────────┐ ┌─────────────────┐                  │
│  │ Q1_Revenue.xlsx │ │ Rules.md        │                  │
│  └─────────────────┘ └─────────────────┘                  │
├────────────────────────────────────────────────────────────┤
│  Ask BYAI anything or / for commands...                   │ ← 输入区
│                                                            │
├────────────────────────────────────────────────────────────┤
│  [📎] [🔧 Tools▾] [Model: GPT-4o▾]     [⏎ Send]  [⌘⏎]     │ ← 工具条
└────────────────────────────────────────────────────────────┘
```

### 10.2 Slash Commands

`/` 触发命令菜单：

```
/summarize      Summarize the current page
/export         Export chat to markdown
/analyze        Analyze data in attached file
/suggest        Suggest next steps
/switch         Switch model or agent
```

### 10.3 @ Mentions

`@` 触发实体引用：

```
@alice          Alice Chen (Customer)
@q1-report      Q1 Revenue Report (Document)
@send-email     Send Email (Tool)
```

### 10.4 Composer CSS

```css
.composer {
  position: sticky;
  bottom: 0;
  background: var(--bg-surface);
  border-top: 1px solid var(--border-default);
  padding: var(--space-3) var(--space-4);
}

.composer-input {
  width: 100%;
  min-height: 40px;
  max-height: 200px;
  padding: var(--space-2);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: 14px;
  resize: none;
  outline: none;
  transition: border-color var(--motion-duration-fast);
}
.composer-input:focus {
  border-color: var(--border-focus);
  box-shadow: var(--shadow-focus-ring);
}

.composer-toolbar {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-2);
}
.composer-toolbar .spacer { flex: 1; }
```

### 10.5 快捷键

| Key | Action |
|---|---|
| `⏎` | 换行（默认） |
| `⌘⏎` / `Ctrl+⏎` | 发送 |
| `Esc` | 清空或关闭 |
| `/` | Slash command |
| `@` | Mention |
| `↑` | Edit last message |

**硬规**：发送键是 `⌘⏎`，**不是**单独 `Enter`。B2B 用户大量撰写多行 prompt，单 Enter 发送会频繁误触。

---

## 11. Suggested Prompts（空状态引导）

Agent Copilot 首次打开时，展示 3–5 个**上下文相关**的建议：

```
┌────────────────────────────────────────────────┐
│                                                │
│        ✨ Hi, I'm BYAI Copilot              │
│        I can help you explore this workspace   │
│                                                │
│        Try:                                    │
│        ┌──────────────────────────────────┐   │
│        │ 📊 Summarize Q1 revenue          │   │
│        └──────────────────────────────────┘   │
│        ┌──────────────────────────────────┐   │
│        │ 🔍 Find overdue invoices         │   │
│        └──────────────────────────────────┘   │
│        ┌──────────────────────────────────┐   │
│        │ ✉ Draft follow-up email to leads │   │
│        └──────────────────────────────────┘   │
│                                                │
└────────────────────────────────────────────────┘
```

**硬规**：建议必须是**可操作的动词短语**，不是"I can help with..."这类笼统话。

---

## 12. Agent Error Handling

### 12.1 透明的错误

不要隐藏或美化错误。

```
✕ Error: query_database returned no rows.
  The filter 'segment = "Enterprice"' has a typo.
  Did you mean 'Enterprise'?  [Retry] [Edit filter]
```

### 12.2 不可解决的错误

```
✕ I don't have permission to access customer_payments.
  You need Finance admin role to proceed.
  [Request access →]
```

### 12.3 限流 / 配额

```
⚠  You've used 4,800 / 5,000 AI tokens this month.
   At current usage, you'll hit the limit in ~2 days.
   [Upgrade plan] [View usage]
```

---

## 13. 检查清单（AI 实现 Agent UI 时自检）

- [ ] Agent 气泡使用 `bg.agent.surface`（violet.50）区别于人类
- [ ] Agent avatar 抽象，不拟人化
- [ ] 流式输出有 cursor 指示 + Stop 按钮
- [ ] Reasoning trace 默认折叠，可展开
- [ ] 工具调用有独立视觉单元，显示 input/output
- [ ] 外部影响操作有 HITL approval card（三态按钮）
- [ ] 数据结论有 citation chip + tooltip
- [ ] 长内容自动拆分到 artifact canvas
- [ ] Context 使用率可见 (bar + drawer)
- [ ] Composer 支持 `/` 和 `@` 命令
- [ ] 发送快捷键是 `⌘⏎` 不是 `⏎`
- [ ] 每条 Agent 消息有 copy / regenerate / feedback actions
- [ ] Error 透明且可恢复，不用泛化的"出错了"
