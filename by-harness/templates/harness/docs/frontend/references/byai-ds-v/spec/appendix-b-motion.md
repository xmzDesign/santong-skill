# Appendix B · Motion
> 缓动 · 时长 · 编排

---

## 0. 动效哲学

> **Motion is functional, not decorative.**
> 动效是功能性的，不是装饰。

每一个动效都应该回答："它帮用户理解了什么？"
- 元素的**来自哪里**（entry direction）
- 元素的**去向哪里**（exit direction）
- 元素的**层级关系**（z-depth）
- 状态的**变化发生**（feedback confirmation）

如果一个动效不解决这些问题，它就是**装饰**——删除它。

---

## 1. Duration Tokens（时长）

| Token | ms | 用途 |
|---|---|---|
| `motion.duration.instant` | 0 | 无动画（偏好减少动效） |
| `motion.duration.fast` | 120 | 微交互：hover / focus / 按下 |
| `motion.duration.base` | 200 | **默认 ✨** · 大多数场景 |
| `motion.duration.slow` | 320 | Modal / Drawer 入场 |
| `motion.duration.slower` | 500 | 大区块切换 / 页面转场 |
| `motion.duration.slowest` | 800 | 特殊场景（引导首帧） |

### 1.1 时长参考表

| 元素 | 时长 |
|---|---|
| Button hover | 120ms |
| Input focus ring | 120ms |
| Popover 入场 | 150ms |
| Tooltip 入场 | 150ms（延迟 500ms） |
| Toast 入场 | 300ms |
| Modal 入场 | 300ms |
| Drawer 滑入 | 320ms |
| Table row 加入 | 400ms |
| Page transition | 200ms |
| Skeleton shimmer loop | 1500ms |
| Spinner loop | 600ms |
| Streaming cursor blink | 1000ms |

---

## 2. Easing Tokens（缓动）

| Token | Curve | 用途 |
|---|---|---|
| `motion.ease.linear` | `linear` | Loading 进度条 · 循环动画 |
| `motion.ease.out` | `cubic-bezier(0.25, 1, 0.5, 1)` | **默认 ✨** · 大多数入场 |
| `motion.ease.in-out` | `cubic-bezier(0.65, 0, 0.35, 1)` | 值变化 · 双向移动 |
| `motion.ease.spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Modal / Drawer 入场 · 带轻微弹 |
| `motion.ease.anticipate` | `cubic-bezier(0.87, 0, 0.13, 1)` | 退场 · 急速离去 |

### 2.1 曲线选择规则

| 场景 | Easing |
|---|---|
| 元素**进入**视口 | `ease.out`（慢下来停稳） |
| 元素**离开**视口 | `ease.anticipate`（加速离开） |
| 值渐变（数字 count-up） | `ease.in-out` |
| 循环 loop | `ease.linear` |
| 强调出场（庆祝） | `ease.spring` |

### 2.2 曲线对照

```
ease.out  →  ╮
              ╰────────  (快→慢，自然停稳)

ease.in   →         ╭
             ──────╯       (慢→快，加速离去)

ease.in-out  →  ╭───╮
                ╰───╯      (先慢后快再慢)

ease.spring  →  ╮  ╭─
                 ╰─╯       (超出一点再回弹)
