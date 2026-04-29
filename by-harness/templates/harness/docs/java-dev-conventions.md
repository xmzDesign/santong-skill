# 分布式 Java 后端编码规范（Harness 完整版）

本规范用于 Java 后端项目在多人协作、跨仓协作、AI 并行开发场景下的统一工程约束与执行闸门。

版本信息：
- Version: `1.1`
- Last Updated: `2026-04-28`

## 1. 适用范围

- 使用 Java/Spring Boot 的后端仓库。
- 涉及分布式调用、缓存、消息、并发控制、事务一致性等场景的业务系统。
- 需要通过 AI 辅助编码且必须可审计、可回滚、可验收的工程场景。

## 2. 规范级别定义

- MUST：必须遵守，违反即不允许合并。
- SHOULD：强烈建议，偏离必须说明理由并经评审确认。
- MUST NOT：明确禁止，违反视为高风险缺陷，必须整改后再发布。

## 3. 通用工程规范（适用于所有后端任务）

- 先读取任务 `spec/contract`，再开始编码。
- 先校验技术栈、边界约束与依赖方向，再做实现决策。
- 改动前必须明确“影响范围 + 回滚路径 + 验收口径”。
- 关键节点日志必须可追踪（`traceId`、`bizId`、`resultCode`、`costMs`）。
- 禁止无依据扩范围、跨层偷依赖、跳过验证直接交付。

## 4. AI Coding 前置闸门（强制）

开始任何代码、脚手架、配置或 SQL 改动前，必须显式确认：

1. 已阅读当前任务 `spec/contract` 与仓库范围约束文档。
2. 已阅读本规范及来源标准文档。
3. SQL 位置确认：MyBatis SQL 写在 XML Mapper，禁止 Java 注解内联 SQL。
4. SQL 语义确认：统计、NULL 判断、分页、多表列限定、数据订正已逐条满足第 8 章。
5. ORM 映射确认：字段清单、`resultMap`、参数绑定、更新字段范围与 `update_time` 已逐条满足第 8 章。
6. 调度约束确认：定时任务统一基于 XXL-Job，不新增 ad-hoc 调度框架。
7. 数据库策略确认：migration 默认不是必选交付项，按任务卡显式要求执行。
8. 分布式约束确认：凡涉及并发、锁、缓存、消息、事务一致性、容错、可观测性、发布停机，逐项满足第 14 章。

若缺失任一确认，不得直接实现。

## 5. 技术栈基线

### 5.1 核心运行时

- JDK：`1.8`
- 构建工具：Maven（支持多模块）

### 5.2 禁止项

- MUST NOT：新增 `gson` 作为业务 JSON 入口。
- MUST NOT：并行引入手写 `jackson` 业务序列化入口（Spring Web 默认消息转换链路除外）。
- MUST NOT：新增 `logback` 依赖链或相关 API。

## 6. 分层架构与依赖方向（必须）

### 6.1 分层职责

- `api`：对外契约、DTO、Dubbo/HTTP 接口定义。
- `domain`：聚合、实体、值对象、领域服务、领域规则。
- `application`：用例编排、事务边界、流程控制、权限校验。
- `infrastructure`：仓储实现、Mapper、缓存、消息、RPC 适配。
- `bootstrap`：启动装配、Web 入口、AOP、Job Handler。

### 6.2 依赖方向

- 允许：`bootstrap -> application -> domain`
- 允许：`bootstrap -> infrastructure -> application/domain`
- 禁止：`domain -> application/infrastructure/bootstrap`
- 禁止：`application -> bootstrap`
- 禁止：跨应用直接读写业务表，跨应用交互必须走 API/消息契约。

## 7. Java Gate：实现硬性规则

本章不是普通阅读材料。只要任务涉及 Java、Spring Boot、Dubbo、XXL-Job、MyBatis、Redis、配置、日志、金额、分页、MapStruct 或 Service/Controller 分层，就必须在 Plan、Build、QA、Stop hook 四个位置重复检查。

### 7.1 触发条件

出现以下任一情况，本章自动触发：

