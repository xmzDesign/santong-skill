# 日志、TraceId 与异常处理规则

本文件适用于日志、TraceId、MDC、Filter、异常转换、全局异常处理、错误码和外部错误响应。

## 1. 适用场景

- 新增或修改 Web/Dubbo/MQ/异步入口日志。
- 新增异常类型、错误码、全局异常处理、Dubbo 异常 Filter。
- 记录请求、响应、配置、三方调用、失败原因或审计信息。

## 2. 核心门禁（触发本维度必须满足）

1. **TraceId 全链路传递**：Web、Dubbo、MQ、异步入口必须生成或复用 TraceId，并在结束时清理 MDC。
2. **日志默认脱敏**：请求、响应、Header、配置、异常和三方数据入日志前必须脱敏。
3. **ERROR 带堆栈**：系统异常、未知异常、外部依赖异常的 ERROR 日志必须包含异常对象。
4. **外部错误安全**：外部响应禁止暴露原始系统异常、SQL、堆栈、内部类名或第三方原始错误。
5. **异常体系统一**：业务异常使用项目统一异常与错误码，不随意新增平行异常体系。

## 3. 日志框架

- 遵循项目 Log4j2 基线。
- 需要日志的类使用 Lombok `@Slf4j`。
- 禁止新增 `logback` 依赖或直接使用 `logback` API。
- 日志文案保持可检索、结构稳定，优先使用稳定前缀。
- 可用时记录 `companyId`、`bizId`、`messageId`、`channelType` 等业务定位信息。
- 边界日志记录耗时，使用 `Duration: {}ms`、`costMs` 或项目既有字段名。

## 4. TraceId 与 MDC

- 每个 Web 和 Dubbo 请求入口都要生成或复用 TraceId。
- HTTP -> Dubbo -> MQ 链路必须传递追踪上下文。
- 异步线程必须通过 `MdcTaskDecorator` 或项目既有机制传播 MDC。
- 异步任务结束后必须清理 MDC / ThreadLocal，避免上下文污染。
- 禁止启动会丢失 TraceId/MDC 的异步任务。

## 5. 敏感字段

以下字段及其同义字段必须脱敏后再入日志：

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

项目已有 `LogSanitizer` 或等价工具时必须复用。除非任务明确要求，禁止新增第二套脱敏工具。

## 6. 日志级别

- `INFO`：成功业务操作、请求/响应边界、初始化成功。
- `WARN`：参数校验失败、业务边界情况、可恢复外部问题。
- `ERROR`：系统故障、未知异常、外部服务失败。
- `DEBUG`：生产排障不应依赖的详细内部诊断。

预期内的业务校验失败不应记录为 ERROR，避免误触告警。

## 7. 稳定日志前缀

- Web 请求：`[WEB_REQUEST]`
- Web 响应：`[WEB_RESPONSE]`
- Web 异常：`[WEB_EXCEPTION]`
- Dubbo 请求：`[DUBBO_REQUEST]`
- Dubbo 响应：`[DUBBO_RESPONSE]`
- Dubbo 异常：`[DUBBO_EXCEPTION]`
- Dubbo 异常 Filter：`[DUBBO_EXCEPTION_FILTER]`

## 8. 异常模型

- 使用 `common` 模块中的项目统一业务异常。
- 除非本地规则已有该模式，禁止新增业务异常子类体系。
- 使用 `ErrorCode` 区分失败类型。
- 新增错误码必须放在正确范围，并使用中文错误消息。
- 技术异常转换为项目异常时必须保留原始 cause。

分层策略：

- Domain：业务规则违反时抛项目统一业务异常。
- Infrastructure：技术失败跨入业务语义时转换为项目异常。
- Repository：数据库运行时异常可按本地 Repository 契约传播或包装。
- Application：在服务边界将异常转换为 `ApiResponse.error(...)`。
- Dubbo Filter：项目异常转换为 `ApiResponse.error(...)`，非业务 RPC/系统异常按 RPC 语义处理。
- Web：由 `GlobalExceptionHandler` 作为 HTTP 边界兜底。

## 9. 示例

禁止：

```java
log.info("create order request={}", request);
return ApiResponse.error("500", exception.getMessage());
```

推荐：

```java
log.info("[DUBBO_REQUEST] bizId={}, request={}", orderNo, LogSanitizer.sanitize(request));
log.error("[DUBBO_EXCEPTION] bizId={}", orderNo, exception);
return ApiResponse.error(ErrorCode.SYSTEM_ERROR.getCode(), "系统繁忙，请稍后重试");
```

## 10. 验收与自动检查

- `convention-check` 会拦截新增 `logback` 依赖链。
- `convention-check` 会拦截疑似敏感日志或硬编码密钥。
- 人工验收必须确认入口 TraceId、异步上下文传播和 MDC 清理。
- 人工验收必须确认 ERROR 日志包含异常堆栈。
- 人工验收必须确认外部错误响应安全、统一、可预期。