```

---

## 3. Transform Patterns（变换模式）

### 3.1 Fade（淡入/淡出）

```css
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes fadeOut {
  from { opacity: 1; }
  to   { opacity: 0; }
}
```

用于：toast / popover / overlay

### 3.2 Slide（滑入）

```css
@keyframes slideUp {
  from { transform: translateY(16px); opacity: 0; }
  to   { transform: translateY(0); opacity: 1; }
}
@keyframes slideInFromRight {
  from { transform: translateX(100%); }
  to   { transform: translateX(0); }
}
```

用于：drawer / toast / 列表新增行

### 3.3 Scale（缩放入场）

```css
@keyframes scaleIn {
  from { transform: scale(0.96); opacity: 0; }
  to   { transform: scale(1); opacity: 1; }
}
```

用于：modal / popover（微缩入，避免突兀出现）

### 3.4 组合（最常用）

```css
@keyframes modalEnter {
  from {
    opacity: 0;
    transform: translate(-50%, -48%) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}
```

---

## 4. Choreography（编排）

### 4.1 Staggered Entry（交错入场）

多个元素依次入场，每个延迟 50–80ms：

```css
.stat-card { animation: slideUp 400ms var(--motion-ease-out) both; }
.stat-card:nth-child(1) { animation-delay: 0ms; }
.stat-card:nth-child(2) { animation-delay: 60ms; }
.stat-card:nth-child(3) { animation-delay: 120ms; }
.stat-card:nth-child(4) { animation-delay: 180ms; }
```

**限制**：最多 8 个元素交错（超过会感觉拖沓）。

### 4.2 Choreography Rules

| 动作 | 规则 |
|---|---|
| 同类元素入场 | 从左到右 / 从上到下 · 每个错开 60–80ms |
| 父子入场 | 父先于子 100ms |
| 替换内容 | 旧内容 `fadeOut 150ms` → 新内容 `fadeIn 200ms`，不重叠 |
| 列表插入 | 新项 `slideUp + fadeIn 300ms`，其他项 `slideDown 200ms` 让位 |

---

## 5. Microinteractions（微交互）

### 5.1 Button

```css
.btn {
  transition:
    background var(--motion-duration-fast) var(--motion-ease-out),
    border-color var(--motion-duration-fast) var(--motion-ease-out),
    box-shadow var(--motion-duration-fast) var(--motion-ease-out),
    transform var(--motion-duration-fast) var(--motion-ease-out);
}
.btn:active:not(:disabled) {
  transform: translateY(0.5px);  /* 轻微按下感 */
}
```

### 5.2 Checkbox 切换

```css
.checkbox-icon {
  transition: transform 200ms var(--motion-ease-spring);
}
.checkbox:checked + .checkbox-icon {
  transform: scale(1) rotate(0);
}
.checkbox:not(:checked) + .checkbox-icon {
  transform: scale(0) rotate(-45deg);
}
```

### 5.3 Switch 切换

```css
.switch::after {
  transition: transform 200ms var(--motion-ease-out);
}
.switch:checked::after { transform: translateX(14px); }
```

### 5.4 Accordion 展开

```css
.accordion-content {
  max-height: 0;
  overflow: hidden;
  transition: max-height 300ms var(--motion-ease-in-out);
}
.accordion-content[data-open="true"] {
  max-height: var(--content-height); /* JS 测量实际高度 */
}
.accordion-chevron {
  transition: transform 200ms var(--motion-ease-out);
}
.accordion[data-open="true"] .accordion-chevron {
  transform: rotate(180deg);
}
```

---

## 6. Page Transitions

SPA 页面切换：

```css
.page-enter { animation: pageEnter 200ms var(--motion-ease-out) both; }
.page-exit  { animation: pageExit 150ms var(--motion-ease-anticipate) both; }

@keyframes pageEnter {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes pageExit {
  from { opacity: 1; transform: translateY(0); }
  to   { opacity: 0; transform: translateY(-4px); }
}
```

**原则**：页面转场 **≤ 200ms**。超过用户感觉慢。

---

## 7. Loading Animations

### 7.1 Spinner

```css
@keyframes spin {
  to { transform: rotate(360deg); }
}
.spinner { animation: spin 600ms linear infinite; }
```

### 7.2 Skeleton Shimmer

```css
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
.skeleton {
  background: linear-gradient(90deg,
    var(--bg-surface-sunken) 0%,
    var(--bg-hover) 50%,
    var(--bg-surface-sunken) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1500ms var(--motion-ease-in-out) infinite;
}
```

### 7.3 Agent Thinking（呼吸光）

```css
@keyframes breathe {
  0%, 100% { opacity: 0.4; transform: scale(0.95); }
  50%      { opacity: 1;   transform: scale(1.05); }
}
.agent-thinking-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--agent-indicator-thinking);
  animation: breathe 1500ms var(--motion-ease-in-out) infinite;
}
```

### 7.4 Streaming Cursor

```css
@keyframes cursor-blink {
  0%, 50%    { opacity: 1; }
  51%, 100%  { opacity: 0.3; }
}
.streaming-cursor {
  animation: cursor-blink 1s var(--motion-ease-in-out) infinite;
}
```

---

## 8. prefers-reduced-motion

**硬规**：必须尊重用户系统偏好。

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

某些**信息性动效**（如 progress bar、skeleton）应该保留，但显著降速或静态替代：

```css
@media (prefers-reduced-motion: reduce) {
  .skeleton {
    animation: none;
    background: var(--bg-surface-sunken);
  }
  .spinner {
    animation-duration: 2s;  /* 减速而非消除 */
  }
}
```

---

## 9. 反例

| ❌ | ✅ |
|---|---|
| 所有元素同时 fade in | 交错 60–80ms 入场 |
| Button hover 用 500ms | ≤ 120ms |
| Modal 用 bounce（过度） | scale + fade 300ms |
| 每个图标都有 hover 旋转 | 仅交互性 icon 有 hover 反馈 |
| 滚动视差装饰 | 无必要，禁用 |
| Loading 转圈 + 脉冲 + 条形叠加 | 单一方式够了 |
| 忽略 `prefers-reduced-motion` | 严格尊重用户偏好 |

---

## 10. 性能考虑

### 10.1 优先用 transform + opacity

这两个属性由 GPU 加速，60fps 流畅：

```css
/* ✅ GPU-accelerated */
.good { transform: translateX(100px); opacity: 0.5; }

/* ❌ 触发重排 */
.bad { left: 100px; width: 200px; }
```

### 10.2 避免 will-change 滥用

```css
.modal { will-change: transform, opacity; }  /* ⚠ 慎用 */
```

仅在**即将发生动画**的瞬间添加，动画结束后移除。

### 10.3 节流动画

```css
/* ❌ 每帧都重算 */
.bad { animation: shake 50ms infinite; }

/* ✅ 合理帧率 */
.good { animation: fade 200ms var(--motion-ease-out) forwards; }
```

---

## 11. 动效检查清单

每个组件的动效应满足：

- [ ] 使用 `motion.duration.*` token（不硬编码 ms）
- [ ] 使用 `motion.ease.*` token（不硬编码 cubic-bezier）
- [ ] 入场用 `ease-out`，退场用 `ease-anticipate`
- [ ] 大多数 UI 微交互 ≤ 200ms
- [ ] 只 animate `transform` 和 `opacity`（除非必要）
- [ ] 有 `prefers-reduced-motion` 降级
- [ ] 没有让人等超过 500ms 的入场
- [ ] 序列动画不超过 8 个元素交错