- 新增或修改 `Controller`、Dubbo `Provider`、XXL-Job `Handler`。
- 新增或修改 `AppService`、`ServiceImpl`、领域服务、应用编排逻辑。
- 新增或修改 MapStruct mapper、DTO/DO/VO 转换。
- 新增或修改金额字段、金额计算、表结构、SQL、Mapper XML。
- 新增或修改分页查询、列表查询、导出查询。
- 新增或修改 Redis 缓存、分布式锁、业务 key。
- 新增或修改日志、配置、密钥、开关、灰度参数。

### 7.2 Plan Gate：规格阶段必须声明

Plan/spec 中必须新增 **Java Gate** 小节，逐项声明本次是否涉及：

- Service 接口/实现拆分：是/否，涉及类名。
- Controller / Provider / Job 依赖方向：是/否，入口类只能依赖接口。
- MapStruct：是/否，mapper 名称与 `unmappedTargetPolicy = ERROR`。
- 金额：是/否，Java 类型、数据库类型、精度与舍入口径。
- 分页/查询：是/否，是否单表优先，PageHelper 与稳定排序字段。
- Redis：是/否，key 命名空间、TTL、缓存失效方式。
- 日志：是/否，Web AOP、Dubbo Filter、关键节点日志字段。
- 配置/密钥：是/否，配置来源、审计、回滚、脱敏方式。

如果 spec 没有 Java Gate，小范围任务也必须在 build 前补齐。

### 7.3 Build Checklist：编码前必须复述

编码前必须先列出本次适用清单：

- [ ] Service 使用 `XxxAppService` 接口 + `XxxAppServiceImpl` 实现。
- [ ] Controller / Dubbo Provider / Job Handler 只注入 `XxxAppService` 接口，禁止依赖 `Impl`。
- [ ] MapStruct 只做结构映射，且 `unmappedTargetPolicy = ReportingPolicy.ERROR`。
- [ ] 新增/修改函数与方法有中文注释，说明用途、关键参数、返回值、副作用。
- [ ] 金额字段 Java 使用 `BigDecimal`，数据库使用 `DECIMAL(18,3)`，禁止 `double/float`。
- [ ] 查询默认单表优先；分页统一 PageHelper，并有稳定排序。
- [ ] Redis key 有统一命名空间；业务缓存写入必须设置 TTL。
- [ ] Web 日志走 AOP；Dubbo 日志走 Filter；关键节点日志包含 `traceId/bizId/resultCode/costMs`。
- [ ] 关键配置可审计、可回滚；密钥托管，禁止硬编码。
- [ ] 业务 JSON 序列化/反序列化统一走 `fastjson2` 封装。

### 7.4 正反例

#### Service 接口与依赖方向

禁止：

```java
@RestController
public class OrderController {
    @Resource
    private OrderAppServiceImpl orderAppService;
}
```

推荐：

```java
public interface OrderAppService {
    /**
     * 创建订单，完成参数校验与应用层编排。
     *
     * @param command 创建订单命令，包含用户、商品和金额信息
     * @return 创建后的订单结果
     */
    OrderCreateResult createOrder(OrderCreateCommand command);
}

@Service
public class OrderAppServiceImpl implements OrderAppService {
    @Override
    public OrderCreateResult createOrder(OrderCreateCommand command) {
        // ...
    }
}

@RestController
public class OrderController {
    @Resource
    private OrderAppService orderAppService;
}
```

#### MapStruct

禁止：

```java
@Mapper(componentModel = "spring")
public interface OrderConvert {
}
```

推荐：

```java
@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.ERROR)
public interface OrderConvert {
}
```

#### 金额与分页

禁止：

```java
private double payAmount;
PageHelper.startPage(pageNo, pageSize);
List<OrderDO> list = orderMapper.selectByCondition(query);
```

推荐：

```java
private BigDecimal payAmount;
PageHelper.startPage(pageNo, pageSize).setOrderBy("id desc");
List<OrderDO> list = orderMapper.selectByCondition(query);
```

DDL 金额列必须使用：

