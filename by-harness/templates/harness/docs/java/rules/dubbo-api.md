# Dubbo 与公共 API 规则

本文件适用于 Dubbo 接口、Dubbo 实现、公共 DTO、`ApiResponse<T>`、client/api 模块、外部 API 包和 RPC Filter。

## 1. 适用场景

- 新增或修改 Dubbo client/api 接口、HTTP 公共 API、公共 DTO、公共枚举。
- 调整 RPC Filter、异常转换、统一响应、client/api POM 或对外兼容策略。
- 对外暴露新的查询、写入、回调、消息消费结果或状态值。

## 2. 核心门禁（触发本维度必须满足）

1. **统一响应包装**：公共 client/api service 方法必须返回 `ApiResponse<T>`，禁止新增并行响应包装。
2. **DTO 可序列化**：公共 DTO 必须实现 `Serializable`，并声明 `private static final long serialVersionUID = 1L;`。
3. **公共枚举稳定**：外部可见枚举使用 `name()` 或显式稳定 code，禁止使用 `ordinal()`。
4. **不泄露内部模型**：公共 API 禁止暴露 Domain、Entity、DO、Mapper、Infrastructure 内部类型。
5. **写接口重试明确**：核心非幂等写接口必须明确 `retries = 0`，或记录项目既有重试与幂等策略。

## 3. 公共契约规则

- 请求 DTO 放在 `client/request/` 或 `api/request/`。
- 响应 DTO 放在 `client/response/` 或 `api/response/`。
- 共享公共枚举放在 `client/enums/` 或 `api/enums/`。
- 稳定业务分类优先使用枚举，不用散落字符串常量。
- 公共字段新增要保持向后兼容；删除、改名、改类型属于破坏性变更，必须由任务明确要求。
- 版本化或外部可见契约需要在 spec/contract 中记录兼容性说明。

## 4. `ApiResponse<T>` 规则

- 成功响应使用 `ApiResponse.success(...)` 或项目既有成功工厂方法。
- 失败响应使用 `ApiResponse.error(code, message)` 或项目既有失败工厂方法。
- 成功判断沿用项目实现，例如 `code == 200` 或 `isSuccess()`。
- 外部错误消息必须安全、稳定、可读。
- 禁止在 `ApiResponse.error(...)` 中返回原始系统异常、SQL、堆栈或第三方原始错误。

## 5. Dubbo 接口规则

- Dubbo 接口放在 `client/service/` 或 `api/service/`。
- 接口命名使用 `{Business}ClientService`。
- 方法名表达业务意图，不暴露传输层细节。
- 入参和出参必须是公共 DTO 或基础类型。
- Public DTO 字段需要中文注释，说明含义、单位、取值范围或兼容要求。

## 6. Dubbo 实现规则

- Dubbo 实现放在 `application` 模块。
- 实现命名使用 `{Business}ApplicationServiceImpl`。
- 项目存在 `BaseApplicationService` 时，按既有约定继承。
- 本地 Spring 使用需要 `@Component`。
- RPC 暴露需要 `@DubboService`。
- Dubbo 实现只做参数校验、应用编排、异常转换和响应包装，核心规则下沉到 Domain/Application Service。

## 7. Dubbo Filter 规则

请求/响应日志 Filter：

- 调用前生成或复用 TraceId。
- 只记录脱敏后的参数。
- 只记录脱敏、截断后的结果。
- 记录耗时。
- 在 `finally` 中清理 TraceId/MDC。
- ERROR 日志必须带异常堆栈。

异常 Filter：

- 项目业务异常转换为 `ApiResponse.error(...)`。
- 非业务系统异常不要被静默吞掉。
- 保留 `RpcException` 的 RPC 语义。
- 异步结果构造沿用项目既有 Dubbo 写法。

## 8. Client/API POM 规则

- 依赖保持最小化，必要时使用 optional。
- 禁止把服务端专用依赖泄漏到 client/api artifact。
- Java source/target 与项目规范保持一致。
- 若项目发布流程要求 source jar，必须保留发布配置。

## 9. 示例

禁止：

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

推荐：

```java
public interface OrderClientService {
    ApiResponse<OrderQueryResponse> query(QueryOrderRequest request);
}

public class OrderQueryResponse implements Serializable {
    private static final long serialVersionUID = 1L;

    /** 订单编号。 */
    private String orderNo;
}

public enum OrderType {
    NORMAL;

    public String code() {
        return name();
    }
}
```

## 10. 验收与自动检查

- `convention-check` 会拦截 Public DTO 未实现 `Serializable` 或缺少 `serialVersionUID`。
- `convention-check` 会拦截公共 API 方法未返回 `ApiResponse<T>`。
- `convention-check` 会拦截外部可见枚举使用 `ordinal()`。
- 人工验收必须确认没有内部模型泄露到公共契约。
- 人工验收必须确认兼容性、重试、幂等和异常转换已写入 contract。
