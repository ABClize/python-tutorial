# 超时与截止时间

超时是某段等待允许使用的最长时长。截止时间是一个绝对时刻，表示整项工作最晚何时结束。超时适合
限制单个操作，截止时间适合让整条调用链共用一份时间预算。

没有时间限制的慢调用会长期占用连接、Task 和请求数据。

<!-- 对应源码：python/backend_interview/async_patterns.py、python/backend_interview/service.py -->

## 没有超时的调用

下面的函数会一直等待下游返回，没有最长等待时间：

```python
async def load_product(
    product_id: str,
) -> dict:
    return await catalog_client.get(product_id)
```

只要 `get()` 一直不返回，调用者就一直等待。即使事件循环还能运行其他 Task，这个请求本身占用的资源
并没有释放。

远程调用通常需要分别考虑：

| 问题 | 对应机制 |
| --- | --- |
| 单次最多等多久 | timeout |
| 整条请求最晚何时结束 | deadline |
| 超时后资源怎样释放 | 取消传播、`finally` |
| 有副作用的远端到底执行没有 | 幂等查询或结果确认 |

## 用 `asyncio.timeout()` 限制等待

仓库中的包装函数很短：

```python
import asyncio
from collections.abc import Awaitable
from typing import TypeVar

R = TypeVar("R")


async def with_timeout(
    awaitable: Awaitable[R],
    seconds: float,
) -> R:
    async with asyncio.timeout(seconds):
        return await awaitable
```

使用时捕获内置 `TimeoutError`：

```python
async def load_product(catalog_client):
    try:
        return await with_timeout(
            catalog_client.get("PY-BOOK"),
            seconds=0.5,
        )
    except TimeoutError:
        print("商品服务超时")
        return None
```

超过 0.5 秒后，timeout 会取消当前 Task，在上下文内部产生 `CancelledError`，再由上下文管理器
转换成外部可捕获的 `TimeoutError`。

## 超时会触发取消

底层协程通常在下一个 await 点收到取消。资源清理应放进 `finally`：

```python
async def fetch(client, url):
    response = await client.open(url)
    try:
        return await response.read()
    finally:
        await response.close()
```

若协程长时间执行纯 CPU 代码且没有 await，它无法及时处理取消。使用了不响应取消的阻塞库时，
`asyncio.timeout()` 也不能强制停止底层线程或远端系统。

## 超时不等于副作用没有发生

下面的时间线很常见：

```text
客户端发起扣款
        ↓
支付服务已扣款
        ↓
响应在网络中延迟
        ↓
客户端超时
```

客户端只知道“没有按时收到结果”，不能据此判断“远端没有执行”。因此支付、创建订单和发消息等操作
需要幂等键、查询结果接口或业务流水号配合。

## 超时可以包围一组操作

下面让多个步骤共同使用一个超时：

```python
async def load_product_and_stock(
    product_id: str,
):
    async with asyncio.timeout(1.0):
        product = await load_product(product_id)
        stock = await load_stock(product_id)
    return product, stock
```

两个 await 共同使用 1 秒。若第一个耗时 0.8 秒，第二个大约只剩 0.2 秒，而不是重新获得 1 秒。

仓库中的 `OrderService.create_order()` 把一组商品和库存查询放进同一个 timeout。任何一个下游依赖
未能在配置时间内完成，服务都会转换成 `UpstreamTimeoutError`。

## 单次 timeout 会层层累加

假设入口承诺 2 秒完成，而每层都给下游完整 2 秒：

```text
认证最多 2 秒
读取订单最多 2 秒
调用风控最多 2 秒
```

最坏情况可能远超入口承诺。timeout 是相对时长；每层重新计时会丢失已经消耗的时间。

## deadline 是绝对截止时刻

事件循环提供单调时钟，可以记录统一截止点：

```python
import asyncio


async def handle() -> None:
    loop = asyncio.get_running_loop()
    deadline = loop.time() + 2.0

    async with asyncio.timeout_at(deadline):
        await perform_request()
```

下层收到同一个 deadline 后，可以计算剩余时间：

```python
remaining = deadline - loop.time()
if remaining <= 0:
    raise TimeoutError
```

这样认证花掉 0.1 秒后，后续只剩 1.9 秒。还要为错误映射、序列化和资源清理预留余量，不能把全部预算
都交给最后一个下游。

当前仓库使用固定的 `request_timeout_seconds`，没有实现跨层 deadline 传播。deadline 是在更长调用链
中的进一步设计，不是现有源码功能。

## 超时值怎样确定

超时太短会误伤正常长尾请求，太长又不能及时释放容量。设置时需要结合：

- 入口的响应时间目标；
- 下游 p95、p99 延迟，即分别有 95%、99% 的请求耗时不超过该值；
- 是否还有重试；
- 连接池和并发上限；
- 清理与响应生成需要的时间。

单次尝试 timeout、整条调用 deadline 和客户端 timeout 应相互协调。客户端比服务端更早放弃时，服务端
可能继续做无用工作；服务端预算远大于入口预算时，内部等待也无法兑现外部承诺。

## 超时与截止时间注意事项

- 每个远程等待都应有上限；
- 一组操作需要共同预算时，在外层设置 timeout；
- 更长的调用链应传播 deadline；
- timeout 会通过取消结束等待，协程必须正确清理；
- 超时只能证明没有按时得到结果，不能证明远端副作用没发生；
- 排队、退避和获取 Semaphore 的时间也应计入总预算。
