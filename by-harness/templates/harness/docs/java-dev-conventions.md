# Java 后端编码规范入口（Harness 分片版）

本文件是 Java 规范入口，不承载全部细则。开始 Java 任务时先读本文件，再按触发项读取 `.harness/docs/java/rules/` 下的对应规则，避免一次性加载过长上下文导致遗漏或幻觉。

版本信息：
- Version: `1.4`
- Last Updated: `2026-04-29`

## 1. 适用范围

- Java / Spring Boot / Dubbo / XXL-Job / MyBatis / Redis / MQ 后端项目。
- 涉及分布式调用、缓存、消息、并发控制、事务一致性、发布停机的业务系统。
- 需要 AI 辅助编码且必须可审计、可回滚、可验收的工程场景。

## 2. 规则级别

- MUST：必须遵守，违反即不允许合并。
- SHOULD：强烈建议，偏离必须说明理由并经评审确认。
- MUST NOT：明确禁止，违反视为高风险缺陷，必须整改后再发布。

## 3. 必读顺序

1. 读取当前任务 `spec/contract` 与仓库入口 `AGENTS.md` / `CLAUDE.md`。
2. 读取本入口文件。
3. 按下方 Rule Loading Map 只读取与任务相关的规则文件。
4. 检查被触碰代码区域的既有实现、测试、配置和命名。
5. 只有当分片规则不足以判断时，再读取仓库本地更详细的标准文档或历史 ADR。

## 4. Rule Loading Map

| 触发项 | 必读规则 |
|---|---|
| 通用工程约束、前置闸门、技术栈、完成口径 | `.harness/docs/java/rules/00-core.md` |
| Java 包职责、DDD 分层、命名、依赖注入、MapStruct、应用服务接口实现 | `.harness/docs/java/rules/java-ddd.md` |
| Dubbo、`ApiResponse<T>`、client/api DTO、公共 API、兼容性、RPC filter | `.harness/docs/java/rules/dubbo-api.md` |
| 日志、TraceId、MDC、脱敏、异常模型、错误响应 | `.harness/docs/java/rules/logging-error.md` |
| MyBatis、SQL、数据库、Redis、锁、MQ、XXL-Job、配置、基础设施 | `.harness/docs/java/rules/persistence-infra.md` |
| 安全、测试、监控、部署、文档、质量门禁 | `.harness/docs/java/rules/testing-security.md` |
| 外部调用、幂等、重试、锁、事务、消息、缓存一致性、异步、发布停机 | `.harness/docs/java/rules/distributed-java-gate.md` |

## 5. Java Gate 触发条件

出现以下任一情况，必须在 plan/build/qa 中显式处理 Java Gate：

- 新增或修改 `Controller`、Dubbo `Provider`、XXL-Job `Handler`。
- 新增或修改 `AppService`、`ServiceImpl`、领域服务、应用编排逻辑。
- 新增或修改 Dubbo 接口、公共 API、`ApiResponse`、request/response DTO、公共枚举或 client/api 包。
- 新增或修改 MapStruct mapper、DTO/DO/VO 转换。
- 新增或修改金额字段、金额计算、表结构、SQL、Mapper XML。
- 新增或修改分页查询、列表查询、导出查询。
- 新增或修改 Redis 缓存、分布式锁、业务 key。
- 新增或修改日志、TraceId、MDC、异常转换、错误码、配置、密钥、开关、灰度参数。
- 新增或修改测试、安全、鉴权、限流、监控指标、部署配置或文档化运行行为。
- 新增或修改外部调用、Dubbo/HTTP/RPC 客户端、MQ、异步任务、线程池、批量处理、事务边界、补偿逻辑、发布停机相关逻辑。

## 6. Plan Gate

Spec 中必须新增 **Java Gate** 小节，逐项声明本次是否涉及：

