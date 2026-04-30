# 持久化与基础设施规则

本文件适用于数据库、MyBatis、Repository、Redis、分布式锁、MQ、HTTP Client、Adapter、配置、XXL-Job 和基础设施服务。

## 1. 适用场景

- 新增或修改表结构、索引、SQL、Mapper、Entity、Repository 实现。
- 接入 Redis、分布式锁、MQ、线程池、HTTP/RPC Adapter、XXL-Job。
- 新增配置项、配置中心 key、基础设施异常转换或三方调用。

## 2. 核心门禁（触发本维度必须满足）

1. **Mapper 边界清晰**：MyBatis Mapper 只在 Infrastructure Repository 实现中使用，Application/Domain 禁止直接调用 Mapper。
2. **SQL 写在 XML**：SQL 必须写在 `resources/mapper/**/*.xml`，禁止 `@Select/@Update/@Insert/@Delete` 内联 SQL。
3. **SQL 基础安全**：禁止 `select *`、`${}`、`resultClass`；统计行数使用 `count(*)`。
4. **数据语义稳定**：金额使用 Java `BigDecimal` 和数据库 `DECIMAL(18,3)`；更新必须维护 `update_time`；分页必须稳定排序。
5. **基础设施可治理**：Redis key 有命名空间且业务缓存有 TTL；锁有超时和持有者校验；MQ/异步/Job 可观测、可重试、可降级。

## 3. Repository 与 Mapper 边界

- Domain 定义 Repository 和 Adapter 接口。
- Infrastructure 实现 Repository 和 Adapter 接口。
- MyBatis Mapper 访问只出现在 Infrastructure Repository 实现中。
- Entity 与 Domain Model 的转换放在 Infrastructure Converter。
- 数据库 Entity 不得泄露到 Application、Domain、Controller 或公共 API。

## 4. 数据库设计

- 表名、字段名、索引名使用 `lower_snake_case`。
- 表必须包含主键 `id`。
- 类外键字段使用 `<entity>_id`。
- 表必须包含 `create_time` 和 `update_time`。
- 软删除表使用 `is_deleted`，其中 `0` 表示有效，`1` 表示删除。
- 金额字段使用 `DECIMAL(18,3)`。
- 时间字段使用 `DATETIME`。
- 字符集默认使用 `utf8mb4` 和 `utf8mb4_unicode_ci`，除非项目已有不同配置。
- 禁止数据库外键和级联更新/删除，关系语义由应用/领域逻辑维护。
- 禁止用存储过程承载业务逻辑。

## 5. MyBatis 与 SQL

- Mapper 接口只保留方法签名，不写内联 SQL。
- 查询列必须显式列出，禁止 `select *`。
- XML 参数绑定使用 `#{}`，禁止对用户或业务参数使用 `${}`。
- 每张表必须使用显式 `<resultMap>`，禁止 `resultClass`。
- POJO boolean 属性不以 `is` 开头；数据库 boolean 字段可用 `is_` 前缀，并通过 `resultMap` 显式映射。
- 查询结果禁止直接输出 `HashMap` 或 `Hashtable`，必须定义 DO/DTO 和 `<resultMap>`。
- 行数统计使用 `count(*)`，不用 `count(column)` 或 `count(常量)`。
- `sum(column)` 可能返回 NULL，业务 SQL 使用 `IFNULL(SUM(column), 0)` 或等价写法。
- NULL 判断按项目约定使用 `ISNULL(column)` / `NOT ISNULL(column)`。
- 多表查询、更新、删除的字段必须带表别名或表名。
- 分页查询先 count；count 为 `0` 时直接返回空页，不继续查明细。
- PageHelper 分页必须有稳定排序，例如 `id desc` 或 `created_time desc`。
- 更新语句必须维护 `update_time`。
- 数据订正、删除、批量更新必须先 select 命中范围，再执行，并保留回滚方案。

## 6. SQL 编写建议

