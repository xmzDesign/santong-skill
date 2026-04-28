# 08 · States
> Loading / Empty / Error / Success / Permission / Onboarding

每一屏至少要考虑 6 种状态。只画"happy path"是业余；画全 6 态才是专业。

---

## 1. Loading States（加载态）

### 1.1 三档加载体感

| 预期时长 | 处理方式 |
|---|---|
| < 300ms | **不展示任何指示**（避免闪烁） |
| 300ms – 2s | **Spinner** 或按钮内 loading |
| 2s – 10s | **Skeleton** 模拟真实结构 |
| > 10s | **Progress** + 预计剩余时间 + 可取消按钮 |

### 1.2 Skeleton 规范

Skeleton 必须匹配真实内容的**形状、位置、数量**。不要用"三条灰条"代替一整页。

**例：Table skeleton**

```html
<table class="table">
  <thead>
    <tr>
      <th style="width:40px"><span class="skeleton skeleton-rect" style="width:16px;height:16px"></span></th>
      <th><span class="skeleton skeleton-rect" style="width:60%;height:12px"></span></th>
      <th><span class="skeleton skeleton-rect" style="width:40%;height:12px"></span></th>
      <th><span class="skeleton skeleton-rect" style="width:30%;height:12px"></span></th>
    </tr>
  </thead>
  <tbody>
    <tr><td colspan="4"><span class="skeleton skeleton-line" style="width:100%"></span></td></tr>
    <tr><td colspan="4"><span class="skeleton skeleton-line" style="width:90%"></span></td></tr>
    <tr><td colspan="4"><span class="skeleton skeleton-line" style="width:95%"></span></td></tr>
    <!-- 约 8–10 行，不多不少 -->
  </tbody>
</table>
```

**例：Stat card skeleton**

```html
<div class="stat-card">
  <span class="skeleton" style="width:60px;height:12px"></span>
  <span class="skeleton" style="width:140px;height:36px;margin-top:8px"></span>
  <span class="skeleton" style="width:80px;height:14px;margin-top:12px"></span>
</div>
```

### 1.3 进度型加载（> 10s）

```
┌──────────────────────────────────────────┐
│  Exporting 12,450 records                │
│  ──────────────────────                  │
│  ████████░░░░░░░ 52%                     │
│  Processing row 6,480 / 12,450            │
│  Estimated 8 seconds remaining            │
│                                          │
│                     [Cancel export]      │
└──────────────────────────────────────────┘
```

**硬规**：> 10s 的操作必须满足三条：
1. 显式进度（百分比 / 已处理数量）
2. 预计剩余时间
3. Cancel 按钮可用

### 1.4 Reasoning-aware Loading（Agent 场景）

Agent 调用时的加载态要说明**它在做什么**，不是笼统的"加载中"：

```
❌  Loading...
❌  Please wait...

✅  Querying sales database...
✅  Analyzing 12,450 records...
✅  Generating summary (8s remaining)
```

---

## 2. Empty States（空态）

空态不是"错误"，是**机会点**。每个空态必须包含 4 个元素：

1. **插画 / 图标**（抽象几何，非拟物）
2. **标题**（说明"什么空了"）
3. **说明**（解释"为什么空 / 接下来做什么"）
4. **CTA**（提供行动入口）

### 2.1 初次使用（No Data Yet）

```
┌─────────────────────────────────────────┐
│                                         │
│            ◊                            │  ← 抽象几何插画
│         ◊  ◊                            │     60 × 60px · violet + amber 组合
│                                         │
│     You don't have any workflows yet    │  ← type.h3
│                                         │
│   Create your first workflow from a     │  ← type.body · fg.muted
│   template or start from scratch.       │
│                                         │
│   ┌─────────────────┐ ┌──────────────┐ │
│   │ Browse templates │ │ Start blank  │ │
│   └─────────────────┘ └──────────────┘ │
│   Primary              Secondary        │
│                                         │
└─────────────────────────────────────────┘
  padding: space.16
  text-align: center
```

### 2.2 筛选无结果（No Results for Filter）

```
┌─────────────────────────────────────────┐
│                                         │
│             🔍                          │
│                                         │
│     No customers match "Entrpise"       │
│                                         │
│   Try adjusting your filters or check   │
│   for typos.                            │
│                                         │
│   ┌────────────────────────────┐       │
│   │ Clear all filters           │       │
│   └────────────────────────────┘       │
│                                         │
└─────────────────────────────────────────┘
```

### 2.3 已完成 / 无更多（All Done）

```
   ✓
   You're all caught up.
   No overdue tasks.
   [Back to dashboard]
```

### 2.4 Empty State CSS

