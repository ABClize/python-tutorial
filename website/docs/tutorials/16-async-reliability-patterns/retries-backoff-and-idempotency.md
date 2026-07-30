# 重试、退避与幂等

重试是在调用失败后再次执行。退避是在下一次重试前等待一段时间。幂等表示同一个操作重复执行，不会
重复产生副作用。

短暂网络故障可以重试。参数错误、权限拒绝和永久业务失败通常不应重试。有副作用的操作只有具备幂等
保证后才能安全重放。

<!-- 对应源码：python/backend_interview/async_patterns.py、python/backend_interview/repository.py、python/backend_interview/service.py -->

## 先判断是否应该重试

适合重试的操作通常同时满足：

1. 失败是暂时的，例如连接重置或服务短暂不可用；
2. 能准确识别这种失败；
3. 操作没有副作用，或已经具备幂等保证；
4. 总 deadline 还有时间；
5. 额外请求不会压垮下游。

通常不应重试：

- 请求格式错误；
- 认证或权限失败；
- 明确的库存不足等业务拒绝；
- 没有幂等保证的副作用；
- 调用方取消；
- 已耗尽总时间预算。

重试不是通用异常处理。把所有异常都再执行一次，常常只是推迟失败并放大流量。

## 仓库中的 `retry_async()`

下面的函数按指定次数重试异步操作，并在每次失败后等待：

```python
async def retry_async(
    operation,
    *,
    attempts: int,
    base_delay: float = 0.01,
    retry_for: tuple[
        type[Exception], ...
    ] = (OSError,),
):
    if attempts < 1:
        raise ValueError("attempts 必须大于 0")

    for attempt in range(attempts):
        try:
            return await operation()
        except retry_for:
            if attempt == attempts - 1:
                raise
            await asyncio.sleep(
                base_delay * 2**attempt
            )
```

`attempts` 是总尝试次数，包括第一次调用。`attempts=3` 的过程是：

```text
第 1 次失败 -> 等待 base_delay
第 2 次失败 -> 等待 base_delay * 2
第 3 次失败 -> 直接抛出，不再等待
```

默认只捕获 `OSError`。若业务定义了另一种瞬时错误，需要显式传入：

```python
result = await retry_async(
    operation,
    attempts=3,
    retry_for=(
        OSError,
        TemporaryServiceError,
    ),
)
```

不要为了方便传 `Exception`，否则代码缺陷和业务拒绝也可能被重复执行。

## 取消不应被当成失败重试

`asyncio.CancelledError` 继承自 `BaseException`，不属于这里捕获的 `Exception`。外部 timeout 或调用方
取消 Task 时，重试循环会停止。

这正是期望行为。取消表示上层不再需要结果，继续 sleep 和重新请求只会浪费资源。

## 指数退避

立即重试容易再次撞在同一个故障窗口。指数退避逐步增加间隔：

```text
0.1 秒 -> 0.2 秒 -> 0.4 秒 -> 0.8 秒
```

仓库使用 `base_delay * 2**attempt`。生产实现通常还会设置最大等待值，否则高次重试可能产生不可接受的
延迟。

## 随机抖动打散重试

许多客户端同时失败时，完全相同的退避会让它们再次同时醒来。随机抖动可以打散请求：

```python
import asyncio
import random


async def sleep_with_jitter(
    base_delay: float,
    attempt: int,
) -> None:
    maximum = base_delay * 2**attempt
    delay = random.uniform(0, maximum)
    await asyncio.sleep(delay)
```

实际实现还应记录等待时长，并在测试中注入随机源与 sleep，使结果可重复。

当前 `retry_async()` 只有指数退避，没有 jitter，也没有接收总 deadline。这是源码的实际边界。

## 重试必须受总预算限制

假设单次 timeout 是 1 秒，最多尝试三次，退避为 0.1 和 0.2 秒：

```text
最坏等待约为 1 + 0.1 + 1 + 0.2 + 1 = 3.3 秒
```

若入口只允许 2 秒，这个策略不可能兑现承诺。每次尝试前要检查剩余 deadline，并把 sleep 也算进预算。

## 幂等让副作用可以安全重放

创建订单可能在服务端成功、响应却丢失。客户端重发时携带相同键：

```text
Idempotency-Key: tutorial-order-001
```

服务层先查已有结果；真正的并发安全由仓储在同一原子操作中保证：

```text
检查幂等键
      ↓
不存在才保存订单
      ↓
保存 key -> order_id 映射
```

第二次请求会得到第一次的订单，并返回 `created=false`。

真实数据库一般依赖唯一索引和事务。只写“先查、再插入”会有竞态，两个并发请求可能同时查到不存在。

## 幂等不只是保存一个 key

完整设计还要处理：

- 相同 key 是否绑定相同请求体；
- 记录保存多久；
- 处理中请求再次到达时是等待还是返回状态；
- 第一次执行失败是否保留记录；
- 多实例怎样共享幂等状态。

当前内存仓储没有保存请求摘要，所以相同 key 配不同请求体时也会返回旧订单。生产实现应明确拒绝这种
冲突。

## 把重试与幂等放在一起理解

读取通常天然可重放；写入必须先建立幂等语义。可靠调用的顺序可以理解为：

```text
确认错误可恢复
      ↓
确认操作可安全重放
      ↓
检查剩余 deadline
      ↓
等待退避并重试
```

少任何一步，重试都可能从“恢复机制”变成“重复副作用或流量放大器”。