```sql
pay_amount DECIMAL(18,3) NOT NULL DEFAULT 0.000 COMMENT '支付金额'
```

#### Redis

禁止：

```java
redisTemplate.opsForValue().set("orderCache", value);
```

推荐：

```java
String key = "order:detail:" + orderId;
redisTemplate.opsForValue().set(key, value, 10, TimeUnit.MINUTES);
```

#### 配置与密钥

禁止：

```java
private static final String SECRET_KEY = "abc123";
```

推荐：

```java
@Value("${payment.secret-key}")
private String secretKey;
```

### 7.5 自动检查映射

`convention-check.py` 会尽量自动拦截可机器识别的问题：

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

机器无法完全判断 Web AOP、Dubbo Filter、关键配置审计回滚等架构性要求，必须在 spec/contract/QA 报告中显式说明。

## 8. 数据库与 MyBatis 规范

本章为 SQL 与 ORM 映射的强制编码底线。凡新增或修改 Mapper、XML SQL、分页查询、数据订正脚本、表结构说明，均必须逐项自检。

### 8.1 SQL 基础约束（MUST）

- 表名/字段名/索引名统一 `lower_snake_case`。
- 主键统一 `id`，外键统一 `<entity>_id`。
- SQL 必须位于 `resources/mapper/**/*.xml`。
- Mapper 接口仅保留方法签名，禁止 `@Select/@Update/@Insert/@Delete` 注解内联 SQL。
- 新增/修改 Mapper 必须同步提交 XML 与接口签名并通过启动期映射校验。
- 事务边界应由 `application` 层管理，禁止跨层隐式扩散。
- 行数统计统一使用 `count(*)`，禁止用 `count(列名)` 或 `count(常量)` 代替。
- 使用 `count(distinct col)` 时必须明确其只统计非 NULL 不重复值；多列 `count(distinct col1, col2)` 中任一参与列为 NULL 的行不计入统计，如果其中一列全为 NULL，即使另一列存在不同值也返回 `0`。
- 聚合函数必须处理 NULL 结果：`count(col)` 在列全 NULL 时返回 `0`，`sum(col)` 在列全 NULL 时返回 `NULL`；业务读取 `sum` 结果必须使用 `IFNULL(SUM(column), 0)` 或等价兜底，避免 NPE。
- NULL 判断统一使用 `ISNULL(column)` / `NOT ISNULL(column)`，禁止使用 `= NULL`、`<> NULL` 或依赖 NULL 与普通值直接比较的结果。
- 分页查询必须先执行 count；当 count 为 `0` 时直接返回空分页结果，禁止继续执行分页明细查询。
- 禁止使用数据库外键与级联更新/删除；外键关系、级联语义、约束校验必须在应用层或领域规则中解决。
- 禁止使用存储过程承载业务逻辑，避免调试、扩展、迁移和审计困难。
- 数据订正、删除或批量修改前必须先 `select` 确认命中范围，确认无误后才能执行 `update/delete`。
- 多表查询、更新、删除中涉及的所有列必须加表别名或表名限定，禁止裸列名。

### 8.2 SQL 写法建议（SHOULD）

- SQL 表别名建议使用 `as t1`、`as t2`、`as t3` 顺序命名，提升多表 SQL 可读性与审查效率。
- `in` 操作能避免则避免；确需使用时必须评估集合规模，原则上控制在 `1000` 个元素以内。
- 涉及字符长度判断时必须区分字节数与字符数：`LENGTH` 返回字节长度，`CHARACTER_LENGTH` 返回字符数量；需要存储表情时使用 `utf8mb4`。
- 开发代码中不建议使用 `TRUNCATE TABLE`；它速度快但无事务且不触发 trigger，误用风险高。清理数据必须按任务给出的审批、备份和回滚要求执行。

### 8.3 ORM / MyBatis 映射约束（MUST）

