# 异步可靠性模式

并发让等待重叠，也会把压力、失败和重试同时放大。可靠性设计的重点不是给每次调用都加 try/except，
而是明确时间预算、并发预算、重试条件、幂等边界和过载时的退让方式。

<p class="source-note">对应源码：<code>python/backend_interview/async_patterns.py</code>、<code>python/backend_interview/service.py</code></p>

## 一次远程调用需要哪些边界

<div class="concept-map">
  <div class="concept-step"><small>时间</small><strong>timeout / deadline</strong></div>
  <span class="concept-arrow">+</span>
  <div class="concept-step"><small>压力</small><strong>并发上限</strong></div>
  <span class="concept-arrow">+</span>
  <div class="concept-step"><small>瞬时失败</small><strong>有限重试</strong></div>
  <span class="concept-arrow">+</span>
  <div class="concept-step"><small>重复副作用</small><strong>幂等</strong></div>
  <span class="concept-arrow">+</span>
  <div class="concept-step"><small>观测</small><strong>指标与日志</strong></div>
</div>

这些策略必须一起设计。只有重试没有并发限制，会在下游故障时制造重试风暴；只有超时没有取消清理，
会让调用方离开后后台工作继续消耗资源。

## timeout 与 deadline

timeout 描述某一步最多等待多久，deadline 描述整个操作必须在什么时刻前完成。多层调用更适合向下
传递剩余 deadline：

```python
async def with_timeout(awaitable, seconds: float):
    async with asyncio.timeout(seconds):
        return await awaitable
```

连接、读取、写入和连接池等待可以有不同阶段超时；最外层还应有总预算。超时后需要确认底层库是否
响应取消、连接是否可复用，以及远端副作用是否可能已经发生。

## 重试只适用于瞬时且安全的失败

示例 `retry_async()` 只捕获配置的异常类型，并使用指数退避：

```python
for attempt in range(attempts):
    try:
        return await operation()
    except retry_for:
        if attempt == attempts - 1:
            raise
        await asyncio.sleep(base_delay * 2**attempt)
```

通常可以重试连接重置、临时 503、部分限流响应；参数错误、权限失败和确定性业务冲突不应重试。

### 为什么需要 jitter

大量客户端在同一时刻失败，如果都按完全相同间隔重试，会再次同时冲击下游。实际退避通常加入随机
jitter，把重试分散到时间窗口。

重试次数不是越多越可靠。总尝试次数会乘上调用链层数；如果网关、服务和 SDK 各重试三次，最底层
可能收到 27 次请求。应明确唯一重试层和总 deadline。

## 幂等决定能否安全重放

读取通常天然幂等，创建订单、扣款和发送消息则可能产生重复副作用。安全重试需要：

- 客户端提供稳定 idempotency key；
- 服务端在原子持久化边界记录 key 与结果；
- 同 key、不同请求体应拒绝或明确定义；
- key 有合理保留周期；
- 返回第一次成功的结果。

“请求超时”只表示客户端没有收到结果，不代表服务端没有完成。没有幂等协议时盲目重试可能重复扣款。

## Semaphore 建立并发预算

`map_bounded()` 为真正执行 worker 的区域加 Semaphore，保证最多 N 个下游调用同时进行。

```python
semaphore = asyncio.Semaphore(limit)


async def run_one(value):
    async with semaphore:
        return await worker(value)
```

limit 应与连接池、下游容量和当前进程副本数一起计算。10 个 Pod 每个允许 100 并发，集群总压力可能
达到 1000。

Semaphore 限制活跃数量，不限制等待队列长度。入口仍需请求上限、有界 Queue 或快速拒绝，防止待办
任务耗尽内存。

## first-success 与竞争请求

`first_success()` 并发启动多个候选操作，返回第一个成功结果，并取消剩余任务。它适合多个等价镜像、
DNS 结果或读取副本，但会放大总流量。

实现必须处理：

- 第一个完成的是失败，仍继续等其他候选；
- 全部失败时保留多个错误；
- 成功后取消并等待其他 Task 清理；
- 空候选立即拒绝；
- 候选操作必须允许重复读取或无副作用。

