# Persistence and Infrastructure Rules

Load this file for databases, MyBatis, repositories, Redis, distributed locks, MQ, HTTP clients, adapters, configuration files, config center, XXL-Job, or infrastructure services.

## Repository and Mapper Boundaries

- Domain defines repository and adapter interfaces.
- Infrastructure implements repository interfaces.
- MyBatis mapper access stays inside infrastructure repository implementations.
- Application and domain code must not directly call mappers.
- Convert between entity and domain model in infrastructure converters.
- Do not leak database entities outside infrastructure boundaries.

## Database Design Rules

- Table, field, and index names use `lower_snake_case`.
- Tables include primary key `id`.
- Foreign-key-like fields use `<entity>_id`.
- Tables include `create_time` and `update_time`.
- Soft-delete tables include `is_deleted`, where `0` means active and `1` means deleted.
- Monetary fields use `DECIMAL(18,3)`.
- Time fields use `DATETIME`.
- Use `utf8mb4` with `utf8mb4_unicode_ci` unless existing project configuration differs.
- Do not use database foreign keys or cascading updates/deletes; enforce relationship semantics in application/domain logic.
- Do not use stored procedures for business logic.

## MyBatis and SQL Rules

- SQL must be in `resources/mapper/**/*.xml`.
- Mapper interfaces keep method signatures only; `@Select/@Update/@Insert/@Delete` inline SQL is forbidden.
- Query columns must be explicit; `select *` is forbidden.
- XML parameter binding uses `#{}`; `${}` is forbidden for user or business parameters.
- Use explicit `<resultMap>` for every table; `resultClass` is forbidden.
- POJO boolean properties must not start with `is`; database boolean fields use `is_` prefix and explicit `resultMap`.
- Query results must not directly output `HashMap` or `Hashtable`; define DO/DTO and `<resultMap>`.
- Row count uses `count(*)`; do not use `count(column)` or `count(constant)` for row counts.
- `sum(column)` can return NULL; business SQL should use `IFNULL(SUM(column), 0)` or equivalent.
- NULL checks use `ISNULL(column)` / `NOT ISNULL(column)` per project convention.
- Multi-table query/update/delete columns must use table aliases or table names.
- Paginated query must run count first; if count is `0`, return empty page without querying details.
- PageHelper pagination must have stable ordering, such as `id desc` or `created_time desc`.
- Updates must maintain `update_time`.
- Data correction, delete, or batch update must first `select` the hit range, then execute with rollback plan.

## SQL Writing Guidance

- SQL aliases should use `as t1`, `as t2`, `as t3` in multi-table statements.
- Avoid `in` when possible; when required, evaluate collection size and keep it around 1000 or less.
- Distinguish `LENGTH` bytes from `CHARACTER_LENGTH` characters.
- Avoid `TRUNCATE TABLE` in application code; it is non-transactional and high risk.
- Avoid broad transactions around large or complex operations.
- Do not design overly broad update APIs; update only fields required by the current business action.
- Use `@Transactional` only after confirming QPS impact, transaction boundary, rollback scope, and external side-effect compensation.

## Redis Key Rules

- Follow the existing key namespace convention.
- Default pattern: `{service}:{feature}:{companyId}:{channelType}`.
- Lock pattern: `{service}:lock:{feature}:{identifier}`.
- Do not introduce unscoped keys that can collide across tenants, services, or environments.
- Business cache writes must set TTL.
- Cache design must define invalidation and downgrade behavior.

Forbidden:

```java
redisTemplate.opsForValue().set("orderCache", value);
```

Recommended:

```java
String key = "order:detail:" + orderId;
redisTemplate.opsForValue().set(key, value, 10, TimeUnit.MINUTES);
```

## Distributed Lock Rules

- Locks must have expiration times.
- Lock values must be unique, usually from the existing `UUIDUtil`.
- Release locks in `finally`.
- Release locks through the existing safe `releaseLock(key, value)` pattern that checks value before deleting.
- Do not release locks with a raw delete operation.

## MQ Rules

- Reuse existing producer base classes and MQ configuration.
- Topics and tags should come from configuration rather than hardcoded values.
- Producers should follow the project initialization order convention, including `@DependsOn` where required.
- JSON payload construction should follow existing project style.
- Include business identifiers in MQ logs without exposing sensitive values.
- Messages must carry `traceId`, `messageId`, and a business key when they cross service boundaries.

## Async and Thread Pool Rules

- Configure async executors centrally, normally in `AsyncConfig`.
- Apply `MdcTaskDecorator` or existing context propagation to preserve TraceId/MDC.
- Use bounded queues and explicit rejection policies.
- Preserve graceful shutdown behavior.
- Bind executor metrics when the project already uses Micrometer monitoring.

## XXL-Job Rules

- Scheduled tasks use XXL-Job.
- Job Handler belongs in `bootstrap.job`.
- Handler naming should follow `{app}:{domain}:{action}`.
- Jobs must be idempotent, retryable, observable, and log start/end/cost/result.
- Handler should call application layer interfaces, not embed complex business details.

## Configuration Rules

- Shared application configuration belongs in `application.yml`.
- Environment-specific configuration belongs in `application-{profile}.yml`.
- New config keys should use `{service}.{module}.{key}`.
- Use `@Value("${key:default}")` only when the default is intentional and safe.
- Critical config changes must be auditable and rollbackable.
- Secrets must be stored encrypted or in the approved config center.
- Do not hardcode secrets in source code, tests, logs, or docs examples.

## Infrastructure Error Rules

- Convert technical failures to project exceptions when returning to business/application layers.
- Preserve exception cause when wrapping.
- ERROR logs must include stack traces.
- Do not expose raw third-party error details to external API callers unless explicitly safe and required.
