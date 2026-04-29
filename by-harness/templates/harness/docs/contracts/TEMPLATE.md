# 冲刺契约：{{FEATURE_NAME}}

## 元信息（Meta）

- **规格文件（Spec）**：`.harness/docs/specs/{{FEATURE_NAME}}.md`
- **创建时间（Created）**：{{DATE}}
- **状态（Status）**：draft
- **最大迭代次数（Max Iterations）**：3
- **执行门禁（Execution Gate）**：单元测试通过（QA 报告非阻塞）

## 范围（Scope）

### 范围内（In Scope）

-

### 范围外（Out of Scope）

-

## 验收标准（Acceptance Criteria）

每条标准都必须可机器验证。

| # | 标准（Criterion） | 验证方法（Verification Method） | 状态（Status） |
|---|-----------|-------------------|--------|
| 1 | | | [ ] |
| 2 | | | [ ] |
| 3 | | | [ ] |
| 4 | | | [ ] |
| 5 | | | [ ] |

### 验证方法说明（Verification Methods）

- **unit**：阅读代码并验证逻辑
- **playwright**：通过 Playwright MCP 进行 E2E 测试
- **devtools**：通过 Chrome DevTools 检查（控制台错误、网络）
- **visual**：通过 zai-mcp-server 做截图对比
- **build**：编译/构建成功
- **manual**：需要用户手动验证

### Java Gate 检查（若适用）

- [ ] 已读取 `.harness/docs/java-dev-conventions.md`
- [ ] 已在 spec/build 中列出本次触发的 Java Gate
- [ ] Service 为 `XxxAppService` 接口 + `XxxAppServiceImpl` 实现
- [ ] Controller / Dubbo Provider / Job Handler 只依赖 Service 接口
- [ ] MapStruct 已配置 `unmappedTargetPolicy = ReportingPolicy.ERROR`
- [ ] 新增/修改函数与方法有中文注释（用途、关键参数、返回值、副作用）
- [ ] 金额 Java 类型为 `BigDecimal`，数据库为 `DECIMAL(18,3)`，无 `double/float`
- [ ] 分页使用 PageHelper，且具备稳定排序
- [ ] Redis key 有统一命名空间，业务缓存写入有 TTL
- [ ] Web 日志走 AOP；Dubbo 日志走 Filter；关键节点日志字段完整
- [ ] 关键配置可审计、可回滚；无硬编码密钥
- [ ] 已运行 convention-check，fail 已修复，warn 已修复或说明风险

### 前端三层规范检查（若适用）

- [ ] 已读取 `.harness/docs/frontend-dev-conventions.md`
- [ ] 已按任务类型读取 `.harness/docs/frontend/rules.md`
- [ ] 已按任务类型读取 `.harness/docs/frontend/code-design.md`
- [ ] 已按任务类型读取 `.harness/docs/frontend/ui-design.md`
- [ ] 若涉及页面级视觉，已打开 `.harness/docs/frontend/references/byai-ds-v/` 对应 HTML 参考页
- [ ] 已明确页面类型：Dashboard / Table / Form / Settings / Agent / Data-viz / Login / Onboarding / Other
- [ ] 验收标准覆盖 loading / empty / error / disabled / focus-visible
- [ ] 验收标准覆盖 token/硬编码检查、响应式或截图验证

## 冲刺日志（Sprint Log）

| 迭代轮次 | Generator 输出 | Evaluator 评分 | 问题 |
|-----------|-----------------|-----------------|--------|
| | | | |

## 签署确认（Sign-off）

- **Generator**：[ ] 同意标准与范围
- **Evaluator**：[ ] 同意验证方式
- **User**：[ ] 批准范围与标准