- 多表 SQL 别名建议使用 `as t1`、`as t2`、`as t3`。
- 尽量避免 `in`；必须使用时评估集合大小，通常控制在 1000 以内。
- 区分 `LENGTH` 字节数和 `CHARACTER_LENGTH` 字符数。
- 应用代码中避免 `TRUNCATE TABLE`，它不可回滚且风险高。
- 避免在大批量或复杂链路上包过宽事务。
- 更新 API 不要设计得过宽，只更新当前业务动作需要的字段。
- 使用 `@Transactional` 前必须确认 QPS 影响、事务边界、回滚范围和外部副作用补偿。

## 7. Redis 与分布式锁

Redis key：

- 遵循项目既有命名空间。
- 默认格式：`{service}:{feature}:{companyId}:{channelType}`。
- 锁格式：`{service}:lock:{feature}:{identifier}`。
- 禁止无命名空间 key，避免跨租户、跨服务、跨环境冲突。
- 业务缓存写入必须设置 TTL。
- 缓存设计必须说明失效、降级和穿透处理。

分布式锁：

- 锁必须有过期时间。
- 锁 value 必须唯一，优先使用项目既有 `UUIDUtil`。
- 解锁必须放在 `finally`。
- 解锁必须使用校验 value 的安全释放模式。
- 禁止直接 `delete` 释放锁。

禁止：

```java
redisTemplate.opsForValue().set("orderCache", value);
```

推荐：

```java
String key = "order:detail:" + orderId;
redisTemplate.opsForValue().set(key, value, 10, TimeUnit.MINUTES);
```

## 8. MQ、异步与线程池

MQ：

- 复用已有 Producer 基类和 MQ 配置。
- Topic、Tag 优先来自配置，不硬编码。
- Producer 初始化顺序遵循项目约定，需要时保留 `@DependsOn`。
- JSON payload 构造遵循项目既有风格。
- MQ 日志记录业务定位信息，但不得泄露敏感值。
- 跨服务消息必须携带 `traceId`、`messageId` 和业务 key。

异步与线程池：

- 异步 Executor 集中配置，通常放在 `AsyncConfig`。
- 使用 `MdcTaskDecorator` 或既有上下文传播机制保留 TraceId/MDC。
- 使用有界队列和明确拒绝策略。
- 保留优雅停机能力。
- 项目已使用 Micrometer 时，线程池指标必须接入监控。

## 9. XXL-Job 与配置

XXL-Job：

- 调度任务使用 XXL-Job。
- Job Handler 放在 `bootstrap.job`。
- Handler 命名建议使用 `{app}:{domain}:{action}`。
- Job 必须幂等、可重试、可观测，并记录开始、结束、耗时、结果。
- Handler 调用 Application 接口，不嵌入复杂业务细节。

配置：

- 共享配置放在 `application.yml`。
- 环境配置放在 `application-{profile}.yml`。
- 新配置 key 使用 `{service}.{module}.{key}`。
- `@Value("${key:default}")` 只有在默认值明确安全时使用。
- 关键配置变更必须可审计、可回滚。
- 密钥必须加密存储或放入批准的配置中心。
- 禁止在源码、测试、日志、文档示例中硬编码密钥。

## 10. 基础设施异常

- 技术失败返回业务/Application 层时，按项目约定转换为项目异常。
- 包装异常时必须保留原始 cause。
- ERROR 日志必须带异常堆栈。
- 除非明确安全且必要，禁止向外部 API 调用方暴露三方原始错误细节。

## 11. 验收与自动检查

- `convention-check` 会拦截 MyBatis 注解 SQL、`select *`、`${}`、`resultClass`、非 `count(*)`。
- `convention-check` 会拦截金额使用 `double/float` 或 SQL 金额列非 `DECIMAL(18,3)`。
- `convention-check` 会提示 PageHelper 附近缺少稳定排序。
- `convention-check` 会拦截 Redis 业务缓存写入缺少 TTL。
- 人工验收必须确认数据订正、事务、锁、MQ、异步、配置和回滚方案已进入 contract。
