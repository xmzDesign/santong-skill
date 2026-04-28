# 前端工程与视觉规范（Harness 版）

本规范用于约束 AI 代码代理在前端任务中的实现行为。它不是泛泛的“写好看一点”，而是一套三层约束：先定禁止项和硬规则，再给标准代码结构，最后给视觉还原规则。

版本信息：
- Version: `2.0`
- Last Updated: `2026-04-28`
- 来源思想：BYAI Design System v1、三层代码规范结构、现有中后台工程约束

## 0. 使用方式

前端任务开始前，必须先完成以下动作：

1. 判断本次任务是否涉及 UI、样式、React/Vue/Next、TypeScript 组件、表单、表格、图表、布局、交互状态或文案。
2. 若涉及，先阅读本文，再按需阅读：
   - `.harness/docs/frontend/rules.md`：约束层，回答“禁止什么、必须怎样”。
   - `.harness/docs/frontend/code-design.md`：示范层，回答“标准代码长什么样”。
   - `.harness/docs/frontend/ui-design.md`：视觉层，回答“页面应该呈现什么气质”。
3. 在 plan/spec 中写明将使用哪类视觉参考：Dashboard、Table、Form、Settings、Agent、Data-viz、Login、Onboarding。
   - 若需要视觉还原或页面级参考，打开 `.harness/docs/frontend/references/byai-ds-v/index.html` 或对应 HTML 页面。
4. 在 build 前列出本次适用的前端硬约束。
5. 在交付前执行前端自检；若存在 `.codex/hooks/convention-check.py` 或 `.claude/hooks/convention-check.py`，运行 `--changed-only`。

## 1. 适用范围

适用于以下任务：
- React / Vue / Next.js / TypeScript 前端编码。
- 中后台、运营后台、SaaS 控制台、Agent 产品界面。
- 页面布局、组件实现、样式修复、视觉还原、表单/表格/图表/弹层/状态视图。
- 任何涉及 HTML、CSS、Less、SCSS、CSS Modules、styled-components、Antd 主题或组件覆盖的改动。

不适用于纯后端逻辑。若同一任务同时涉及前后端，前端部分必须遵守本文。

## 2. 三层规范模型

### 第一层：约束层

约束层是硬规则，优先级最高。它告诉模型“哪些行为绝对不能发生”。

核心要求：
- 不硬编码视觉体系。
- 不随意 invent 颜色、间距、圆角、字号。
- 不绕过项目已有组件库和样式体系。
- 不把 UI 做成 landing page、装饰页或低密度宣传页。
- 不牺牲 loading / empty / error / disabled / focus-visible 等状态。

详见 `.harness/docs/frontend/rules.md`。

### 第二层：示范层

示范层是标准代码模式。它告诉模型“生成新页面或组件时照哪种结构写”。

核心要求：
- 页面负责组合，复杂状态放进 controller hook。
- view 层只展示，不直接请求接口。
- 表格、筛选、分页、弹层、表单、状态视图必须按模板组织。
- 使用 Antd 时优先复用 Antd4/Antd5 项目现有能力；自定义组件必须说明原因。
- CSS Modules / Less / SCSS 必须局部化，避免裸全局污染。

详见 `.harness/docs/frontend/code-design.md`。

### 第三层：视觉层

视觉层是页面气质和视觉还原规则。它告诉模型“UI 最终应该像什么”。

默认方向：
- B2B SaaS / AI-native cockpit，而不是营销落地页。
- 信息密度优先，专业用户一屏内看到关键数据。
- 暖调、克制、清晰；避免紫色渐变、玻璃拟态、空洞大 banner。
- Agent 行为必须可见、可解释、可中断、可追溯。

详见 `.harness/docs/frontend/ui-design.md`。页面级 HTML 参考位于 `.harness/docs/frontend/references/byai-ds-v/`，用于理解布局、层级、密度、状态和 token 使用方式；不要把 demo HTML 直接复制为业务实现。

## 3. 优先级

当规则冲突时，按以下顺序执行：

1. 用户当前明确要求。
2. 当前仓库更近范围的 `AGENTS.md / CLAUDE.md / AGENTS.override.md`。
3. 本文与 `.harness/docs/frontend/*.md`。
4. 项目已有代码模式、组件库、主题系统。
5. 通用审美偏好。

若项目已有成熟设计系统，优先对齐项目系统；若项目没有成熟系统，使用本文内置的 BYAI 风格约束作为默认设计系统。

## 4. 前端硬门禁

以下规则默认强制执行：

1. 颜色、字号、间距、圆角、阴影、动效必须来源于 token 或项目已有主题变量。
2. 业务样式中禁止新增裸 hex 色值；token 文件、第三方品牌 logo、图表库配置例外，但必须集中管理。
3. 禁止新增无必要的 `style={{ ... }}`；动态尺寸可例外，但必须解释原因。
4. 禁止用红/绿作为唯一状态编码；必须配合图标、文字或符号。
5. 禁止默认使用紫色渐变、磨玻璃、大面积 bokeh/orb 装饰。
6. 所有交互控件必须覆盖 default / hover / active / focus-visible / disabled。
7. 所有请求必须有 loading；空数据必须有 empty；失败必须有 error 和关键链路 retry。
8. 表单必须有可见 label；placeholder 只能作为示例，不能替代 label。
9. 破坏性操作必须二次确认，按钮文案必须复述动作和对象。
10. 表格列宽不能平均分；名称列宽、数字列窄、操作列自适应。
11. Agent 或 AI 行为必须展示工具调用、进度、来源、可中断入口。
12. 移动端和窄屏不得出现非预期横向滚动；表格横滚必须显式容器化。

