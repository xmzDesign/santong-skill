# 10 · Voice & Microcopy
> 中英双语文案规范 · Agent persona · 错误文案库

---

## 0. Voice Principle（一句话定义）

> **"BYAI 说话像一个资深同事：直接、有信息量、不绕弯、不装腔。"**

如果你写的按钮文字像保险合同 or 客服话术，那肯定错了。

---

## 1. 四条 Voice Attribute

| Attribute | 是 | 不是 |
|---|---|---|
| **Direct（直接）** | "Delete 3 customers?" | "Are you sure you want to proceed with this action?" |
| **Specific（具体）** | "Export 1,240 rows as CSV" | "Download" |
| **Professional（专业）** | "Verification failed. The API key is revoked." | "Oops! Something went wrong 😱" |
| **Calm（平静）** | "Saved." | "Yay! All done! 🎉" |

---

## 2. Verb Library（动词库）

每个界面 CTA、菜单项，都应该从这个表里选词。**不用近义词混用**（"Save" 和 "Submit" 含义不同）。

### 2.1 常用动词（英文）

| Action | 推荐动词 | 避免 |
|---|---|---|
| 创建 | Create / Add / New | Make |
| 保存 | Save / Apply | Submit（除非表单专用） |
| 删除 | Delete / Remove | Kill / Trash |
| 编辑 | Edit / Update | Modify |
| 复制 | Copy / Duplicate | Clone（除非技术语境） |
| 移动 | Move | Shift |
| 取消 | Cancel | Abort / Back out |
| 确认 | Confirm / OK | Alright / Sure |
| 继续 | Continue / Next | Proceed / Go on |
| 返回 | Back | Go back |
| 关闭 | Close / Dismiss | Hide（含义不同） |
| 导出 | Export | Download（除非明确是文件） |
| 导入 | Import / Upload | Load |
| 分享 | Share / Invite | Send |
| 开启 | Enable / Turn on | Activate（除非账户类） |
| 关闭（功能） | Disable / Turn off | Deactivate |
| 归档 | Archive | Hide / Stash |
| 还原 | Restore | Undo（含义不同） |
| 撤销 | Undo | Reverse |

### 2.2 常用动词（中文）

| 操作 | 推荐动词 | 避免 |
|---|---|---|
| 创建 | 创建 / 新建 / 添加 | 增加（太口语） |
| 保存 | 保存 | 储存 / 存储 |
| 删除 | 删除 | 清除（含义不同） |
| 编辑 | 编辑 / 修改 | 更改 |
| 复制 | 复制 | 拷贝（太技术） |
| 取消 | 取消 | 放弃 / 终止 |
| 确认 | 确认 | 确定（在某些语境 OK，优先确认） |
| 继续 | 继续 / 下一步 | 进入 |
| 关闭 | 关闭 | 收起（仅 UI 折叠用） |
| 导出 | 导出 | 下载（仅文件下载用） |
| 导入 | 导入 | 上传 / 输入 |
| 分享 | 分享 | 共享 |
| 开启/关闭 | 开启 / 关闭 | 启用 / 停用（太正式） |

---

## 3. Button & CTA Copy

### 3.1 一条黄金规则：**按钮是动作，不是标签**

```
❌  OK
❌  Confirm
❌  确定
❌  Submit

✅  Save changes
✅  Delete 3 customers
✅  Send invitation
✅  发送邀请
```

### 3.2 长度控制

| Size | 字数 |
|---|---|
| Primary / Secondary | 英文 1–3 词 · 中文 2–6 字 |
| Link button | 英文 1–4 词 · 中文 2–8 字 |
| Destructive confirm | 英文可长（"Delete alice-chen-acme"） |

### 3.3 Primary CTA 的"主谓宾"原则

好的 primary CTA 自带动词 + 对象：

```
❌  Save
❌  Create

✅  Save changes
✅  Create workflow
✅  Publish report
```

---

## 4. Error Copy（错误文案·最难写）

### 4.1 公式

```
[What happened] + [Why, if safely explainable] + [What user can do]
```

### 4.2 前文后文对照

| ❌ 泛化 | ✅ 具体 |
|---|---|
| Something went wrong | Couldn't reach the database. Check your connection and retry. |
| Invalid input | Enter a valid email (e.g., name@acme.com). |
| 操作失败 | 无法发送邀请。收件人邮箱 bob@acme 缺少域名。 |
| 请稍后重试 | 服务器响应超时（30 秒）。稍后重试或 [联系支持]。 |

### 4.3 避免敷衍的情感化

```
❌  Oops!
❌  哎呀！
❌  Uh oh...

✅  Couldn't connect.
✅  无法连接。
```

### 4.4 Agent Error 特殊规则

Agent 出错时，应该：

1. **直接承认**："I couldn't do X because..."
2. **给替代方案**："Try..."
3. **不自责**：不要说 "I'm so sorry"，专业即可