- 查询字段必须显式列出，禁止 `select *`。
- POJO 布尔属性禁止以 `is` 开头；数据库布尔字段必须使用 `is_` 前缀，并在 `resultMap` 中显式映射字段与属性。
- 禁止使用 `resultClass` 作为返回映射；每个表必须有对应 `<resultMap>`，即使字段名与属性名完全一致也必须显式定义。
- SQL XML 参数绑定统一使用 `#{}`，禁止使用 `${}` 拼接用户输入或业务参数，避免 SQL 注入。
- 禁止使用 iBATIS `queryForList(String statementName, int start, int size)` 做分页；分页参数必须下推到 SQL，例如通过 `start`、`size` 参数传入 Mapper。
- 查询结果禁止直接输出为 `HashMap` 或 `Hashtable`；必须定义明确 DO/DTO 与 `<resultMap>`，避免数据库版本或驱动差异导致类型不一致。
- 更新数据表记录时，必须同步更新该记录的 `update_time` 为当前时间。

### 8.4 ORM / MyBatis 写法建议（SHOULD）

- 不要设计“大而全”的更新接口。更新 SQL 只允许写入本次业务真正需要变更的字段，避免误覆盖、降低执行成本并减少 binlog 膨胀。
- `@Transactional` 不得滥用。启用事务前必须确认数据库 QPS 影响、事务边界、回滚范围，以及缓存、搜索引擎、消息、统计数据等外部副作用的补偿方案。
- 维护历史 iBATIS 动态 SQL 时，必须准确区分条件标签语义：`<isEqual>` 的 `compareValue` 是与属性值比较的常量，`<isNotEmpty>` 表示非空字符串且非 NULL，`<isNotNull>` 仅表示非 NULL。

## 9. 分布式运行规则（摘要）

- 外部调用必须有超时、重试上限、幂等前提与退避策略。
- 分布式锁必须具备命名空间、超时与持有者校验释放。
- 跨服务一致性必须给出可恢复路径（Outbox/Saga/TCC/补偿）。
- 缓存必须可降级，且处理穿透、击穿、雪崩。
- 消息处理必须幂等，失败必须可补偿、可追踪、可重放。
- 停机前必须冲刷在途任务、队列与异步缓冲。

完整条款见第 14 章《通用分布式编码契约》。

## 10. 调度与异步任务规范

- 定时任务统一使用 XXL-Job。
- Job Handler 统一放在 `bootstrap.job` 包。
- Handler 命名建议：`{app}:{domain}:{action}`。
- 任务必须满足幂等、可重试、可观测（开始/结束/耗时/结果）。
- 任务中禁止直接堆叠复杂业务细节，统一调用 application 层接口。

## 11. 日志、可观测与追踪规范

- 日志、指标、链路追踪必须同时具备。
- 关键字段统一：`traceId`、`bizId`、`operatorId`、`resultCode`、`costMs`。
- HTTP -> Dubbo -> MQ 全链路必须透传追踪上下文。
- 异步边界必须正确传递并清理 `MDC/ThreadLocal`，防止上下文污染。
- 禁止循环刷屏日志、敏感信息明文输出、无上下文错误日志。

## 12. 配置与安全规范

- 配置必须集中治理并做环境隔离。
- 关键配置变更必须可审计、可回滚。
- 对外接口必须具备鉴权、限流、输入校验、输出脱敏。
- 密钥必须托管，不得硬编码。
- 禁止依赖前端透传关键身份字段进行授权判断。

## 13. 质量门禁与交付要求

统一门禁命令：

```bash
mvn verify
```

建议仓内规则校验：

```bash
rg -n "@Select\\(|@Update\\(|@Insert\\(|@Delete\\(" src/main/java
rg -n "org\\.slf4j|lombok\\.extern\\.slf4j|@Slf4j|logback" pom.xml src/main/java
```

交付前必须确认：

- 构建、测试与静态检查通过。
- 变更范围、回滚方案、验收口径已在任务文档中落地。
- 涉及分布式改动时，已逐条对照第 14 章并形成自检记录。

## 14. 通用分布式编码契约（核心章节）

当任务触及外部调用、并发控制、异步处理、缓存、消息、事务、发布与停机流程时，本章条款触发即强制执行。

### 14.1 资源隔离与并发治理

