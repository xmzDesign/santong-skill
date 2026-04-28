# Appendix D · Anti-patterns
> AI 最常犯的通病清单 · 不该出现的设计

这份清单是真金白银——它直接消除 AI 生成 UI 时 90% 的毛病。

---

## 1. 色彩类 Anti-patterns

### ❌ 1.1 紫色渐变 + 磨玻璃

所谓"AI product 通病"。两个特征：

```css
/* 禁用 */
background: linear-gradient(135deg, #8B5CF6, #3B82F6);
backdrop-filter: blur(20px) saturate(180%);
```

**替代**：纯色 `bg.canvas` + 极微小 `shadow.xs`。editorial 温度靠字体和暖调 off-white，不靠渐变。

### ❌ 1.2 红绿二元

```css
/* 禁用 */
.up   { color: green; }
.down { color: red; }
```

**替代**：amber `↑` / blue `↓` + 必带符号前缀。

### ❌ 1.3 硬编码 hex

```html
<!-- 禁用 -->
<button style="background: #A36E10">Save</button>
```

**替代**：`class="btn btn-primary"`，CSS 内用 `var(--intent-primary-bg)`。

### ❌ 1.4 纯黑字 on 纯白

```css
/* 太硬 */
body { background: #FFFFFF; color: #000000; }
```