```
❌  I'm sorry, I made a mistake and couldn't process your request. 😔

✅  I can't send this email because 2 recipients don't have valid addresses.
    [Fix recipients] [Skip invalid and send]
```

---

## 5. Empty State Copy

### 5.1 公式

```
[What's empty] + [Why it might be empty] + [What to do next]
```

### 5.2 例子

```
❌  No data

✅  No customers yet
    Import a CSV or add your first customer manually.
    [Import CSV] [Add customer]
```

```
❌  没有数据

✅  还没有客户
    从 CSV 导入，或手动添加第一个客户。
    [导入 CSV] [添加客户]
```

---

## 6. Placeholder & Helper Text

### 6.1 Placeholder

Placeholder 提供**格式示例**，不重复 label，不作为唯一说明：

```
Label:        Work email
Placeholder:  name@company.com       ← 具体示例 ✅
Placeholder:  Please enter email     ← 重复 label ❌
```

### 6.2 Helper text

Helper 补充 label 没说完的上下文：

```
Label:   API key
Helper:  Find this in Settings → Integrations. Keys start with `sk-`.
```

**硬规**：不要把必填说明放在 placeholder（用户一开始打字就消失了）。要么放 label（加 `*`），要么放 helper。

---

## 7. Confirmation & Destructive Copy

### 7.1 破坏性操作确认

**标题必须包含具体对象**：

```
❌  Confirm delete
❌  Are you sure?

✅  Delete "alice-chen-acme"?
✅  删除"alice-chen-acme"？
```

**body 必须说明后果**：

```
✅  This action cannot be undone. All associated records will be
    purged after 30 days. Linked invoices will remain but marked
    as "customer deleted".
```

### 7.2 确认按钮文字

**不是 "OK"，是重复动作**：

```
❌  [Cancel] [OK]
❌  [取消] [确定]

✅  [Cancel] [Delete customer]
✅  [取消] [删除客户]
```

---

## 8. Success Copy

轻量·事实性：

```
❌  Great! Your settings have been saved successfully! 🎉
❌  太棒了！设置保存成功！🎉

✅  Settings saved.
✅  设置已保存。
```

---

## 9. Toast Copy

Toast 限制：

- 最多 2 行
- 总字数：英文 ≤ 20 词 · 中文 ≤ 40 字
- 不带 emoji（icon 够了）

```
✅  Settings saved.
    Applied to all 12 team members.

✅  设置已保存。
    已应用于全部 12 位成员。
```

---

## 10. Agent Persona（AI 说话方式）

Agent 在气泡里说话的风格：

### 10.1 特征

- **第一人称**："I've found..." / "我找到了..."
- **不过分谦卑**：不说 "I'm just an AI" / "我只是个 AI"
- **适度不确定**：知道的说知道，不知道说不知道
- **引用来源**：有数据说"基于 X 数据显示"，没数据就承认

### 10.2 例句库

```
✅  Based on your Q1 data [1], revenue grew 12.3% YoY.

✅  I don't have access to last quarter's payment records.
    Want me to request access?

✅  I found 3 possible matches for "John Smith". Which did you mean?

✅  This would send emails to 847 customers. Want to preview 3 first?
```

### 10.3 Agent 不该说的话

```
❌  I'm just a language model and can't truly understand...
❌  According to my training data...
❌  作为 AI，我认为...
❌  I'll do my best to help you! 💪
```

### 10.4 Streaming 过程中的 Thinking 文案

```
Thinking... (3s)
Searching database...
Analyzing 1,234 records...
Drafting summary...
Almost done...
```

**硬规**：Thinking 文案必须**随 elapsed time 变化**——超过 5s 不更新会让用户以为卡了。

---

## 11. 字符与符号规范

### 11.1 Dashes / 破折号

| Symbol | 用途 |
|---|---|
| `-` (hyphen) | 连字符：`user-id` `multi-step` |
| `–` (en dash) | 范围：`2020–2024` `Mon–Fri` |
| `—` (em dash) | 强调 / 插入语（英文）：`Ship fast — but not reckless` |

中文内一律用**全角破折号** `——`（两个连用）。

### 11.2 Quote / 引号

| 语言 | 直引号 | 弯引号 |
|---|---|---|
| English body | — | `"smart quotes"` `'apostrophe'` |
| Code / technical | `"straight"` | — |
| 中文 | — | `"中文双引号"` `'中文单引号'` |

代码片段里保持直引号，body 文字用弯引号更 editorial。

### 11.3 Ellipsis

用 Unicode `…` 而非三个点 `...`

### 11.4 空格

| Context | Rule |
|---|---|
| 中英混排 | 手动加半角空格："使用 BYAI 分析" |
| 数字与单位 | 加半角空格："12 MB"（除货币/百分比） |
| 货币 | 不加空格："¥12,345" `$12,345` |
| 百分比 | 不加空格："12.3%" |

