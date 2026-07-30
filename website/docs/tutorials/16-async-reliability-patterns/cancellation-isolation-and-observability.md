# 取消、故障隔离与可观测性

取消是要求异步 Task 停止执行。故障隔离是把一次失败限制在尽可能小的范围。可观测性是通过日志、
指标和追踪了解程序正在发生什么。

客户端断开、超时、兄弟任务失败和应用关闭都可能触发取消。Task 停止前还要释放资源并等待子任务
收尾。

<!-- 对应源码：python/backend_interview/async_patterns.py、python/backend_interview/service.py、python/backend_interview/main.py -->

## 取消从哪里来

常见来源包括：

- 调用方执行 `task.cancel()`；
- `asyncio.timeout()` 到期；
- TaskGroup 中兄弟任务失败；
- HTTP 客户端断开；
- 应用关闭。

取消是控制流，不是普通业务错误。协程通常应完成清理后继续传播，而不是返回一个看似成功的结果。

## 用 `finally` 释放资源

下面保证任务无论正常结束、失败还是被取消，都会关闭资源：

```python
async def use_resource() -> None:
    resource = await acquire_resource()
    try:
        await perform_operation(resource)
    finally:
        await resource.close()
```

锁、响应流、临时文件和数据库事务都需要类似结构。若清理本身也可能长时间等待，还要为清理过程设置
独立但有限的时间预算。

取消是协作式的：协程在 await 点收到取消。长时间纯 CPU 循环没有 await，就不能及时响应。

## 取消子任务后还要等待

只调用：

```python
task.cancel()
```

只是发出取消请求。任务可能还在执行 `finally`，也可能产生尚未读取的异常。应保留任务引用并等待结束：

```python
task.cancel()
await asyncio.gather(
    task,
    return_exceptions=True,
)
```

仓库的 `first_success()` 正是这样收尾剩余竞争任务。

## 谨慎使用 `asyncio.shield()`

`shield()` 阻止外层等待把取消传播给内部 awaitable，但不会自动管理后台任务：

```python
result = await asyncio.shield(
    commit_operation()
)
```

外层仍可能收到取消，而内部操作继续执行。如果调用者没有保留引用、记录结果并负责最终收尾，工作就会
变成失去所有者的后台任务。

只有提交阶段确实必须完成，并且程序明确承担其生命周期时才考虑 shield。它不是“防止超时”的快捷方式。

## 故障隔离的三个层次

容量问题需要按作用范围隔离：

```text
单次调用：timeout
单个下游：独立连接池和 Semaphore
不同业务或租户：独立 worker、队列或配额
```

如果商品查询和风控共用全部连接与 Semaphore，风控流量突增可能拖垮商品接口。为不同依赖分配独立
资源池和容量预算，称为舱壁隔离（bulkhead isolation）：像船舱隔板一样，把一个区域的故障限制在局部。

## 熔断器减少无意义调用

下游持续失败时，熔断器可以暂时快速拒绝：

```text
closed
  正常放行并统计结果
      ↓ 失败达到阈值
open
  快速拒绝新调用
      ↓ 冷却结束
half-open
  放少量探测请求
      ↓
成功回到 closed，失败回到 open
```

失败窗口是统计最近一段时间或最近若干次调用；冷却是暂停调用后等待依赖恢复的一段时间；探测请求是
冷却结束后少量放行、用来判断依赖是否恢复的请求。熔断器需要根据业务确定窗口大小、失败阈值、冷却
时间、探测数量以及多个实例怎样保持一致。

当前仓库没有实现熔断器或跨业务舱壁隔离，这些是扩展设计，不应被当作现有功能。

无论是否使用熔断，timeout 与容量上限仍是基础。熔断不能让已经发出的慢调用自动结束。

## 限制器的实际共享范围

`OrderService` 构造时创建批量 Semaphore，但 FastAPI 依赖为每个请求创建新的 Service。因此它主要
限制一次批量请求内部：

```text
请求 A -> Service A -> Semaphore A
请求 B -> Service B -> Semaphore B
```

若目标是限制整个进程，需要把 Semaphore 放在 lifespan 共享状态；若要限制多个实例的总量，还需要
API 网关、共享限流服务或下游自身配额。

进程内缓存、锁和计数器也遵循相同规律。

## 可观测性要回答哪些问题

可靠性机制会改变延迟与流量，必须通过数据验证。常见记录包括：

- 请求总耗时和各下游耗时；
- timeout 发生在哪个下游、哪个阶段；
- 当前剩余 deadline；
- 尝试次数、重试原因和退避时长；
- 当前正在处理的请求或任务数、Semaphore 等待数和等待时间；
- Queue 长度、拒绝数和丢弃数；
- 缓存命中率与 single-flight 合并次数；
- 取消次数、TaskGroup 失败和异常组内容；
- 幂等重放与幂等冲突；
- request id、trace id 和下游调用 id。

平均延迟会掩盖长尾。容量和 timeout 通常要结合 p95、p99 分位延迟、超时率和错误率观察。p95、p99
分别表示 95%、99% 的请求耗时不超过该值。

仓库的 HTTP 中间件把 `X-Request-ID` 放入响应，并记录 `X-Process-Time`。这是关联请求的起点，不是完整
监控系统。

## 组合这些机制

一次有副作用的远程操作可以按下面的顺序处理：

```text
入口 deadline
      ↓
入口限流或有界 Queue
      ↓
幂等键检查
      ↓
获取下游并发预算
      ↓
单次尝试 timeout
      ↓
只对瞬时错误退避重试
      ↓
原子记录结果
      ↓
释放资源并记录指标
```

具体顺序取决于业务，但两个时间漏洞尤其常见：

- 每次重试重新获得完整 timeout，突破总 deadline；
- 等待 Queue、Semaphore 和退避的时间没有计入总预算。

## 可靠性检查清单

- timeout 不表示远端副作用已经停止；
- 重试只针对可识别瞬时错误和可安全重放操作；
- 排队、退避和重试都计入 deadline；
- Semaphore 不限制所有等待 Task；
- 无界 Queue 不提供背压；
- single-flight 在 key 锁内再次检查缓存；
- TaskGroup 表达共同成功，first-success 表达任一成功；
- 取消任务后继续 await，确保资源完成收尾；
- 进程内对象不会自动约束多实例；
- 没有日志和指标时，无法判断策略是在恢复故障还是放大故障。