**替代**：`bg-canvas` (#FAFAF7) + `fg-default` (#2A2620)，暖调且对比度仍达 AA。

### ❌ 1.5 过饱和 saturated UI 色

特征：饱和度 > 80%、亮度 > 60% 的 primary 色（如 `#3B82F6` 纯蓝、`#10B981` 亮绿）。

**替代**：BYAI 的 `amber.600` 饱和度约 85% 但亮度只有 38%——深沉而不刺眼。

---

## 2. 排版类 Anti-patterns

### ❌ 2.1 Inter / Roboto / system-ui 打天下

```css
/* 不够有辨识度 */
font-family: Inter, system-ui, sans-serif;
```

**替代**：`Geist`（英文）+ `Microsoft YaHei`（中文）+ `Fraunces`（标题点缀）。

### ❌ 2.2 中文用衬线（宋体系）

小尺寸衬线中文在屏幕上极难读。

**替代**：中文只用 `Microsoft YaHei` / `PingFang SC`。editorial 衬线通过英文 display 字体实现。

### ❌ 2.3 段落居中对齐

```css
/* 禁用 */
p { text-align: center; }
```

除非是 landing Hero / 空状态，**正文一律左对齐**。

### ❌ 2.4 全大写中文

```
❌  首 页 管 理 员 登 录
```

没有任何 editorial 效果，只显得粗暴。

### ❌ 2.5 字号随意

```
❌  font-size: 15px; 17px; 19px; 21px;
```

**替代**：严格使用 9 档字阶（11/12/13/14/16/18/22/28/36）。

### ❌ 2.6 行高过紧或过松

```css
/* ❌ */
p { line-height: 1.2; }  /* 太紧 */
p { line-height: 2.0; }  /* 太松 */
```

**替代**：body 行高 20/14 ≈ 1.43，中文场景可到 1.6。

---

## 3. 间距类 Anti-patterns

### ❌ 3.1 非 4 倍数间距

```css
padding: 13px 18px 22px;  /* ❌ 随意 */
```

**替代**：`padding: var(--space-3) var(--space-4) var(--space-5);`（12 16 20）

### ❌ 3.2 Card 叠 Shadow

```css
.card { box-shadow: 0 20px 40px rgba(0,0,0,0.2); }
```

过重的 shadow 让界面像 2015 Material。

**替代**：`border: 1px solid var(--border-subtle)` 分割，或 `shadow.xs / sm` 轻微提升。

### ❌ 3.3 盲目留白

```
┌────────────────────────────────────┐
│                                    │
│                                    │
│                                    │
│         Dashboard                  │
│                                    │
│                                    │
│  [Card]  [Card]                    │
│                                    │
│                                    │
└────────────────────────────────────┘
```

违反 Tenet 2（Density as Respect）。专业用户想一屏看尽。

---

## 4. 组件类 Anti-patterns

### ❌ 4.1 按钮文字是"OK / Confirm / Submit"

```html
<button>OK</button>     <!-- ❌ -->
<button>Save changes</button>  <!-- ✅ -->
```

### ❌ 4.2 页面多个 Primary CTA

```
[Delete]  [Save]  [Publish]  [Export]
  primary   primary  primary   primary
```

**替代**：每页最多 1 个 primary。次级用 secondary。

### ❌ 4.3 Modal 嵌套 Modal

第一层 modal 里点按钮再弹出第二层 modal。用户迷失。

**替代**：改用 **Stepper** / **Drawer nested**。

### ❌ 4.4 禁用按钮无解释

```html
<button disabled>Send</button>
<!-- 用户：为什么不能点？-->
```

**替代**：disabled 按钮必须配 tooltip，说明 prerequisite。

### ❌ 4.5 Table 行高 56px

B2B 的悲剧。

**替代**：默认 36px（Comfortable）。

### ❌ 4.6 所有列平分宽度

```css
table { table-layout: fixed; }
th { width: 12.5%; }  /* 平均分 */
```

**替代**：名称列宽、数字列窄、action 列 fit-content。

### ❌ 4.7 Dropdown 用颜色编码

```
Status ▾
  [红]  Inactive
  [绿]  Active
```

**替代**：色 + icon + 文字。

### ❌ 4.8 Input 的 label 放 placeholder

```html
<input placeholder="Email" />
```

用户开始打字 label 就消失。

**替代**：永远独立 `<label>` + placeholder 作为示例。

### ❌ 4.9 Tooltip 里放链接 / 按钮

Tooltip 是**悬停即消失**的临时信息。放 interactive 元素用户无法点击。

**替代**：改用 Popover（onClick）。

### ❌ 4.10 Confirmation dialog 用"Yes / No"

```
Are you sure? [No] [Yes]
```

**替代**：`[Cancel] [Delete customer]`——重复动作名，明确后果。

---

## 5. 交互类 Anti-patterns

### ❌ 5.1 Enter 单击发送

Chat composer 里 `Enter` 发送 `Shift+Enter` 换行——对于 multi-line prompt 用户极易误触。

**替代**：`Cmd+Enter` / `Ctrl+Enter` 发送，`Enter` 换行。

### ❌ 5.2 Loading 完全空白

```
Page → 白屏 → 完整内容
```

**替代**：Skeleton 先展示结构。

### ❌ 5.3 Agent 黑箱

```
You:  Analyze Q1 revenue
Bot:  Revenue grew 12.3%.
```

看不到 Agent 怎么得出结论的、用了什么数据。

**替代**：展示 reasoning trace + tool call + citation。

### ❌ 5.4 HITL 只有"Approve"

```
The AI wants to send 50 emails. [Approve]
```

无法编辑、无法拒绝并说明原因。

**替代**：三态 `[Decline] [Edit] [Approve]`。

### ❌ 5.5 Toast 不可关闭

Toast 自动 5s 消失但期间不能手动关闭——用户眼睛不在那里时错过了。

**替代**：手动关闭 button + 自动消失。

### ❌ 5.6 Focus ring 用浏览器默认

```css
*:focus { outline: 2px dotted blue; }  /* 浏览器默认 · 丑 */
```

**替代**：`box-shadow: var(--shadow-focus-ring)` · 暖调 amber ring。

### ❌ 5.7 无 Esc 关闭的 Modal

所有 modal/drawer/popover 必须支持 `Esc`。

### ❌ 5.8 Tab 顺序乱

```
[Name] → [Cancel] → [Email] → [Save]  ❌
```

**替代**：符合视觉顺序。

---

## 6. 信息架构类 Anti-patterns

### ❌ 6.1 埋藏关键功能

核心操作藏在三层菜单。

**替代**：核心操作上 Command Palette（⌘K），页面上有直接入口。

### ❌ 6.2 一页多功能

Dashboard 一个页面堆满 10 个 section。

**替代**：分标签页（Tabs）或子页面。

### ❌ 6.3 面包屑缺失

用户不知道自己在哪、从哪来。

**替代**：每个深层页面必有 breadcrumb。

### ❌ 6.4 Settings 无分组

长列表 50 个开关。

**替代**：分 section（Account / Team / Integrations / Billing / Advanced）。

---

## 7. Agent 产品专属 Anti-patterns

### ❌ 7.1 拟人化头像

给 Agent 画一张"人脸"或"萌机器人脸"。提高用户对能力的错误预期。

**替代**：抽象几何 / 符号（✨ ◆ ●）。

### ❌ 7.2 "I'm just an AI" 式 disclaimer

```
I'm just a language model and I may be wrong...
```

废话。用户已经知道。

**替代**：需要不确定时精确表述，如"I found 2 possible matches"。

### ❌ 7.3 Streaming 没有 Stop 按钮

一旦错误开始流式，用户只能等完。

**替代**：Stop 按钮**始终**可见。

### ❌ 7.4 无 Citation 的结论

```
Revenue grew 12.3% YoY.
```

基于什么？哪张表？

**替代**：每个事实后带 citation chip。

### ❌ 7.5 无 Reasoning Trace

用户想追溯 Agent 怎么想的，没处看。

**替代**：折叠 reasoning trace，可选展开。

### ❌ 7.6 无 Context Window 可视化

用户不知道 Agent 还记不记得 5 轮之前说了啥。

**替代**：顶部 context bar + 可展开 drawer。

### ❌ 7.7 多 Agent 系统但视觉无区分

Planner / Coder / Reviewer 都长一样。

**替代**：不同图标 / violet 色系内变体区分。

---

## 8. 无障碍类 Anti-patterns

### ❌ 8.1 Icon-only button 无 aria-label

```html
<button><svg>...</svg></button>  <!-- 屏幕阅读器: "button" -->
```

### ❌ 8.2 颜色承载唯一信息

"绿色是必填"、"红色边框是错误"——色盲用户无法察觉。

**替代**：颜色 + 图标 + 文字。

### ❌ 8.3 动画无 prefers-reduced-motion 降级

引起前庭敏感用户不适。

### ❌ 8.4 过小点击区

```css
button { width: 16px; height: 16px; }
```

WCAG 推荐最小 24×24px 点击区（48×48 on mobile）。

### ❌ 8.5 无 skip-to-content

键盘用户每次都要 tab 过 nav。

**替代**：`<a class="skip-link" href="#main">Skip to content</a>`

---

## 9. 文案类 Anti-patterns

### ❌ 9.1 过度 Emoji

```
🎉 Great job! You've successfully saved your changes! 🚀
```

### ❌ 9.2 Casual 感叹号

```
Your report is ready!!!
Click here!
```

### ❌ 9.3 敷衍的"Oops"

```
Oops! Something went wrong 😅
```

### ❌ 9.4 技术词未翻译

```
Deserialization error
Null pointer exception
```

**替代**：给用户看的是"Couldn't read the file—is it valid JSON?"。

---

## 10. Performance 类 Anti-patterns

### ❌ 10.1 动画属性触发 Layout

```css
.bad { transition: left 200ms, width 200ms; }  /* 每帧重排 */
```

**替代**：`transform` + `opacity`。

### ❌ 10.2 强制自定义滚动条

重度自定义滚动条在不同 OS 上表现不一致。

**替代**：遵从系统滚动条，或极简样式：

```css
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 4px; }
```

### ❌ 10.3 大图不懒加载

首屏塞几张大图，LCP 拉垮。

**替代**：`<img loading="lazy">` + 响应式尺寸。

---

## 11. 一张清单：代码提交前检查

AI 产出每段代码前，对照检查：

- [ ] **无 hex 字面值**（`grep "#[A-F0-9]" | grep -v "tokens.css"` 应为空）
- [ ] **无 Red/Green 二元**（`grep "color: green\|color: red"` 应为空）
- [ ] **无 Inter / Arial 中文**（`grep "font-family.*Arial\|Roboto" | grep 中`）
- [ ] **按钮文字不是 "OK / Submit / Confirm"**
- [ ] **每个 modal 有 Esc 关闭**
- [ ] **每个 icon-only button 有 aria-label**
- [ ] **每个破坏性操作有 confirmation + 输入验证**
- [ ] **Agent 消息有 violet background + avatar + citation + actions**
- [ ] **Composer 发送键是 `Cmd+Enter`**
- [ ] **Skeleton 匹配真实内容结构**
- [ ] **Empty state 有 title + description + CTA**
- [ ] **Error state 说明 what / why / what-now**

---

## 12. 总结：三句话记住 Anti-patterns

> 1. **任何需要颜色才能看懂的东西，色盲用户看不懂。**
> 2. **任何 Agent 做了但用户不知道的事，用户认为它在作恶。**
> 3. **任何需要用户去猜的 UI，就已经失败了。**