- MUST
  - 不同业务优先级必须资源隔离（线程池/协程池/Worker 池）。
  - 并发参数必须可配置并支持运行时生效。
  - 执行资源必须使用业务语义化命名。
  - 拒绝策略必须按优先级分层定义。
- SHOULD
  - 采用高/中/低优先级分池并独立监控。
  - 提供租户或业务维度快速失败开关。
- MUST NOT
  - 禁止全业务共享一个资源池。
  - 禁止无界队列直接上线。
  - 禁止高峰期把拒绝全部回落调用线程造成级联阻塞。
- 验收标准
  - 活跃度、排队长度、拒绝次数可实时观测。
  - 单业务过载不影响其他业务 SLA。

### 14.2 超时、重试与幂等

- MUST
  - 所有外部调用必须设置超时。
  - 重试必须满足幂等前提、次数上限、退避抖动。
  - 写操作必须具备幂等键（请求号/业务主键/消息号）。
  - 必须区分可重试与不可重试错误。
- SHOULD
  - 默认重试不超过 3 次。
  - 总重试窗口受端到端超时预算约束。
- MUST NOT
  - 禁止无限等待调用。
  - 禁止无限重试或固定间隔硬重试。
  - 禁止无幂等保护的重复写入。
- 验收标准
  - 每个接口能说明超时值、重试策略、幂等键。
  - 故障时不会因重试放大下游压力。

### 14.3 分布式锁与并发一致性

- MUST
  - 锁 key 必须带命名空间。
  - 加锁必须同时设置等待时间和租约时间。
  - 解锁必须在 `finally` 中并校验当前持有者。
  - 锁获取失败必须返回明确错误码或状态。
- SHOULD
  - 优先细粒度锁。
  - 优先乐观锁/CAS，锁仅用于必要临界区。
- MUST NOT
  - 禁止无超时阻塞锁。
  - 禁止未校验持有者直接解锁。
  - 禁止大范围锁覆盖整条链路。
- 验收标准
  - 锁等待时长、超时次数、冲突率可观测。
  - 并发回放下无重复执行和脏覆盖。

### 14.4 事务与最终一致性

- MUST
  - 本地事务必须显式声明回滚范围。
  - 事务边界必须最小化。
  - 跨服务一致性必须有可恢复方案（Outbox/Saga/TCC/补偿任务）。
  - 必须定义补偿触发条件、终止条件、人工接管路径。
- SHOULD
  - 显式指定事务传播行为。
  - 关键状态变更使用版本号或状态机校验。
- MUST NOT
  - 禁止长事务中夹带 RPC。
  - 禁止跨服务写入无补偿路径。
  - 禁止状态机缺失导致非法状态跳转。
- 验收标准
  - 任意失败点都能给出恢复路径。
  - 演练可证明最终一致性可达。

### 14.5 缓存治理

- MUST
  - 缓存必须设置 TTL。
  - 必须明确序列化协议和兼容策略。
  - 必须处理缓存穿透（含空值缓存）。
  - 缓存故障必须有降级方案。
- SHOULD
  - TTL 增加随机抖动。
  - 热点数据采用本地 + 远程两级缓存。
- MUST NOT
  - 禁止永久缓存业务数据。
  - 禁止超大对象直接缓存且无分片/压缩。
  - 禁止缓存不可用时把全部流量直接压到数据库。
- 验收标准
  - 命中率、回源率、穿透率有指标。
  - 缓存故障时系统可降级运行。

### 14.6 消息与事件处理

- MUST
  - 消息必须携带 `traceId`、`messageId`、业务键。
  - 消费端必须幂等。
  - 发送失败必须进入可补偿通道（重试/失败表/死信）。
  - 消息契约必须版本化管理。
- SHOULD
  - 超过重试阈值自动进死信并报警。
  - 高吞吐场景采用批量消费与批量提交。
- MUST NOT
  - 禁止只保证“发出成功”不保证“消费一致”。
  - 禁止无版本号的消息结构变更。
  - 禁止失败消息静默丢弃。
- 验收标准
  - 可按 `messageId` 追踪生产、消费、补偿全生命周期。
  - 重复投递不产生重复副作用。

