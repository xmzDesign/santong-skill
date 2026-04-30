# Java 后端编码规范入口（分片版）

本文件只做入口、路由和总门禁，不承载全部细则。每次 Java 修改都必须先读本文件，再按本次触发的维度读取 `.harness/docs/java/rules/` 下的分片规则。不要默认加载全部分片，避免上下文过长导致遗漏和幻觉。

版本信息：
- Version: `1.5`
- Last Updated: `2026-04-29`

## 1. 执行顺序

1. 读取当前任务 `spec/contract`、仓库入口 `AGENTS.md` / `CLAUDE.md`。
2. 读取本入口文件，确认本次触发哪些规范维度。
3. 只读取触发维度对应的分片规则。
4. 检查被修改区域的既有实现、测试、配置、命名和本地约定。
5. 在 spec/contract/build/qa 中记录已读取的规则、触发原因、验收方式和未触发理由。

## 2. 规范维度路由

| 维度 | 触发场景 | 必读分片 |
|---|---|---|
| 通用工程 | 任意 Java 代码、配置、SQL、脚手架改动 | `.harness/docs/java/rules/00-core.md` |
| 分层与 DDD | 包结构、Service、Domain、Repository、Adapter、Converter、MapStruct | `.harness/docs/java/rules/java-ddd.md` |
| Dubbo 与公共 API | Dubbo 接口、`ApiResponse<T>`、client/api DTO、公共枚举、RPC Filter | `.harness/docs/java/rules/dubbo-api.md` |
| 日志与异常 | 日志、TraceId、MDC、脱敏、错误码、异常转换、外部错误响应 | `.harness/docs/java/rules/logging-error.md` |
| 持久化与基础设施 | MyBatis、SQL、数据库、Redis、锁、MQ、XXL-Job、配置、HTTP/RPC 适配 | `.harness/docs/java/rules/persistence-infra.md` |
| 测试安全运维 | 测试、鉴权、限流、监控、部署、回滚、文档 | `.harness/docs/java/rules/testing-security.md` |
| 分布式契约 | 外部调用、重试、幂等、线程池、锁、事务、消息、缓存一致性、停机 | `.harness/docs/java/rules/distributed-java-gate.md` |

## 3. 总门禁（每次 Java 修改必须满足）

所有 Java 修改都必须在 build 前复述并在 qa 中核对以下 5 条总门禁：

1. **先契约后实现**：必须先有 spec/contract；若缺少 Java 总门禁、触发分片规则或分布式 Java 门禁声明，先补齐再编码。
2. **先本地后通用**：先看本地已有实现和约定，优先复用已有工具、异常、响应包装、转换器、配置和命名。
3. **边界不被突破**：入口层只依赖应用接口，Application 不直连 Mapper，Domain 不依赖基础设施，对外契约不暴露内部模型。
4. **风险显式落地**：公共 API、SQL、缓存、消息、事务、配置、发布、回滚、安全影响必须写入 spec/contract 验收项。
5. **验证可追溯**：必须运行可用测试和 `convention-check`；无法运行时写明阻塞原因和最小建议验证命令。

## 4. 维度核心门禁（按触发维度追加）

### 4.1 通用工程门禁

1. 最小安全变更，不无依据扩范围。
2. 保持公共契约兼容，破坏性变更必须由任务明确要求。
3. 不重复造工具类、异常类、转换器、响应包装或框架胶水。
4. 新增/修改方法必须有中文注释，说明用途、参数、返回值和副作用。
5. 交付摘要必须记录读取的分片、验证命令和剩余风险。

### 4.2 分层与 DDD 门禁

1. Controller / Provider / Job 只能依赖应用服务接口，不能注入 `Impl`。
2. `XxxAppService` 必须是接口，`XxxAppServiceImpl` 必须实现对应接口。
3. Domain 不依赖 Spring、MyBatis、Redis、MQ、HTTP Client 或数据库 Entity。
4. Application 不直接操作 MyBatis Mapper；通过 Domain Repository/Adapter 抽象访问。
5. MapStruct 必须设置 `unmappedTargetPolicy = ReportingPolicy.ERROR`。

### 4.3 Dubbo 与公共 API 门禁