对同一后端发“hedged request”应在观察到尾延迟问题后谨慎使用，并设置额外请求预算。

## single-flight 防止缓存击穿

缓存过期瞬间，如果 100 个请求都去加载同一个 key，下游会承受 100 次相同工作。Single-flight
让同 key 的并发 miss 只执行一次 factory：

```text
请求 A ─┐
请求 B ─┼─ key lock ── factory 一次 ── 共享结果
请求 C ─┘
```

示例先无锁读取缓存，miss 后获取“每个 key 一把锁”，进入锁后再次检查缓存。这次二次检查不可省略，
因为等待锁期间其他请求可能已经填充值。

还需明确：

- factory 失败是否缓存；
- 空值如何区分“未命中”；
- 过期条目和 key lock 如何清理；
- 多进程或多实例之间是否需要分布式协调；
- TTL 是否加入随机抖动，避免大量 key 同时过期。

## Queue 建立背压

Queue 把生产速度与消费速度解耦，但无界队列只是在把过载推迟为内存问题。

```python
queue: asyncio.Queue[Job | None] = asyncio.Queue(maxsize=100)
```

生产者在满队列上等待，或者根据业务选择拒绝、丢弃、降级。消费者必须在 finally 中调用
`task_done()`；关闭时通过 sentinel 或显式取消让 worker 退出，再等待 `queue.join()`。

生产任务还要考虑至少一次、至多一次或恰好一次的处理语义。进程内 asyncio Queue 无法在崩溃后恢复，
持久任务需要消息队列和幂等消费者。

## 熔断与隔舱

仓库示例实现了并发隔舱，但没有实现完整 circuit breaker。两者解决不同问题：

- bulkhead / 隔舱：限制某类调用占用的并发资源；
- circuit breaker / 熔断：连续失败超过阈值后暂时快速失败，避免持续调用已故障下游；
- rate limit：限制单位时间请求数；
- load shed：过载时主动拒绝低优先级工作。

熔断器需要 closed、open、half-open 状态、时间窗口和试探请求，贸然手写容易产生全局同步和恢复震荡，
应优先使用成熟基础设施并配合指标。

## 取消与清理是可靠性的一部分

任何组合函数都要在返回或失败前处理自己创建的 Task。示例 `first_success()` 在 finally 中取消未完成
Task，并用 `gather(..., return_exceptions=True)` 等待收尾，避免泄漏。

不要把 CancelledError 当普通重试异常。上游取消通常意味着结果已无人需要，应尽快释放连接、锁和
队列占位。

## 可观测性回答“策略是否有效”

至少记录和度量：

- 调用次数、成功率和按异常分类的失败率；
- p50、p95、p99 延迟和超时率；
- 重试次数、首次成功率与重试后成功率；
- 当前并发、Semaphore 等待时间和 Queue 深度；
- 缓存命中、single-flight 合并数量与 factory 失败；
- 取消数量和清理耗时。

日志应携带 request ID、操作名和 attempt，但不要泄露密钥或完整请求体。没有指标时，无法判断重试在
恢复服务还是放大故障。

## 常见误区

### 所有异常都重试

确定性错误不会因为等待而消失，重试只会增加延迟和压力。

### 超时越长成功率越高

过长超时会占用连接和 worker，让排队进一步恶化。超时需要结合容量和用户总预算。

### 有 Semaphore 就不会过载

Semaphore 只限制活跃工作，无界等待任务仍会消耗内存并增加尾延迟。

### 缓存解决所有下游压力

低命中、同时过期、热点 key 和多实例 miss 都可能击穿。缓存必须配合容量、single-flight 和失效策略。

## 面试时怎么表述

> 我会把远程调用放进时间预算和并发预算，只对瞬时且幂等的失败做有限指数退避重试，并加入 jitter。
> Semaphore 控制活跃压力，Queue 建立背压，single-flight 合并同 key 的并发 miss。所有组合函数都
> 负责取消和等待自己创建的 Task，并用延迟、重试、队列深度和缓存命中指标验证策略。
