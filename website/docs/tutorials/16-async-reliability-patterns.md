# 异步可靠性

异步可靠性是指程序遇到慢响应、临时故障、流量突增或任务取消时，仍能及时结束并保持数据正确。
常用做法包括超时、有限重试、并发限制、有界队列、幂等处理和资源清理。

<p class="source-note">对应源码：<code>python/backend_interview/async_patterns.py</code>、<code>python/backend_interview/service.py</code>、<code>python/backend_interview/repository.py</code></p>

## 本章内容

- [超时与截止时间](./16-async-reliability-patterns/timeouts-and-deadlines)：
  限制一次等待和整条调用链的最长时间。
- [重试、退避与幂等](./16-async-reliability-patterns/retries-backoff-and-idempotency)：
  只重试临时错误，并防止重复请求产生重复副作用。
- [并发限制与背压](./16-async-reliability-patterns/concurrency-limits-and-backpressure)：
  限制同时执行和等待处理的任务数量。
- [Single-flight、竞争请求与任务组](./16-async-reliability-patterns/single-flight-and-task-groups)：
  合并重复请求，竞争第一个成功结果，或让一组任务共同成败。
- [取消、故障隔离与可观测性](./16-async-reliability-patterns/cancellation-isolation-and-observability)：
  正确停止任务、缩小故障影响并记录运行指标。
