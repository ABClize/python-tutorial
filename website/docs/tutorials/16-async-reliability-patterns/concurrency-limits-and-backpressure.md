# 并发限制与背压

并发限制控制同一时刻正在执行的任务数量。背压表示下游处理不过来时，上游必须减速、等待或拒绝新
任务。`Semaphore` 限制运行中的任务，有界 `Queue` 限制等待中的任务。

数据库连接、文件描述符和下游服务容量都有限，不能因为创建 Task 很便宜就无限创建。

<!-- 对应源码：python/backend_interview/async_patterns.py、python/backend_interview/service.py -->

## Semaphore 限制在途数量

下面让最多 10 个商品查询同时调用下游：

```python
semaphore = asyncio.Semaphore(10)


async def load_bounded(
    product_id: str,
):
    async with semaphore:
        return await catalog_client.get(
            product_id
        )
```

同一时刻最多十个 Task 进入 `get()`。第十一个 Task 会异步等待，不会阻塞事件循环。

并发值应结合：

- 下游限额；
- 连接池大小；
- 应用实例数量；
- 单次延迟和目标吞吐；
- timeout 与队列长度。

值越大不一定越快。下游过载后延迟上升，连接占用更久，反而可能降低整体吞吐。

## Semaphore 没有限制什么

Semaphore 只控制临界区内的 Task 数。它没有限制：

- 等待获取 Semaphore 的 Task 数量；
- 多进程或多实例总并发；
- 单次调用执行多久；
- Task 在进入临界区前已经占用的内存；
- 请求进入应用的总速率。

因此它通常要与 timeout、入口限流和有界 Queue 一起使用。

## `map_bounded()` 保持输入顺序

仓库把 Semaphore 与 TaskGroup 组合：

```python
async def map_bounded(
    values,
    worker,
    *,
    limit: int,
):
    if limit < 1:
        raise ValueError("limit 必须大于 0")

    semaphore = asyncio.Semaphore(limit)

    async def run_one(value):
        async with semaphore:
            return await worker(value)

    tasks = []
    async with asyncio.TaskGroup() as group:
        for value in values:
            tasks.append(
                group.create_task(
                    run_one(value)
                )
            )

    return [task.result() for task in tasks]
```

它有三个重要行为：

1. 同时执行的 worker 不超过 `limit`；
2. 一个 worker 失败时，TaskGroup 取消兄弟任务；
3. 结果按输入顺序返回，而不是完成顺序。

即使第三项先完成，结果仍放在第三个位置，因为 `tasks` 是按输入顺序保存的。

## 大量 Task 仍然会占内存

`map_bounded()` 会为每个输入创建 Task。输入一百万项时，虽然只有十个 Task 同时进入 worker，其余
Task 仍要排队并占用内存。

```text
Semaphore：
  限制正在执行的任务
  不限制已经创建、正在等待的任务
```

有限且不太大的批处理适合这种写法。无限流或超大输入更适合固定 worker 加有界 Queue。

## Queue 把生产和消费分开

下面用 Queue 保存尚未处理的任务，由固定数量的 worker 消费：

```python
queue: asyncio.Queue[str | None] = (
    asyncio.Queue(maxsize=100)
)


async def producer(
    product_id: str,
) -> None:
    await queue.put(product_id)
```

队列已有 100 项时，`put()` 会等待消费者取走一项。这会把下游处理速度反馈给生产者，也就是背压。

无界 Queue 不会控制积压，只会把过载变成内存增长和更长等待时间。

## 队列满时需要业务策略

等待并不是唯一选择。系统应根据任务性质决定：

- 等待，但不能超过请求 deadline；
- 快速拒绝，让调用方稍后重试；
- 丢弃低优先级或已过期任务；
- 转入有持久化能力的消息系统。

例如用户同步请求不应无期限排队；离线作业可以等待更久；日志采样在极端压力下可能允许丢弃部分低价值
数据。

## `task_done()` 与 `join()`

worker 每次 `get()` 都要对应一次 `task_done()`：

```python
async def queue_worker(
    queue,
    handler,
) -> None:
    while True:
        item = await queue.get()
        try:
            if item is None:
                return
            await handler(item)
        finally:
            queue.task_done()
```

`queue.join()` 等待的是“所有放入队列的项都已经调用 task_done”，不是“队列当前为空”。遗漏
`task_done()` 会让 join 永远等待；多调用又会抛错。

这里的 `None` 是停止哨兵。每个 worker 都需要一个哨兵，才能全部退出。

## worker 失败可能让管线卡住

仓库中的 `queue_worker()` 若在 handler 处抛错，会结束当前 worker。队列中还有项目时，
`run_queue_pipeline()` 可能停在 `queue.join()`，因为剩余项再也无人消费。

生产级管线必须定义失败协议：

- 任一项失败就取消所有 worker；
- 单项按条件重试；
- 失败项写入死信队列；
- 记录失败后继续其他项。

仅仅使用 Queue 不会自动获得可靠 worker 池。

## 限制应该放在哪个生命周期

`OrderService` 构造时创建批量 Semaphore。FastAPI 每次请求都会组装新的 Service，因此它主要限制
单次批量请求内部，并不是全进程共享上限。

如果目标是：

| 目标范围 | 限制器放置位置 |
| --- | --- |
| 单个批量操作 | 当前服务实例 |
| 一个应用进程 | lifespan 创建的共享对象 |
| 多个实例总量 | API 网关、共享存储或下游配额 |

锁和 Semaphore 的作用范围由它们实际共享的范围决定，名称叫“global”也不能让进程内对象自动跨机器。

## 同时限制执行量和积压量

一个常见组合是：

```text
入口速率限制
      ↓
有界等待队列
      ↓
Semaphore 控制在途数
      ↓
单次调用 timeout
```

入口控制新流量，Queue 控制积压，Semaphore 保护执行资源，timeout 防止慢任务长期占位。每一层解决的
问题不同，不能相互替代。
