# 冲刺契约：{{FEATURE_NAME}}

## 元信息（Meta）

- **规格文件（Spec）**：`.harness/docs/specs/{{FEATURE_NAME}}.md`
- **创建时间（Created）**：{{DATE}}
- **状态（Status）**：draft
- **最大迭代次数（Max Iterations）**：3
- **执行门禁（Execution Gate）**：单元测试通过（QA 报告非阻塞）

## 规范引用（Norm References）

本节必须从 spec 派生，不能只写“已阅读”。

| 规范文件 | 是否适用 | 适用/不适用原因 | 派生验收项 |
|---|---|---|---|
| `.harness/docs/java-dev-conventions.md` | 是/否 | | |
| `.harness/docs/java-dev-conventions.md` 第 14 章 | 未触发/触发 | | |
| `.harness/docs/frontend-dev-conventions.md` | 是/否 | | |
| `.harness/docs/frontend/rules.md` | 是/否 | | |
| `.harness/docs/frontend/code-design.md` | 是/否 | | |
| `.harness/docs/frontend/ui-design.md` | 是/否 | | |
| `.harness/docs/frontend/references/byai-ds-v/<page>.html` | 是/否 | | |

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

### Distributed Java Gate 检查（所有 Java 改动必须声明）

- [ ] 已在 spec/contract/build/qa 中声明 Distributed Java Gate：未触发 / 触发
- [ ] 若声明未触发，已说明理由，且本次 Java 改动不涉及外部调用、Dubbo/HTTP/RPC、MQ、异步、线程池、锁、Redis、事务、补偿、发布停机
- [ ] 若触发资源隔离：线程池/队列/Worker 池有业务命名、容量、隔离和拒绝策略
- [ ] 若触发外部调用：每个调用有超时、重试上限、退避策略、可重试错误分类和幂等前提
- [ ] 若触发写操作/Job/消息消费：有幂等键（请求号/业务主键/messageId）和重复执行保护
- [ ] 若触发分布式锁：锁 key 有命名空间，获取有等待时间和租约时间，释放在 `finally` 且校验持有者
- [ ] 若触发事务/跨服务一致性：事务边界最小化，跨服务一致性有 Outbox/Saga/TCC/补偿路径、终止条件和人工接管
- [ ] 若触发缓存：TTL、空值缓存、防穿透/击穿/雪崩、降级方案和失效策略已明确
- [ ] 若触发 MQ/事件：消息携带 `traceId/messageId/业务键`，消费端幂等，失败进入重试/失败表/死信且可重放
- [ ] 若触发批量异步：队列有界，具备阈值触发 + 定时触发，停机前冲刷剩余数据
- [ ] 若触发容错降级：失败可追踪、可重放、可终止，告警限流去重，有人工接管入口
- [ ] 若触发异步边界：`MDC/ThreadLocal` 正确透传并清理，关键链路具备日志/指标/trace
- [ ] 若触发配置安全：集中配置、环境隔离、变更审计、回滚、鉴权、限流、脱敏、密钥托管已明确
- [ ] 若触发发布停机：健康检查、灰度放量、快速回滚、停止接收新流量、在途任务处理、队列冲刷方案已明确
- [ ] 对机器无法验证的补偿、降级、人工接管、发布回滚项，已列入人工确认或发布检查清单

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
