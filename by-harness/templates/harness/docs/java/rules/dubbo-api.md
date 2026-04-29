# Dubbo, ApiResponse, and Public API Rules

Load this file for Dubbo interfaces, Dubbo service implementations, public DTOs, `ApiResponse`, client/api modules, external API packages, or RPC filters.

## Public Contract Rules

- All public client/api service methods return `ApiResponse<T>`.
- Request DTOs live under `client/request/` or `api/request/`.
- Response DTOs live under `client/response/` or `api/response/`.
- Shared public enums live under `client/enums/` or `api/enums/`.
- Public DTOs implement `Serializable`.
- Public DTOs declare `private static final long serialVersionUID = 1L;`.
- Use enums for stable business categories instead of string constants.
- Serialize enum values with `name()`, never `ordinal()`.
- Do not expose domain models, database entities, DOs, or infrastructure internals through public APIs.
- Public API changes must be intentional and compatible, or explicitly requested.

## ApiResponse Rules

- Use the existing `ApiResponse<T>` wrapper for public boundaries.
- Success uses `ApiResponse.success(...)`.
- Failure uses `ApiResponse.error(code, message)` or the existing project variant.
- Success is determined by `code == 200` or the existing `isSuccess()` implementation.
- Do not introduce a competing response wrapper.
- Do not return raw system exception messages in `ApiResponse.error(...)`.

## Dubbo Interface Rules

- Dubbo interfaces belong in the `client/service/` or `api/service/` package.
- Interface names follow `{Business}ClientService`.
- Method names must describe business intent, not transport implementation.
- Public DTO fields must remain backward compatible unless the task explicitly allows breaking change.
- Versioned or external-facing contracts should include compatibility notes in spec/contract.

## Dubbo Implementation Rules

- Dubbo service implementations belong in the `application` module.
- Implementation names follow `{Business}ApplicationServiceImpl`.
- Implementations should extend the existing `BaseApplicationService` when the project uses it.
- Add `@Component` for local Spring usage.
- Add `@DubboService` for RPC exposure.
- Core non-idempotent business services must use `retries = 0`, or explain existing project strategy.
- Application services orchestrate domain services and repositories through domain abstractions.

## Dubbo Filter Rules

For request/response logging filters:

- Generate or reuse TraceId before invocation.
- Log sanitized arguments only.
- Log sanitized/truncated results.
- Log duration.
- Clear TraceId in `finally`.
- ERROR logs must include stack traces.

For exception filters:

- Convert project business exceptions to `ApiResponse.error(...)`.
- Do not swallow non-business system exceptions.
- Preserve RPC semantics for `RpcException`.
- Use the existing Dubbo async result construction pattern already used by the project.

## Client/API Package POM Rules

- Keep dependencies minimal and optional where appropriate.
- Avoid leaking server-only dependencies into the client/api artifact.
- Keep Java source/target compatibility aligned with the project specification.
- Publish source jars when the existing release process expects them.

## Example

Forbidden:

```java
public interface OrderClientService {
    OrderEntity query(QueryOrderRequest request);
}

public enum OrderType {
    NORMAL;

    public int code() {
        return ordinal();
    }
}
```

Recommended:

```java
public interface OrderClientService {
    ApiResponse<OrderQueryResponse> query(QueryOrderRequest request);
}

public class OrderQueryResponse implements Serializable {
    private static final long serialVersionUID = 1L;

    private String orderNo;
}

public enum OrderType {
    NORMAL;

    public String code() {
        return name();
    }
}
```

## Review Checklist

- DTOs are serializable and have `serialVersionUID`.
- API methods return `ApiResponse<T>`.
- No entity/domain/internal infrastructure type leaks into the public contract.
- Exceptions are converted at the correct boundary.
- Logs are sanitized and TraceId-safe.
- Compatibility impact is documented.
