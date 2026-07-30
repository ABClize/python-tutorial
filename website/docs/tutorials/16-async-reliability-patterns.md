# 异步可靠性

异步并发可以重叠 I/O 等待，却不会自动处理慢响应、临时故障、流量突增和任务取消。真正稳定的异步
程序，需要为等待时间、重试、并发量、积压和资源清理分别建立边界。

<p class="source-note">对应源码：<code>python/backend_interview/async_patterns.py</code>、<code>python/backend_interview/service.py</code>、<code>python/backend_interview/repository.py</code></p>

## 本章内容

- [超时与截止时间](./16-async-reliability-patterns/timeouts-and-deadlines)
- [重试、退避与幂等](./16-async-reliability-patterns/retries-backoff-and-idempotency)
- [并发限制与背压](./16-async-reliability-patterns/concurrency-limits-and-backpressure)
- [Single-flight、竞争请求与任务组](./16-async-reliability-patterns/single-flight-and-task-groups)
- [取消、故障隔离与可观测性](./16-async-reliability-patterns/cancellation-isolation-and-observability)