### 14.7 批量处理与异步落盘

- MUST
  - 高频写入必须支持“异步入队 + 批量提交”。
  - 缓冲队列必须有界并有溢出处理。
  - 必须有“阈值触发 + 定时触发”双刷盘机制。
  - 停机前必须冲刷剩余数据。
- SHOULD
  - 批量大小以压测结果确定。
  - 按分片键分组提交提升局部性。
- MUST NOT
  - 禁止逐条循环写库。
  - 禁止无界队列。
  - 禁止只靠单一触发条件导致数据滞留。
- 验收标准
  - 入队延迟、批量大小、刷盘耗时可观测。
  - 异常重启后无系统性数据丢失。

### 14.8 容错、降级与补偿

- MUST
  - 外部依赖失败必须进入既定策略（重试/降级/熔断/补偿）。
  - 失败任务必须可追踪、可重放、可终止。
  - 告警必须限流去重。
  - 必须提供人工接管入口。
- SHOULD
  - 关键依赖接入熔断与隔离舱。
  - 对网络抖动、超时、部分成功分别制定策略。
- MUST NOT
  - 禁止 catch 后仅打印日志。
  - 禁止失败任务无状态机。
  - 禁止无去重告警风暴。
- 验收标准
  - 每类故障都有 runbook。
  - 故障演练可量化 MTTR 改善。

### 14.9 可观测性与上下文传递

- MUST
  - 日志、指标、链路追踪三件套齐备。
  - 日志必须包含关键业务上下文。
  - 核心链路必须具备延迟、吞吐、错误率指标。
  - 异步边界必须透传并清理上下文（`MDC`/`ThreadLocal`）。
- SHOULD
  - 建立业务 SLA 与技术指标映射。
  - 关键阶段增加埋点，便于定位性能瓶颈。
- MUST NOT
  - 禁止仅有错误日志而无链路维度。
  - 禁止 `traceId` 在异步边界丢失。
  - 禁止上下文容器不清理导致污染。
- 验收标准
  - 一次 trace 能定位关键失败节点。
  - 指标可按租户/接口/任务类型切片。

### 14.10 配置与安全边界

- MUST
  - 配置集中治理并做环境隔离。
  - 关键配置具备启动校验和变更审计。
  - 身份以服务端可信上下文为准。
  - 对外接口必须有鉴权、限流、输入校验、输出脱敏。
- SHOULD
  - 配置变更支持灰度和回滚。
  - 密钥轮换自动化。
- MUST NOT
  - 禁止硬编码密钥和敏感配置。
  - 禁止测试配置直接用于生产。
  - 禁止依赖前端透传关键身份字段做授权。
- 验收标准
  - 安全扫描无高危硬编码问题。
  - 关键配置变更可追溯到人和时间。

### 14.11 发布、回滚与优雅停机

- MUST
  - 发布必须支持健康检查、灰度放量、快速回滚。
  - 停机前必须停止接收新流量并处理在途任务。
  - 停机流程必须包含队列冲刷与消息确认。
  - 变更必须具备可逆回滚单元。
- SHOULD
  - 发布前执行最小故障注入演练。
  - 关键链路采用金丝雀验证。
- MUST NOT
  - 禁止强杀进程作为常规停机手段。
  - 禁止无回滚预案直接全量发布。
  - 禁止不可逆数据变更与应用发布强耦合上线。
- 验收标准
  - 有标准化发布/回滚清单。
  - 演练可证明停机不造成系统性数据损坏。

## 15. migration 策略

- 默认不将应用内 migration 作为必选交付项。
- 仅当任务明确要求结构变更时，提交 SQL 变更说明与回滚方案。
- 结构变更上线前必须有兼容性与回滚演练记录。

## 16. 与项目契约关系

- 本文件是 Java 项目的工程规范闸门，优先级低于用户显式指令。
- 若项目仓库已有更严格且可执行的本地规范，可在不放松本规范底线的前提下覆盖默认建议。
- 若本规范与项目既有规范冲突，必须在任务 `spec/contract` 中记录冲突、决策与生效范围。