---

## 12. 双语并列原则

BYAI 界面会在**一个产品里并存中英用户**。规则：

### 12.1 Label 双语

单一 UI 决定一种语言，不做内联混排双语（如 "保存 / Save"）。根据用户 locale 切。

### 12.2 产品名不翻

`BYAI` `Telos AI` `LeadSpark` 在中文界面内保留英文，不强译。

### 12.3 技术名词

常见技术词**不翻**：API, SDK, Token, Webhook, OAuth, CSV

### 12.4 混合场景示例

```
中文用户界面：
  按钮：  "导出 CSV"      （动词中 + 术语英）
  Hint：  "API Key 以 sk- 开头"  （可接受）
  标题：  "Webhook 配置"

英文用户界面：
  按钮：  "Export CSV"
  Hint：  "API keys start with sk-"
  标题：  "Webhook configuration"
```

---

## 13. Tooltip Copy

Tooltip 严格限制：

- **英文 ≤ 12 词 · 中文 ≤ 30 字**
- 补充信息，**不重复可见文字**
- 完整句子或词组，不要截断

```
Button: [📎]
❌ Tooltip: "Attach"          ← 信息量不足
❌ Tooltip: "This button allows you to attach files..."  ← 太长

✅ Tooltip: "Attach files (⌘U)"
```

---

## 14. Form Label 规范

### 14.1 Label 格式

- 英文：**Sentence case**（只大写首字母）："Work email" 不是 "Work Email" 或 "WORK EMAIL"
- 中文：正常词组，无特殊规则
- 必填：label 后加 ` *`（红色小星）
- 选填：**不标**"(Optional)"（默认选填，标必填更清晰）

### 14.2 例子

```
Work email *
API key
Description    ← 选填，不标
```

---

## 15. Microcopy 快查表（Cheat Sheet）

### 15.1 按钮动作对照

| 场景 | 中 | 英 |
|---|---|---|
| 保存表单 | 保存 / 保存更改 | Save / Save changes |
| 取消操作 | 取消 | Cancel |
| 确认危险操作 | 删除 3 条记录 | Delete 3 records |
| 新建资源 | 创建工作流 | Create workflow |
| 邀请成员 | 发送邀请 | Send invitation |
| 导出数据 | 导出 CSV | Export CSV |
| 订阅升级 | 升级 | Upgrade |
| 下一步 | 下一步 | Continue |
| 上一步 | 上一步 | Back |
| 完成 | 完成 | Done |
| 查看更多 | 查看全部 | View all |
| 应用筛选 | 应用筛选 | Apply filters |
| 清除筛选 | 清除 | Clear |

### 15.2 空态对照

| 场景 | 中 | 英 |
|---|---|---|
| 无数据 | 还没有数据 | No data yet |
| 无结果 | 没有符合条件的结果 | No results match your filters |
| 全部完成 | 已全部处理完 | You're all caught up |
| 无通知 | 暂无新通知 | No new notifications |

### 15.3 错误对照

| 场景 | 中 | 英 |
|---|---|---|
| 必填 | 此项必填 | This field is required |
| 格式错 | 请输入有效的邮箱 | Enter a valid email |
| 网络 | 网络连接失败，请重试 | Couldn't connect. Check your network. |
| 超时 | 请求超时（30 秒），请重试 | Request timed out after 30s. |
| 权限 | 你没有权限访问此资源 | You don't have permission to access this. |
| 不存在 | 未找到此资源 | We couldn't find what you're looking for |

### 15.4 Agent-specific 对照

| 场景 | 中 | 英 |
|---|---|---|
| 思考中 | 思考中…… | Thinking... |
| 生成中 | 生成中（3s） | Generating... (3s) |
| 调用工具 | 正在查询数据库…… | Querying database... |
| 停止 | 停止生成 | Stop generating |
| 重新生成 | 重新生成 | Regenerate |
| 复制 | 复制 | Copy |
| 反馈有用 | 有帮助 | Helpful |
| 反馈无用 | 不准确 | Not helpful |

---

## 16. 反例集

| ❌ 过度殷勤 | ✅ 专业 |
|---|---|
| Please kindly confirm your action | Confirm |
| 请您确认是否继续 | 确认继续 |
| We're so sorry, but... | Couldn't... |
| 非常抱歉，系统出现了问题 | 暂时无法连接 |

| ❌ 过度省略 | ✅ 清晰 |
|---|---|
| OK | Save changes |
| ✓ | Mark as done |
| 提交 | 发送邀请 |

| ❌ 技术词滥用 | ✅ 人话 |
|---|---|
| Deserialization error | Couldn't read the file—is it valid JSON? |
| 请求已被 throttle | 请求过于频繁，请稍后再试 |
