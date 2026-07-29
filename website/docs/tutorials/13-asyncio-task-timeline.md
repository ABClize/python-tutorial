# asyncio 任务时间线

`asyncio` 最容易混淆的不是 `async` / `await` 语法，而是协程对象、Task、事件循环和等待点之间
如何配合。把执行过程放到时间线上，就能看清“并发”“结果顺序”和“取消”分别发生在哪里。

<p class="source-note">对应源码：<code>python/python_interview_practice/13_asyncio_concurrency.py</code>、<code>python/backend_interview/async_patterns.py</code></p>

## 协程不等于正在运行的任务

调用 `async def` 函数会得到协程对象；只有把它交给事件循环等待，或包装成 Task，它才会推进。

```python
import asyncio


async def fetch(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return name


async def main() -> None:
    tasks = [
        asyncio.create_task(fetch("A", 0.8)),
        asyncio.create_task(fetch("B", 0.5)),
        asyncio.create_task(fetch("C", 0.3)),
    ]
    results = await asyncio.gather(*tasks)
    print(results)  # ['A', 'B', 'C']


asyncio.run(main())
```

`create_task()` 把协程调度为 Task。Task 执行到 `await asyncio.sleep()` 时主动暂停，事件循环就能
运行其他就绪任务；等待时间到了，Task 再从暂停点恢复。

### 不保存 Task 引用会失去生命周期控制

创建后台 Task 后应保存引用、观察异常，并定义谁负责等待或取消。随手 `create_task()` 后丢弃引用，
可能在任务失败时只得到“Task exception was never retrieved”，应用关闭时也无法可靠清理。

```python
background_tasks: set[asyncio.Task] = set()

task = asyncio.create_task(refresh_cache())
background_tasks.add(task)
task.add_done_callback(background_tasks.discard)
```

真正长期后台任务还需要在 lifespan 退出时统一取消并等待，而不是只依赖集合防止回收。

## 完成顺序不等于结果顺序

调整三个任务的延迟，观察它们的实际完成顺序和 `gather()` 返回顺序。也可以在 0.3 秒时取消 B，
查看取消从等待点如何传播。

<ClientOnly>
  <AsyncioTimeline />
</ClientOnly>

`gather()` 并发等待多个 awaitable，但成功时会按传入顺序组织结果，不按完成顺序。若业务需要
“谁先完成就先处理谁”，可以考虑 `asyncio.as_completed()`。

`asyncio.wait()` 则返回 done/pending 两组 Task，可选择 FIRST_COMPLETED、FIRST_EXCEPTION 或
ALL_COMPLETED。它不会自动替你取消 pending，调用方必须明确后续生命周期。

### 为什么总耗时接近最慢任务

三个任务的等待区间重叠，所以总时间接近最大延迟，而不是延迟之和。这种优势只适用于能在
`await` 处让出控制权的 I/O 等待。若在协程里直接执行长时间 CPU 计算或阻塞式 I/O，事件循环
仍会被卡住。

## `await` 是明确的切换点

在单线程事件循环中，普通同步代码会连续执行，直到：

- 遇到尚未完成的 awaitable 并暂停；
- 函数返回或抛出异常；
- 显式把控制权交还事件循环。

这意味着两个 `await` 之间的代码不会被另一个普通 Task 在任意机器指令处“抢占”，但共享状态
仍可能跨越 `await` 形成竞态：

```python
current = counter
await asyncio.sleep(0)
counter = current + 1
```

两个 Task 都可能先读到相同的 `counter`，再分别写回同一个结果。解决方式通常是缩小临界区、
使用 `asyncio.Lock`，或改成消息传递和单一所有者。

## Semaphore 与 Queue 控制压力

创建一万个 Task 再用 gather 等待，虽然语法简短，却可能同时打开过多连接。Semaphore 把真正进入
下游调用的数量限制在 N：

```python
semaphore = asyncio.Semaphore(20)


async def bounded_fetch(url: str):
    async with semaphore:
        return await fetch(url)
```

若输入是持续数据流，Queue 更适合建立生产者/消费者和背压。`asyncio.Queue(maxsize=N)` 满时，
生产者的 `put()` 会等待；消费者每次 `get()` 必须在 finally 中 `task_done()`。

