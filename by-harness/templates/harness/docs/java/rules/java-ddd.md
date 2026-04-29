# Java Style, Package Structure, and DDD Rules

Load this file for Java class placement, naming, Lombok, MapStruct, dependency injection, domain modeling, converters, package structure, or DDD layering.

## Package Responsibilities

- `client` / `api`: public API contracts, request/response DTOs, shared enums, Dubbo client service interfaces.
- `common`: shared constants, error codes, unified exceptions, utilities.
- `domain`: domain models, domain services, repository/adapter interfaces, business rules, invariants.
- `infrastructure`: repository implementations, database entities, MyBatis mappers, Redis, MQ, HTTP/RPC adapters, config adapters.
- `application`: use case orchestration, transaction boundaries, Dubbo service implementations, application converters, filters, application utilities.
- `bootstrap` / `web`: startup assembly, REST controllers, web filters, web config, global exception handlers, job handlers.

## Dependency Direction

Allowed:

```text
Bootstrap/Web -> Application -> Domain
Bootstrap/Web -> Infrastructure -> Application/Domain
Domain -> Repository/Adapter interfaces
Infrastructure -> Domain interfaces
```

Forbidden:

- `domain -> application/infrastructure/bootstrap/web`
- `application -> bootstrap/web`
- Domain depending on Spring infrastructure, MyBatis annotations, Redis, MQ, HTTP clients, or database entities.
- Application directly operating MyBatis mappers; use domain repository abstractions.
- Web/Controller bypassing application services.
- Cross-application direct table reads/writes; use API or message contracts.

## Naming Rules

- Dubbo interface: `{Feature}ClientService`.
- Dubbo implementation: `{Feature}ApplicationServiceImpl`.
- Application service: `{Feature}AppService` / `{Feature}AppServiceImpl`.
- Domain service: `{Feature}Service`.
- Repository interface: `{Name}Repository`.
- Repository implementation: `{Name}RepositoryImpl`.
- Adapter: `{Provider}{Channel}Adapter`.
- Request DTO: `{Action}Request`.
- Response DTO: `{Action}Response`.
- Database entity: `{Name}Entity`.
- MapStruct converter: `{Name}Converter`.
- MyBatis mapper: `{Name}Mapper`.
- Config class: `{Feature}Config`.
- Constants class: `{Domain}Constants`.

## Method Naming Rules

- Repository query: `findBy{Condition}`.
- Repository save/update: `save`, `update`, or `update{Field}`.
- Validation and loading: `validateAndGet{Object}`.
- Parameter validation: `validParam`.
- Conversion: `toEntity`, `toDomain`, `toResponse`.
- Batch conversion: `toEntityList`, `toDomainList`, `toResponseList`.
- Builders: `build{Object}`.

## Lombok and Injection

- Use `@Slf4j` for services, controllers, filters, and infrastructure components that log.
- DTOs, entities, and simple domain models may use `@Data` when consistent with existing code.
- Use `@Builder` with `@NoArgsConstructor` and `@AllArgsConstructor` when builder construction is needed.
- Use `@Getter` for enums and read-only value exposure.
- Prefer the injection style already used in the touched layer.
- Application service implementations may follow existing `@Resource` field injection when extending a base service.
- Infrastructure components should prefer constructor injection with `@RequiredArgsConstructor` and `final` fields when it matches local style.
- Do not mix injection styles unnecessarily in a single class.

## MapStruct Rules

- Use `@Mapper(componentModel = "spring", unmappedTargetPolicy = ReportingPolicy.ERROR)`.
- Keep converters in the correct layer:
  - DTO/domain converters in `application/converter/`.
  - domain/entity converters in `infrastructure/converter/`.
- Use `toEntity`, `toDomain`, `toResponse` method names.
- Enum conversion must use `name()`.
- Use `@Mapping` and `@Named` for non-trivial field conversion.
- Reuse existing converters before adding new ones.
- MapStruct only performs structural mapping; business rules stay in domain/application logic.

## Domain Modeling

- Put business rules on domain models or domain services, not controllers.
- Domain services access persistence through repository interfaces.
- Domain models must not expose infrastructure entities.
- Keep invariants close to the domain concept that owns them.
- Do not add new service layers when an existing layer already owns the responsibility.

## Validation

- Prefer application-layer manual validation through existing base service conventions.
- Validation failures use the project exception and `ErrorCode.PARAM_ERROR`.
- Field names in validation messages should use bracket format such as `[companyId]`.
- Web validation annotations may supplement but should not replace required application boundary validation.

## Service Interface Example

Forbidden:

```java
@RestController
public class OrderController {
    @Resource
    private OrderAppServiceImpl orderAppService;
}
```

Recommended:

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