- Service 接口/实现：是/否，涉及类名。
- Controller / Provider / Job 依赖方向：是/否，入口类只能依赖接口。
- MapStruct：是/否，mapper 名称与 `unmappedTargetPolicy = ERROR`。
- 金额：是/否，Java 类型、数据库类型、精度与舍入口径。
- 分页/查询：是/否，是否单表优先，PageHelper 与稳定排序字段。
- Redis：是/否，key 命名空间、TTL、缓存失效方式。
- 日志异常：是/否，TraceId/MDC、LogSanitizer、错误码、异常转换边界。
- 配置/密钥：是/否，配置来源、审计、回滚、脱敏方式。
- 公共 API/Dubbo：是/否，`ApiResponse<T>`、DTO 序列化、枚举序列化、兼容性策略。
- DDD 分层：是/否，涉及模块、依赖方向、Repository/Adapter/Converter 落位。
- 测试安全监控：是/否，鉴权/限流/输入校验/输出脱敏、测试覆盖、指标与告警影响。
- Distributed Java Gate：必须声明“未触发”或列出 `.harness/docs/java/rules/distributed-java-gate.md` 的触发条款。

如果 spec 缺少 Java Gate 或 Distributed Java Gate，小范围任务也必须在 build 前补齐；不能用“改动很小”跳过。

## 7. Build Checklist

编码前必须复述本次适用清单：

- [ ] 已读取本入口文件与任务触发的分片规则。
- [ ] Service 使用 `XxxAppService` 接口 + `XxxAppServiceImpl` 实现。
- [ ] Controller / Dubbo Provider / Job Handler 只注入接口，禁止依赖 `Impl`。
- [ ] MapStruct 只做结构映射，且 `unmappedTargetPolicy = ReportingPolicy.ERROR`。
- [ ] 新增/修改函数与方法有中文注释，说明用途、关键参数、返回值、副作用。
- [ ] 金额字段 Java 使用 `BigDecimal`，数据库使用 `DECIMAL(18,3)`，禁止 `double/float`。
- [ ] 查询默认单表优先；分页统一 PageHelper，并有稳定排序。
- [ ] Redis key 有统一命名空间；业务缓存写入必须设置 TTL。
- [ ] Web 日志走 AOP；Dubbo 日志走 Filter；关键节点日志包含 `traceId/bizId/resultCode/costMs`。
- [ ] 公共 client/api service 方法统一返回 `ApiResponse<T>`，Public DTO 实现 `Serializable` 并声明 `serialVersionUID`。
- [ ] 公共枚举外部序列化使用 `name()`，禁止 `ordinal()`。
- [ ] 对外契约不暴露 Domain 模型、数据库 Entity 或 Infrastructure 内部类型。
- [ ] 关键配置可审计、可回滚；密钥托管，禁止硬编码。
- [ ] 已声明 Distributed Java Gate：未触发需说明原因；触发时逐条对照分布式规则。

## 8. 自动检查映射

`.codex/hooks/convention-check.py` 与 `.claude/hooks/convention-check.py` 会尽量自动拦截可机器识别的问题：

- Controller / Provider / Job 依赖 `*AppServiceImpl`：fail。
- `XxxAppServiceImpl` 未实现 `XxxAppService`：fail。
- `XxxAppService` 被写成 class 而不是 interface：fail。
- MapStruct `@Mapper` 缺少 `unmappedTargetPolicy = ReportingPolicy.ERROR`：fail。
- 金额字段使用 `double/float`：fail。
- SQL 金额列使用 `double/float` 或非 `DECIMAL(18,3)`：fail。
- `PageHelper.startPage` 附近缺少稳定排序：warn。
- Redis 业务缓存写入缺少 TTL：fail。
- 疑似硬编码密钥：fail。
- 新增/修改方法缺少中文注释：warn。
- MyBatis 注解内联 SQL、`select *`、`${}`、`resultClass`、非 `count(*)` 统计：fail。
- Public DTO 缺少 `Serializable` 或 `serialVersionUID`：fail。
- 公共 API 方法未返回 `ApiResponse<T>`：fail。
- `ordinal()` 用于外部可见枚举语义：fail。
- 日志中直接输出敏感字段、请求头或 token/password/secret：fail。
- 新增 `logback` 依赖链：fail。
- 无界线程池、无容量队列、无超时锁、事务中疑似外部调用、消息缺少 `traceId/messageId`：warn/fail。

机器无法完全判断 Web AOP、Dubbo Filter、关键配置审计回滚、补偿路径、发布停机方案等架构性要求，必须在 spec/contract/QA 报告中显式说明。

## 9. 完成前摘要

交付摘要必须写明：

- 本次读取或适用的 Java 分片规则。
- 本次未适用的高风险分片及理由。
- Java Gate 与 Distributed Java Gate 的触发结论。
- 实际运行的验证命令，或无法运行时的最小建议验证命令。
