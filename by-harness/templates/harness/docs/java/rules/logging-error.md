# Logging, TraceId, and Error Handling Rules

Load this file for logs, TraceId, MDC, filters, exception conversion, global exception handling, error codes, or response error behavior.

## Logging Framework

- Follow the project Log4j2 baseline.
- Use Lombok `@Slf4j` for classes that log.
- Do not introduce `logback` dependencies or APIs.
- Keep log messages searchable and structured with stable prefixes.
- Include useful business identifiers such as `companyId`, `bizId`, `messageId`, and `channelType` when available.
- Include response duration as `Duration: {}ms` or `costMs` for request/response boundary logs.

## TraceId and MDC

- Generate TraceId at every Web and Dubbo request entry.
- Reuse an existing TraceId if one already exists.
- Clear TraceId in a `finally` block after the request completes.
- Propagate MDC into async threads through `MdcTaskDecorator` or the existing context propagation mechanism.
- Do not start async work that loses TraceId/MDC context.
- HTTP -> Dubbo -> MQ chains must propagate tracing context.

## Log Safety

Always sanitize sensitive data before logging request arguments, response payloads, headers, configuration, or exceptions that may include external values.

Sensitive field names include:

- `authInfo`
- `password`
- `secret`
- `apiSecret`
- `appSecret`
- `clientSecret`
- `token`
- `accessToken`
- `refreshToken`
- `authorization`
- `signature`
- `apiKey`
- `x-api-key`
- `privateKey`
- `sk`
- `skey`
- `ak`
- `appKey`

Use the existing `LogSanitizer` convention when available. Do not create a second sanitizer unless explicitly required.

## Log Levels

- `INFO`: successful business operations, request/response boundaries, initialization success.
- `WARN`: validation failures, business boundary conditions, recoverable external issues.
- `ERROR`: system failures, unexpected exceptions, external service failures.
- `DEBUG`: detailed internal diagnostics that should not be required in production.

ERROR logs must include exception stack traces, for example `log.error("message", exception)`.

## Stable Log Prefixes

- Web request: `[WEB_REQUEST]`
- Web response: `[WEB_RESPONSE]`
- Web exception: `[WEB_EXCEPTION]`
- Dubbo request: `[DUBBO_REQUEST]`
- Dubbo response: `[DUBBO_RESPONSE]`
- Dubbo exception: `[DUBBO_EXCEPTION]`
- Dubbo exception filter: `[DUBBO_EXCEPTION_FILTER]`

## Exception Model

- Use the single project business exception class from the `common` module.
- Do not create business exception subclasses unless local project rules already require that pattern.
- Use `ErrorCode` to distinguish failure types.
- Add new error codes only in the correct numeric range and with Chinese messages.
- Preserve original exception stacks when converting technical exceptions into project exceptions.

## Layer Strategy

- Domain: throw the project exception for business rule violations.
- Infrastructure: convert technical failures to project exceptions when crossing into business semantics.
- Repository: database runtime failures may propagate unless local repository contract says otherwise.
- Application: catch exceptions and return `ApiResponse.error(...)` at service boundaries.
- Dubbo filter: convert project exceptions to `ApiResponse.error(...)` and let non-business RPC/system failures propagate correctly.
- Web: use `GlobalExceptionHandler` as the HTTP boundary fallback.

## External Error Safety

- Do not return raw system exception messages to external callers.
- Fallback system errors should return a safe generic message.
- Business validation messages may be returned only when intentional and safe.

Forbidden:

```java
log.info("create order request={}", request);
return ApiResponse.error("500", exception.getMessage());
```

Recommended:

```java
log.info("[DUBBO_REQUEST] bizId={}, request={}", orderNo, LogSanitizer.sanitize(request));
log.error("[DUBBO_EXCEPTION] bizId={}", orderNo, exception);
return ApiResponse.error(ErrorCode.SYSTEM_ERROR.getCode(), "系统繁忙，请稍后重试");
```