```css
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  padding: var(--space-16) var(--space-8);
  text-align: center;
}

.empty-state-illustration {
  width: 80px;
  height: 80px;
  margin-bottom: var(--space-4);
  color: var(--fg-subtle);
}

.empty-state-title {
  font-size: 18px;
  line-height: 24px;
  font-weight: 600;
  color: var(--fg-strong);
}

.empty-state-description {
  font-size: 14px;
  line-height: 20px;
  color: var(--fg-muted);
  max-width: 360px;
}

.empty-state-actions {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-4);
}
```

### 2.5 常见空态场景对照表

| 场景 | 标题 | 描述 | CTA |
|---|---|---|---|
| 无工作流 | You don't have any workflows | Create your first workflow | Browse templates / Start blank |
| 无客户 | No customers yet | Import a CSV or add manually | Import CSV / Add customer |
| 无消息 | Inbox zero | You're all caught up | — |
| 搜索无结果 | No results for "X" | Try different keywords | Clear search |
| 无权限 | Restricted section | You don't have access | Request access |
| 筛选后无数据 | No items match | Adjust your filters | Clear filters |
| Agent 无历史 | Start a conversation | Ask BYAI anything | Try: [suggestions] |

---

## 3. Error States（错误态）

### 3.1 错误的四个层级

| Scope | UI Pattern |
|---|---|
| **字段级** | Inline message（红字 + icon 在 input 下方） |
| **区块级** | Alert banner（在 card / section 顶部） |
| **页面级** | Error page（整页替换） |
| **全局级** | Toast + 可能的全局 banner |

### 3.2 错误文案三要素

Error 文案**必须**包含：

1. **发生了什么**（What happened）
2. **为什么**（Why，如果能说的话）
3. **怎么办**（Next action）

```
❌  Something went wrong.
❌  Error occurred. Please try again.
❌  500 Server Error

✅  Couldn't save your changes.
    The connection timed out after 30 seconds.
    [Retry] [Save locally]

✅  You can't invite more than 10 users on the Starter plan.
    You have 10 / 10 seats in use.
    [Upgrade plan] [Manage seats]
```

### 3.3 页面级错误

```
┌──────────────────────────────────────────────┐
│                                              │
│                                              │
│              ⚠                               │
│                                              │
│          We hit a snag                       │  ← type.h1
│                                              │
│   We couldn't load this dashboard.           │  ← type.body-lg, muted
│   This is usually temporary.                 │
│                                              │
│   Error ID: ERR-2026-04-21-a1b2              │  ← font-mono, muted
│                                              │
│   ┌───────────┐  ┌──────────────────┐       │
│   │ Try again │  │ Contact support  │       │
│   └───────────┘  └──────────────────┘       │
│                                              │
│   ▸ Technical details                        │  ← 折叠区
│                                              │
└──────────────────────────────────────────────┘
```

**技术细节展开**（只给明显是技术用户看）：

```
▾ Technical details
  Request ID: req_abc123
  Status: 500
  Endpoint: POST /api/v2/dashboards/42
  Timestamp: 2026-04-21T14:32:08Z
  [Copy to clipboard]
```

### 3.4 404 页面

```
    404
    Page not found

    The page you're looking for doesn't exist
    or has been moved.

    ┌──────────────┐
    │ Go home      │
    └──────────────┘

    Or try:
    • /dashboard
    • /customers
    • Search everything (⌘K)
```

### 3.5 Inline Error 规范（字段级）

```html
<div class="input-field">
  <label class="input-label" for="email">Work email</label>
  <div class="input-wrapper" data-invalid="true">
    <input id="email" value="acme.com" aria-invalid="true" aria-describedby="email-err" />
  </div>
  <span id="email-err" class="input-helper" data-error="true">
    <svg class="icon icon-xs" aria-hidden="true">⚠</svg>
    Enter a valid email address (e.g., name@acme.com).
  </span>
</div>
```

**硬规**：
1. 错误图标 + 错误文字（色觉差异友好 · 双编码）
2. 具体而非泛化（"Enter a valid email" 而非 "Invalid"）
3. 给例子（`(e.g., name@acme.com)`）
4. `aria-invalid="true"` + `aria-describedby` 关联

---

## 4. Success States（成功态）

### 4.1 轻量成功（Toast）

大多数成功反馈应该是 **toast**，不是 modal：

```
┌───────────────────────────────┐
│ ✓  Changes saved              │
│    Settings applied to all    │
│    team members               │
└───────────────────────────────┘
```

### 4.2 重大成功（Full screen，罕用）

仅用于**关键里程碑**——如首次开户、订阅激活、首次发布：