1. 公共 client/api service 方法统一返回 `ApiResponse<T>`。
2. Public DTO 必须实现 `Serializable` 并声明 `serialVersionUID`。
3. 公共枚举对外使用 `name()` 或稳定 code，禁止使用 `ordinal()`。
4. 公共 API 不暴露 Domain、Entity、DO、Mapper、Infrastructure 内部类型。
5. 非幂等核心写接口必须明确 `retries = 0` 或记录项目既有策略。

### 4.4 日志与异常门禁

1. Web/Dubbo/MQ/异步入口必须生成或传递 TraceId，并在结束时清理 MDC。
2. 日志必须脱敏，禁止输出 token、密码、密钥、签名、授权头等敏感值。
3. ERROR 日志必须带异常堆栈和业务上下文。
4. 外部错误响应不得暴露原始系统异常、SQL、堆栈或第三方原始错误。
5. 业务异常使用项目统一异常和错误码，不新增随意的异常体系。

### 4.5 持久化与基础设施门禁

1. MyBatis SQL 必须写在 XML Mapper，禁止注解内联 SQL。
2. SQL 禁止 `select *`、`${}`、`resultClass`，统计行数使用 `count(*)`。
3. 金额使用 Java `BigDecimal` 和数据库 `DECIMAL(18,3)`，更新记录必须维护 `update_time`。
4. 分页必须稳定排序；count 为 0 时不继续查明细。
5. Redis key 必须有命名空间，业务缓存必须设置 TTL；锁必须有超时和持有者校验释放。

### 4.6 测试安全运维门禁

1. 不得硬编码或提交任何密码、token、API key、私钥、签名密钥。
2. 受保护操作必须有鉴权、输入校验和必要的限流/审计。
3. 核心业务逻辑和公共 API 变更必须补充正常/异常路径测试。
4. 监控指标必须控制标签基数，不使用 raw ID 作为高基数 label。
5. 生产影响变更必须写明发布验证、灰度、回滚或人工确认方案。

### 4.7 分布式契约门禁

1. 所有 Java 改动必须声明分布式 Java 门禁：未触发要说明理由，触发要列条款。
2. 外部调用必须有超时、重试上限、退避策略和幂等前提。
3. 线程池、队列、锁必须有业务命名、容量/超时限制和拒绝/失败策略。
4. 跨服务一致性必须有事务边界、补偿路径、终止条件和人工接管方案。
5. MQ/异步/缓存/停机必须可观测、可重放或可降级，并能处理在途任务。

## 5. Plan / Build / QA 要求

- **Plan**：spec 必须列出触发维度、读取分片、每条门禁的实现方式、验收方式和自动检查项。
- **Build**：编码前必须复述总门禁和触发维度门禁；缺失 contract 验收项时先补 contract。
- **QA**：逐项核对总门禁、触发维度门禁、`convention-check` 输出和测试结果；fail 必须修复，warn 必须解释或修复。

## 6. 自动检查映射

`.codex/hooks/convention-check.py` 与 `.claude/hooks/convention-check.py` 会拦截可机器识别的问题：

- Controller / Provider / Job 依赖 `*AppServiceImpl`：fail。
- `XxxAppServiceImpl` 未实现 `XxxAppService`：fail。
- `XxxAppService` 被写成 class 而不是 interface：fail。
- MapStruct 缺少 `unmappedTargetPolicy = ReportingPolicy.ERROR`：fail。
- 金额字段使用 `double/float`：fail。
- SQL 金额列使用 `double/float` 或非 `DECIMAL(18,3)`：fail。
- PageHelper 附近缺少稳定排序：warn。
- Redis 业务缓存写入缺少 TTL：fail。
- MyBatis 注解 SQL、`select *`、`${}`、`resultClass`、非 `count(*)`：fail。
- Public DTO 缺少 `Serializable` 或 `serialVersionUID`：fail。
- 公共 API 方法未返回 `ApiResponse<T>`：fail。
- 外部可见枚举使用 `ordinal()`：fail。
- 疑似硬编码密钥或敏感日志：fail。
- 新增 `logback` 依赖链：fail。

机器无法完全判断补偿、降级、人工接管、发布停机等架构性要求，必须在 spec/contract/QA 中人工确认。