## 取消是一种协作

`task.cancel()` 会请求取消。任务下一次运行到可取消的暂停点时，通常收到
`asyncio.CancelledError`，从而有机会执行 `finally` 清理。

```python
async def worker() -> None:
    resource = await acquire()
    try:
        await use(resource)
    finally:
        await release(resource)
```

不要无意吞掉 `CancelledError`。清理完成后通常应该继续抛出，让上层知道任务没有正常完成。
如果一个操作确实不能被调用方取消，可以研究 `asyncio.shield()`，但它会改变生命周期边界，
不应作为默认兜底。

取消只会在任务重新获得事件循环执行机会时生效。协程中长时间没有 await 的 CPU 循环，既阻塞其他
任务，也无法及时响应取消。需要把 CPU 工作移到进程池、原生实现，或在可接受位置显式让出控制权。

## 超时也建立在取消之上

现代 Python 可以使用 `asyncio.timeout()` 给一段等待设置边界：

```python
async def load() -> str:
    try:
        async with asyncio.timeout(1.0):
            return await fetch("payload", 2.0)
    except TimeoutError:
        return "fallback"
```

超时上下文会取消内部等待，并在边界外转换为 `TimeoutError`。生产代码还要考虑重试是否幂等、
底层资源是否释放，以及客户端超时后服务端工作是否仍在继续。

### 超时预算应逐层递减

外层请求有 2 秒预算时，内部三个依赖不能各自都设置 2 秒并顺序重试。应把剩余 deadline 向下传递，
给清理和响应预留时间。连接超时、读取超时和总操作 deadline 也是不同概念。

## `gather()` 的异常语义

默认情况下，一个子任务抛出异常时，`gather()` 会把异常传播给等待者。其他任务的生命周期需要
根据 Python 版本和调用方式仔细管理，不能仅凭“有一个失败了”就假定所有兄弟任务都已完成清理。

当一组任务具有共同成败关系时，Python 3.11 的 `asyncio.TaskGroup` 更适合表达结构化并发：

```python
async with asyncio.TaskGroup() as group:
    first = group.create_task(fetch("A", 0.8))
    second = group.create_task(fetch("B", 0.5))
```

离开上下文前，任务组会等待成员结束，并以 `ExceptionGroup` 汇总并发错误。

## 阻塞函数如何与事件循环共存

遗留同步 I/O 可以暂时通过 `await asyncio.to_thread(function, ...)` 移到线程池，ContextVar 会被
传播。但这不会让 CPU 密集 Python 代码并行，也无法强制终止已经运行的线程函数。

异步库和同步库不能只看函数名混用。一次阻塞 DNS、文件操作或数据库调用就可能拖住整个事件循环；
可以启用 asyncio debug、记录慢 callback，并在压测中观察事件循环延迟。

## 常见误区

### `async` 会自动使用多个线程

不会。默认事件循环通常在单线程中协作调度 Task。真正的并行 CPU 计算需要进程、原生扩展，
或其他并行方案；阻塞函数可以通过 `asyncio.to_thread()` 移出事件循环线程。

### 每个协程都要立刻 `create_task()`

不需要。直接 `await coroutine()` 表达顺序依赖；`create_task()` 表达“让它独立推进”。
过早创建 Task 会让生命周期和异常归属更难追踪。

### 捕获 `Exception` 就处理了取消

不要依赖这种假设。取消有特殊的控制流语义，应显式考虑、正确清理并按需要继续传播。

## 面试时怎么表述

> 协程对象描述可暂停的计算，Task 把协程交给事件循环调度。任务在未完成的 `await` 处让出控制权，
> 所以多个 I/O 等待可以重叠。`gather()` 成功时按输入顺序返回结果，不代表完成顺序。取消是协作式
> 的，通常在等待点注入 `CancelledError`，代码应在 `finally` 中清理并避免误吞取消。

如果场景进一步涉及并发写共享状态，再补充“切换发生在等待点，但跨等待点仍会产生逻辑竞态”，
并说明锁、队列或单一所有者模型中的选择。