```
              ◆
           ◆  ◆  ◆
              ◆

       🎉 Welcome to BYAI

    Your workspace is ready.
    Let's build your first workflow.

    ┌──────────────────────┐
    │ Get started          │
    └──────────────────────┘

    ▸ Invite your team first
```

**反例**：日常操作（如保存按钮）弹一个满屏 modal "Success!"。**❌ 永远不要**。

### 4.3 过度庆祝反例

| ❌ | ✅ |
|---|---|
| 保存成功后弹出 confetti + modal | Toast 一行 + 自动消失 |
| 每次操作都播放"叮"的音效 | 默认静音 |
| 保存后跳转到另一个页面 | 原地刷新数据 |

---

## 5. Permission States（权限态）

Agent 产品对权限极其敏感——尤其企业版。

### 5.1 权限不足 Page

```
┌──────────────────────────────────────┐
│              🔒                      │
│                                      │
│     You don't have access            │
│                                      │
│   This workspace requires "Admin"    │
│   role. You currently have "Editor". │
│                                      │
│   ┌─────────────────────────┐       │
│   │ Request access          │       │
│   └─────────────────────────┘       │
│   Requests go to wanglei@byai.cn     │
│                                      │
└──────────────────────────────────────┘
```

### 5.2 部分权限（Read-only banner）

```
┌──────────────────────────────────────────────────────┐
│ ℹ  You have read-only access to this workflow.       │
│    Contact the owner to request edit permissions.    │
│    [Request access]                                   │
└──────────────────────────────────────────────────────┘
```

**硬规**：只读模式必须在页面顶部**持续展示** banner，而不只是禁用按钮（disabled button 信息量不够）。

### 5.3 Agent 权限不足

Agent 主动发现自己权限不足时：

```
┌──────────────────────────────────────────┐
│ ✕ I can't access customer_payments table │
│   You need Finance admin role to let me  │
│   query billing data.                     │
│                                          │
│   [Request access] [Ask without this data]│
└──────────────────────────────────────────┘
```

---

## 6. Onboarding States（新手引导）

### 6.1 首次进入 Workspace

不要用传统的"五步 wizard 遮罩"。BYAI 推荐**嵌入式 checklist**：

```
┌──────────────────────────────────────────────┐
│ Get started                       4 of 6 done │
│ ──────────────                                │
│ ✓  Create your workspace                     │
│ ✓  Invite your first teammate                │
│ ✓  Connect a data source                     │
│ ✓  Run your first workflow                   │
│ ○  Configure billing                         │ ← 未完成
│ ○  Explore Agent templates                   │
│                                              │
│ [Dismiss] · [Keep showing]                   │
└──────────────────────────────────────────────┘
  放置位置：Dashboard 左上角 Card
  可关闭 · 可重新打开 · 进度持久化
```

### 6.2 Feature Tour（新功能引导）

仅用于**新上线重要功能**。一次不超过 3 步，否则用户跳出：

```
┌──────────────────────────────┐
│ 🆕 New: AI Workflow Builder  │
│ ──────────                   │
│ Drag & drop to create your   │
│ Agent workflows visually.    │
│ ─                            │
│ Step 1 of 3 → [Next]  [Skip] │
└──────────────────────────────┘
   箭头指向新功能入口
```

### 6.3 空状态 ≠ Onboarding

初次用户看到的是**空态**（第 2 节），不是满屏遮罩的 onboarding。两者职责不同：

- **空态**：告诉用户"现在没东西 · 你可以做什么"
- **Onboarding**：主动介绍"产品有什么 · 你可能错过了什么"

新手的第一秒应该看到**空态**，主动探索；只有当用户**卡住**或**访问新功能**时，才展示 onboarding 提示。

---

## 7. Offline / Connection States

### 7.1 断网 Banner

```
┌────────────────────────────────────────────────────┐
│ ⚡ Connection lost. Your changes are saved locally │
│    and will sync when you're back online.  [Retry] │
└────────────────────────────────────────────────────┘
   yellow tint · sticky top · 非 dismissible
```

### 7.2 重连

```
┌──────────────────────────────────────┐
│ ✓ Back online. Synced 3 changes.    │
└──────────────────────────────────────┘
   auto-dismiss 3s
```

---

## 8. 状态覆盖自检清单

每一屏都应确认以下 6 态的实现：

- [ ] **Happy path** — 数据齐全时
- [ ] **Loading** — 请求中 / streaming 中
- [ ] **Empty** — 首次 / 筛选后无结果
- [ ] **Error** — 请求失败 / 验证失败
- [ ] **Permission** — 无权访问 / 只读
- [ ] **Offline** — 断网 / 连接超时

**硬规**：Pull request 中缺任何一态的视觉稿都是未完成状态，不该合入。