## 5. 工程结构约束

保持项目已有结构优先。若项目没有明确规范，采用以下默认约定：

- 页面组件：`pages/**`
- 通用/业务组件：`components/**`
- 配置：`config/**`
- 工具函数：`utils/**`
- 常量/枚举：`constants/**`
- hooks：`hooks/**`
- 接口请求封装：`service/**` 或 `services/**`
- 类型定义：`types/**`

页面与组件目录采用“文件夹 + index 入口”：

```text
pages/<domain>/<feature>/index.tsx
components/<domain>/<feature>/index.tsx
```

复杂页面建议：

```text
pages/<feature>/
  index.tsx
  view.tsx
  hooks/use-<feature>-controller.ts
  components/
  utils.ts
  types.ts
  style.module.scss
```

## 6. TypeScript / React 约束

1. 禁止使用 `any`；必要时用 `unknown` 加类型守卫。
2. 公共函数建议显式返回类型。
3. 使用函数组件和 Hooks。
4. 组件保持小而专注；复杂逻辑抽到 hooks / utils / service。
5. `useEffect` 依赖必须完整，订阅类副作用必须 cleanup。
6. 列表 key 必须稳定，不使用数组 index 作为可变列表 key。
7. 单个组件文件推荐 `<= 300` 行，超过 `350` 行必须拆分。
8. 所有新增/修改函数、方法必须补充中文注释，说明用途、关键参数、返回值、副作用。

## 7. 数据请求与状态管理

1. 页面/组件不得直接调用裸请求库；必须走项目已有 service 层。
2. 高频输入触发请求必须防抖/节流。
3. 并发请求必须考虑竞态，至少保留最后一次请求结果。
4. 保存、删除、切换、批量操作必须有提交中状态，防止重复提交。
5. 可回滚交互失败时必须恢复原值，保证 UI 与数据一致。
6. 批量操作后必须刷新列表，并清理或明确保留选中态。

## 8. 样式与设计系统

若项目已有 token，使用项目 token。若没有，按以下内置语义建立最小 token：

```text
bg.canvas / bg.surface / bg.surface-sunken
fg.default / fg.strong / fg.muted / fg.subtle / fg.disabled
border.subtle / border.default / border.strong / border.focus
intent.primary / intent.info / intent.warning / intent.danger / intent.neutral
space.1/2/3/4/5/6/8/10/12/16
radius.sm/md/lg/xl/full
shadow.xs/sm/focus-ring
motion.duration.fast/base/slow
```

视觉默认值：
- 页面背景：暖调 off-white，而不是纯白。
- 主强调色：amber/orange 方向；信息色用 blue。
- Danger 色仅用于危险操作，必须伴随图标和明确文案。
- 字号阶梯：`11 / 12 / 13 / 14 / 16 / 18 / 22 / 28 / 36` 或项目已有阶梯。
- 间距：4px grid，优先 `4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48`。
- 圆角：默认 6-8px，卡片不超过 8px，弹层可 12px。
- 阴影：轻量，优先边框分隔，避免重 shadow。

## 9. Antd 兼容

1. Antd 项目优先复用 Antd 组件，不重复造基础控件。
2. Antd4 通过 Less 变量或项目现有主题层映射 token。
3. Antd5 通过 `ConfigProvider theme.token` 映射 token。
4. 覆盖 Antd 样式必须局部化，CSS Modules 中使用 `:global` 包在模块根类下。
5. 禁止多层裸 `.ant-*` 全局覆盖和滥用 `!important`。
6. 如果自定义替代 Antd 基础组件，必须说明：Antd 不能满足的交互、可访问性或视觉原因。

## 10. 状态、无障碍与动效

必须覆盖：
- Loading：请求中、提交中、长耗时进度。
- Empty：初次无数据、筛选无结果、已完成无更多。
- Error：字段级、块级、页面级、网络/权限错误。
- Disabled：说明不可用原因，关键操作配 tooltip/help。
- Success：轻量反馈，避免过度庆祝。

无障碍要求：
- 文本对比度达到 WCAG 2.2 AA。
- 所有交互元素可键盘访问。
- Focus visible 清晰，不使用浏览器默认虚线作为唯一焦点样式。
- Icon-only button 必须有 `aria-label`。
- 不仅靠颜色传达状态。
- Modal / Drawer 打开后管理焦点，Esc 可关闭，关闭前处理未保存内容。

动效要求：
- 优先使用 `transform` 和 `opacity`。
- 支持 `prefers-reduced-motion`。
- 微交互建议 120-200ms，复杂过渡不超过 400ms。

## 11. 交付前自检

前端任务完成前必须逐条检查：

- 是否读取并遵守了 `.harness/docs/frontend/rules.md`。
- 是否选择了对应视觉类型并参考 `.harness/docs/frontend/ui-design.md`。
- 是否没有新增硬编码颜色、裸全局样式、无解释 inline style。
- 是否覆盖 loading / empty / error / disabled / focus-visible。
- 是否所有新增/修改函数、方法都有中文注释。
- 是否执行构建、测试或至少说明无法执行的原因。
- 若 UI 变化明显，是否完成桌面与窄屏截图或浏览器验证。
- 若有 hook，是否运行 `python3 .codex/hooks/convention-check.py --changed-only` 或 `python3 .claude/hooks/convention-check.py --changed-only`。

## 12. 例外流程

允许例外，但必须在最终回复说明：

- 违反了哪条规则。
- 为什么当前业务或技术条件需要例外。
- 风险是什么。
- 后续如何回收。

没有说明的例外视为未完成。
