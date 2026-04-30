# Java 分层与 DDD 规则

本文件适用于类放置、包结构、命名、Lombok、依赖注入、MapStruct、领域建模、转换器和 DDD 分层。

## 1. 适用场景

- 新增或调整 Controller、Provider、Job、Application Service、Domain Service、Repository、Adapter。
- 新增 DTO、Domain Model、Entity、Converter、Mapper、配置类或公共常量。
- 调整包结构、依赖方向、注入方式、参数校验、领域规则或转换逻辑。

## 2. 核心门禁（触发本维度必须满足）

1. **入口只依赖接口**：Controller、Dubbo Provider、Job Handler 只能依赖应用服务接口，禁止注入 `XxxAppServiceImpl`。
2. **应用服务接口成对存在**：`XxxAppService` 必须是 interface，`XxxAppServiceImpl` 必须实现对应接口。
3. **领域层保持纯净**：Domain 禁止依赖 Spring 基础设施、MyBatis、Redis、MQ、HTTP Client、数据库 Entity。
4. **应用层不越过领域边界**：Application 不直接操作 MyBatis Mapper，持久化和外部访问通过 Domain Repository/Adapter 抽象进入。
5. **MapStruct 严格映射**：Mapper 必须使用 `unmappedTargetPolicy = ReportingPolicy.ERROR`，复杂字段显式 `@Mapping`。

## 3. 包职责

- `client` / `api`：公共 API 契约、请求/响应 DTO、共享枚举、Dubbo client service 接口。
- `common`：共享常量、错误码、统一异常、通用工具。
- `domain`：领域模型、领域服务、Repository/Adapter 接口、业务规则和不变量。
- `infrastructure`：Repository 实现、数据库 Entity、MyBatis Mapper、Redis、MQ、HTTP/RPC Adapter、配置适配。
- `application`：用例编排、事务边界、Dubbo Service 实现、应用层 Converter、Filter、应用工具。
- `bootstrap` / `web`：启动装配、REST Controller、Web Filter、Web Config、全局异常处理、Job Handler。

## 4. 依赖方向

允许的方向：

```text
Bootstrap/Web -> Application -> Domain
Bootstrap/Web -> Infrastructure -> Application/Domain
Domain -> Repository/Adapter 接口
Infrastructure -> Domain 接口
```

禁止的方向：

- `domain -> application/infrastructure/bootstrap/web`。
- `application -> bootstrap/web`。
- Domain 依赖 Spring 基础设施、MyBatis 注解、Redis、MQ、HTTP Client 或数据库 Entity。
- Application 直接操作 MyBatis Mapper。
- Web/Controller 绕过 Application Service 直接访问 Domain 或 Infrastructure。
- 跨应用直接读写对方表；跨应用交互使用 API 或消息契约。

## 5. 命名规则

- Dubbo 接口：`{Feature}ClientService`。
- Dubbo 实现：`{Feature}ApplicationServiceImpl`。
- 应用服务：`{Feature}AppService` / `{Feature}AppServiceImpl`。
- 领域服务：`{Feature}Service`。
- Repository 接口：`{Name}Repository`。
- Repository 实现：`{Name}RepositoryImpl`。
- Adapter：`{Provider}{Channel}Adapter`。
- 请求 DTO：`{Action}Request`。
- 响应 DTO：`{Action}Response`。
- 数据库 Entity：`{Name}Entity`。
- MapStruct Converter：`{Name}Converter`。
- MyBatis Mapper：`{Name}Mapper`。
- 配置类：`{Feature}Config`。
- 常量类：`{Domain}Constants`。

方法命名建议：

- Repository 查询：`findBy{Condition}`。
- Repository 保存/更新：`save`、`update`、`update{Field}`。
- 校验并加载：`validateAndGet{Object}`。
- 参数校验：`validParam`。
- 转换：`toEntity`、`toDomain`、`toResponse`。
- 批量转换：`toEntityList`、`toDomainList`、`toResponseList`。
- 构建对象：`build{Object}`。

## 6. Lombok 与注入

- 需要日志的 Service、Controller、Filter、Infrastructure Component 使用 `@Slf4j`。
- DTO、Entity、简单 Domain Model 可在符合本地风格时使用 `@Data`。
- 需要 Builder 构造时，`@Builder` 应配合 `@NoArgsConstructor` 和 `@AllArgsConstructor`。
- 枚举和只读值暴露优先使用 `@Getter`。
- 优先沿用被修改层的既有注入风格。
- 继承 Base Service 的 Application Service 可沿用项目已有 `@Resource` 字段注入。
- Infrastructure Component 在本地风格允许时优先使用构造器注入、`@RequiredArgsConstructor` 和 `final` 字段。
- 同一个类中不要混用多种注入风格。

## 7. MapStruct 与转换器

- 统一使用 `@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.ERROR)`。
- DTO/Domain 转换器放在 `application/converter/`。
- Domain/Entity 转换器放在 `infrastructure/converter/`。
- 方法命名使用 `toEntity`、`toDomain`、`toResponse`。
- 枚举转换使用 `name()` 或稳定 code，禁止使用 `ordinal()`。
- 非平铺字段、枚举、金额、状态、时间等复杂转换必须显式 `@Mapping` 或 `@Named`。
- 新增转换器前先查找并复用已有转换器。
- MapStruct 只做结构映射，业务规则留在 Domain/Application。

## 8. 领域建模与校验

- 业务规则放在 Domain Model 或 Domain Service，不放在 Controller。
- Domain Service 通过 Repository/Adapter 接口访问持久化和外部能力。
- Domain Model 不暴露 Infrastructure Entity。
- 不变量放在拥有该概念的领域对象附近。
- 已有分层能承载职责时，不新增平行 Service 层。
- 应用边界必须做参数校验；Web 注解校验只能补充，不能替代应用层校验。
- 校验失败使用项目统一异常和 `ErrorCode.PARAM_ERROR`。
- 校验消息中的字段名建议使用 `[companyId]` 这类括号格式。

## 9. 示例

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

## 10. 验收与自动检查

- `convention-check` 会拦截入口层依赖 `*AppServiceImpl`。
- `convention-check` 会拦截 `XxxAppService` 被写成 class。
- `convention-check` 会拦截 `XxxAppServiceImpl` 未实现对应接口。
- `convention-check` 会拦截 MapStruct 缺少 `ReportingPolicy.ERROR`。
- 人工验收必须确认 Domain、Application、Infrastructure 依赖方向没有被突破。
