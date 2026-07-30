# 并发限制、队列与异步资源

一次创建大量 Task 可能压垮连接池或下游服务。Semaphore 限制同时运行数量，有限 Queue 限制积压，
异步迭代与上下文管理器则表达需要等待的数据流和资源生命周期。

<p class="source-note">对应源码：<code>python/python_interview_practice/13_asyncio_concurrency.py</code>、<code>python/backend_interview/async_patterns.py</code></p>

## Semaphore

```python
import asyncio

semaphore = asyncio.Semaphore(2)


async def limited_job(number: int) -> int:
    async with semaphore:
        await asyncio.sleep(0.1)
        return number * 10


async def main() -> list[int]:
    return list(
        await asyncio.gather(
            *(limited_job(number) for number in range(5))
        )
    )
```

五个任务可以同时存在，但同一时刻最多两个任务进入受保护区域。

Semaphore 只限制临界区内并发，不限制等待获取它的 Task 数量。输入规模可能持续增长时，还需要有界
Queue 或分批读取。

## asyncio.Queue

```python
async def worker(
    queue: asyncio.Queue[str | None],
) -> None:
    while True:
        item = await queue.get()
        try:
            if item is None:
                return
            print("处理", item)
        finally:
            queue.task_done()
```

有限队列：

```python
queue: asyncio.Queue[str | None] = asyncio.Queue(
    maxsize=100
)
```

队列满时 `await queue.put(item)` 暂停生产者；队列空时 `await queue.get()` 暂停消费者。双方不需要
循环 sleep 检查状态。

## Queue 的关闭流程

1. 创建固定数量消费者；
2. 放入普通任务；
3. 为每个消费者放入一个停止哨兵；
4. `await queue.join()` 等待未完成计数归零；
5. `await asyncio.gather(*workers)` 等待消费者退出。

每次成功 `get()` 都要对应 `task_done()`，包括哨兵。遗漏时 `join()` 会一直等待。

仓库中的 `queue_demo()` 在多消费者处理后按任务编号排序结果，因为具体消费者分工不应成为业务契约。

## 异步生成器

数据每一项都可能需要等待时，使用 `async for`：

```python
async def numbers():
    for number in range(3):
        await asyncio.sleep(0)
        yield number


async def main() -> None:
    async for number in numbers():
        print(number)
```

异步生成器逐项产生数据，不必等待全部完成后一次返回。

## 异步上下文管理器

资源的获取和释放本身需要 await 时，使用 `async with`：

```python
async with client.stream("GET", url) as response:
    async for chunk in response.aiter_bytes():
        process(chunk)
```

`__aenter__` 和 `__aexit__` 可以执行异步操作。数据库事务、流式 HTTP 响应和异步锁都常使用这个协议。

## 容量和资源注意事项

- Semaphore 上限要与连接池和下游配额协调；
- Queue 应有容量或明确的拒绝策略；
- 生产速度长期大于消费速度时，增加 Task 只会扩大积压；
- 异步生成器通常只能向前消费，错误可能在迭代中途发生；
- `async with` 退出阶段也可能需要处理异常和取消；
- asyncio 主要提高 I/O 并发，不会让 CPU 计算自动并行。
