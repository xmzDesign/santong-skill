# Distributed Java Gate

Load this file when a Java task touches external calls, concurrency control, async processing, cache, MQ, transactions, consistency, release, or shutdown behavior.

Every Java change must declare Distributed Java Gate in spec/contract/build/qa:

- `未触发` with a concrete reason; or
- `触发` with the clauses below, implementation evidence, verification method, and manual confirmation items.

## 14.1 资源隔离与并发治理

MUST:

- Different business priorities use isolated execution resources: thread pools, queues, worker pools.
- Concurrency parameters are configurable and can take effect at runtime when the project supports it.
- Execution resources use business-semantic names.
- Rejection policies are defined by priority.

MUST NOT:

- Do not share one resource pool across all business workloads.
- Do not ship unbounded queues.
- Do not fallback all rejections to caller threads during peak periods and cause cascading blockage.

Acceptance:

- Active count, queue length, and rejection count are observable.
- One overloaded business area does not break unrelated SLA.

## 14.2 超时、重试与幂等

MUST:

- Every external call has a timeout.
- Retry has idempotency premise, attempt limit, backoff, and jitter.
- Write operations have an idempotency key: request number, business key, or message ID.
- Retriable and non-retriable errors are classified.

SHOULD:

- Default retries do not exceed 3.
- Total retry window fits the end-to-end timeout budget.

MUST NOT:

- No infinite waits.
- No infinite or fixed-interval hard retries.
- No repeated writes without idempotency protection.

Acceptance:

- Each interface can state timeout, retry strategy, and idempotency key.
- Failure does not amplify downstream pressure through retry storms.

## 14.3 分布式锁与并发一致性

MUST:

- Lock keys have namespaces.
- Lock acquisition has wait time and lease time.
- Unlock runs in `finally` and verifies current owner.
- Lock acquisition failure returns a clear error code or state.

SHOULD:

- Prefer fine-grained locks.
- Prefer optimistic lock/CAS; use distributed locks only for necessary critical sections.

MUST NOT:

- No blocking lock without timeout.
- No unlock without owner check.
- No large lock covering the whole chain.

Acceptance:

- Lock wait duration, timeout count, and conflict rate are observable.
- Concurrent replay causes no duplicate execution or dirty overwrite.

## 14.4 事务与最终一致性

MUST:

- Local transactions explicitly define rollback scope.
- Transaction boundaries are minimized.
- Cross-service consistency has a recovery design: Outbox, Saga, TCC, or compensation task.
- Compensation trigger, terminal condition, and manual takeover path are defined.

SHOULD:

- Specify transaction propagation behavior.
- Key state changes use version numbers or state-machine checks.

MUST NOT:

- No RPC/MQ/external calls inside long transactions.
- No cross-service writes without compensation path.
- No illegal state transition caused by missing state machine.

Acceptance:

- Any failure point has a recovery path.
- Rehearsal can prove eventual consistency is reachable.

## 14.5 缓存治理

MUST:

- Cache has TTL.
- Serialization protocol and compatibility strategy are defined.
- Cache penetration is handled, including empty-value caching.
- Cache failure has downgrade behavior.

SHOULD:

- TTL includes random jitter.
- Hot data may use local + remote two-level cache.

MUST NOT:

- No permanent business-data cache.
- No huge cached objects without sharding/compression.
- No direct full traffic fallback to DB when cache is unavailable.

Acceptance:

- Hit rate, fallback-to-origin rate, and penetration rate are measurable.
- System can degrade when cache fails.

## 14.6 消息与事件处理

MUST:

- Messages carry `traceId`, `messageId`, and business key.
- Consumers are idempotent.
- Send failure enters a compensation channel: retry, failure table, or dead letter.
- Message contracts are versioned.

SHOULD:

- Exceeding retry threshold enters dead letter and alerts.
- High-throughput scenarios use batch consume and batch commit.

MUST NOT:

- Do not only guarantee “sent successfully” while ignoring consumption consistency.
- Do not change message structures without versioning.
- Do not silently drop failed messages.

Acceptance:

- The full production, consumption, and compensation lifecycle is traceable by `messageId`.
- Duplicate delivery causes no duplicate side effects.

## 14.7 批量处理与异步落盘

MUST:

- High-frequency writes support async enqueue + batch commit.
- Buffer queues are bounded and have overflow handling.
- Flush supports both threshold trigger and timed trigger.
- Shutdown flushes remaining data.

SHOULD:

- Batch size is based on pressure-test results.
- Commit grouping follows sharding/locality keys when useful.

MUST NOT:

- No row-by-row loop writes for high-frequency paths.
- No unbounded queues.
- No single trigger condition that can leave data stuck.

Acceptance:

- Enqueue latency, batch size, and flush cost are observable.
- Abnormal restart causes no systemic data loss.

## 14.8 容错、降级与补偿

MUST:

- External dependency failures enter a defined strategy: retry, downgrade, circuit break, or compensation.
- Failed tasks are traceable, replayable, and terminable.
- Alerts are rate-limited and deduplicated.
- Manual takeover entry is provided.

SHOULD:

- Key dependencies use circuit breakers and isolation.
- Network jitter, timeout, and partial success have separate strategies.

MUST NOT:

- No catch block that only logs and continues.
- No failed task without a state machine.
- No alert storm without deduplication.

Acceptance:

- Each fault category has a runbook.
- Drill can measure MTTR improvement.

## 14.9 可观测性与上下文传递

MUST:

- Logs, metrics, and tracing are all present.
- Logs include key business context.
- Core links have latency, throughput, and error-rate metrics.
- Async boundaries propagate and clear context: `MDC` / `ThreadLocal`.

SHOULD:

- Map business SLA to technical metrics.
- Add phase metrics for performance diagnosis.

MUST NOT:

- No error-only logs without trace dimension.
- No traceId loss at async boundaries.
- No uncleared context holder causing contamination.

Acceptance:

- One trace can locate the key failure node.
- Metrics can slice by tenant, interface, or task type when cardinality is controlled.

## 14.10 配置与安全边界

MUST:

- Configuration is centralized and environment-separated.
- Critical configs have startup validation and change audit.
- Identity comes from trusted server context.
- External interfaces have auth, rate limit, input validation, and output masking.

SHOULD:

- Config changes support grayscale and rollback.
- Secret rotation is automated when platform supports it.

MUST NOT:

- No hardcoded secrets or sensitive config.
- No test config used directly in production.
- No authorization based on frontend-transmitted critical identity fields.

Acceptance:

- Security scan has no high-risk hardcoded secret.
- Critical config changes are traceable to person and time.

## 14.11 发布、回滚与优雅停机

MUST:

- Release supports health checks, grayscale rollout, and quick rollback.
- Shutdown stops accepting new traffic and handles in-flight tasks.
- Shutdown includes queue flush and message acknowledgement.
- Changes have reversible rollback units.

SHOULD:

- Minimal failure-injection drill before release for key links.
- Canary validation for critical paths.

MUST NOT:

- No forced process kill as regular shutdown.
- No full rollout without rollback plan.
- No tightly coupled irreversible data change and app release.

Acceptance:

- Standard release/rollback checklist exists.
- Drill proves shutdown does not cause systemic data corruption.
