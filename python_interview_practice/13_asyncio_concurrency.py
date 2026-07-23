"""asyncio 并发面试示例。

本文件覆盖：
- coroutine（协程）与 event loop（事件循环）
- asyncio.gather：并发等待一组协程，并保持返回值的输入顺序
- asyncio.create_task：显式创建、命名和等待 Task
- asyncio.timeout / wait_for：为异步操作设置超时
- asyncio.Queue：生产者—消费者模型、join 与 task_done
- Semaphore：限制同时访问稀缺资源的任务数量
- 异常传播与取消：并发代码中常见的资源清理问题

asyncio 适合大量 I/O 密集型任务，例如网络请求、数据库访问和消息处理。
它不会让纯 Python 的 CPU 密集计算自动变快；CPU 密集任务通常考虑多进程。
所有 sleep 都只是在本地模拟 I/O，不访问网络，运行结果稳定且很快。
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from typing import TypeVar

T = TypeVar("T")


def title(text: str) -> None:
    print(f"\n--- {text} ---")


async def simulated_request(name: str, delay: float) -> str:
    """用 sleep 模拟非阻塞 I/O，并返回一个可识别的结果。"""
    await asyncio.sleep(delay)
    return f"{name}:完成"


async def gather_demo() -> None:
    """gather 并发运行协程，并按传入顺序组织结果。"""
    title("asyncio.gather")

    completion_order: list[str] = []

    async def tracked_request(name: str, delay: float) -> str:
        result = await simulated_request(name, delay)
        completion_order.append(name)
        return result

    # 三个协程并发执行。C 最先完成，但 gather 的 results 仍按 A、B、C 排列。
    results = await asyncio.gather(
        tracked_request("A", 0.03),
        tracked_request("B", 0.02),
        tracked_request("C", 0.01),
    )

    print("实际完成顺序:", completion_order)
    print("gather 返回顺序:", results)
    assert completion_order == ["C", "B", "A"]
    assert results == ["A:完成", "B:完成", "C:完成"]

    # return_exceptions=True 会把异常放进结果列表，而不是立刻向外抛出。
    # 适合“尽量完成全部任务”的批处理，但调用者必须逐项检查异常。
    async def divide(numerator: int, denominator: int) -> float:
        await asyncio.sleep(0)
        return numerator / denominator

    mixed_results = await asyncio.gather(
        divide(8, 2),
        divide(8, 0),
        return_exceptions=True,
    )
    normalized = [
        type(item).__name__ if isinstance(item, BaseException) else item for item in mixed_results
    ]
    print("收集普通结果与异常:", normalized)


async def task_demo() -> None:
    """create_task 把协程包装为由事件循环调度的 Task。"""
    title("create_task 与 Task 生命周期")

    first = asyncio.create_task(simulated_request("任务一", 0.02), name="first-request")
    second = asyncio.create_task(simulated_request("任务二", 0.01), name="second-request")

    # create_task 后任务已经进入调度队列；当前协程可以继续做别的工作。
    print("创建后的任务名:", first.get_name(), second.get_name())
    print("创建后立即完成了吗:", first.done(), second.done())

    await asyncio.sleep(0)  # 主动让出控制权，让两个子任务开始运行。
    print("主协程可以同时处理其他工作")

    # 等待 Task 与把协程传给 gather 都可以；Task 还能被命名、取消和查询状态。
    results = await asyncio.gather(first, second)
    print("任务结果:", results)
    print("等待后完成了吗:", first.done(), second.done())

    # 不应“创建后忘记等待”。保存 Task 引用并最终 await，异常才不会悄悄丢失。
    assert first.result() == "任务一:完成"


async def await_with_timeout(
    awaitable: Awaitable[T],
    seconds: float,
) -> T | None:
    """使用 3.11 的 timeout 上下文管理器，超时时返回 None。"""
    try:
        async with asyncio.timeout(seconds):
            return await awaitable
    except TimeoutError:
        return None


async def timeout_demo() -> None:
    """超时通常会取消内部等待，因此被调用方要正确执行 finally 清理。"""
    title("timeout、wait_for 与清理")

    events: list[str] = []

    async def resource_operation(delay: float) -> str:
        events.append("资源已打开")
        try:
            await asyncio.sleep(delay)
            return "操作成功"
        finally:
            # 正常结束、抛异常或被取消，finally 都会运行。
            events.append("资源已关闭")

    timed_out = await await_with_timeout(resource_operation(0.05), seconds=0.01)
    print("asyncio.timeout 结果:", timed_out)
    print("超时后仍执行清理:", events)

    completed = await asyncio.wait_for(
        simulated_request("快速操作", 0.005),
        timeout=0.05,
    )
    print("wait_for 未超时:", completed)

    try:
        await asyncio.wait_for(
            simulated_request("慢速操作", 0.05),
            timeout=0.005,
        )
    except TimeoutError:
        print("wait_for 超时: TimeoutError")


async def queue_demo() -> None:
    """Queue 把生产速度和消费速度解耦，并提供安全的异步等待。"""
    title("asyncio.Queue 生产者—消费者")

    queue: asyncio.Queue[int | None] = asyncio.Queue(maxsize=2)
    processed: list[tuple[int, int]] = []
    worker_count = 2

    async def producer() -> None:
        for number in range(1, 6):
            # 队列满时 put 会挂起，让消费者有机会处理，形成“背压”。
            await queue.put(number)

        # 每个消费者需要一个哨兵值，表示之后不会再有任务。
        for _ in range(worker_count):
            await queue.put(None)

    async def consumer() -> None:
        while True:
            item = await queue.get()
            try:
                if item is None:
                    return
                await asyncio.sleep(0.002)
                processed.append((item, item * item))
            finally:
                # 每一次成功的 get 都必须对应一次 task_done，包括哨兵。
                queue.task_done()

    producer_task = asyncio.create_task(producer(), name="producer")
    consumers = [
        asyncio.create_task(consumer(), name=f"consumer-{index}")
        for index in range(1, worker_count + 1)
    ]

    await producer_task
    # join 等待 unfinished_tasks 计数归零；忘记 task_done 会导致它永远等待。
    await queue.join()
    await asyncio.gather(*consumers)

    # 多消费者的具体分工不应被业务依赖，因此只按任务编号展示最终结果。
    processed.sort()
    print("处理结果:", processed)
    print("队列已清空:", queue.empty())
    assert processed == [(1, 1), (2, 4), (3, 9), (4, 16), (5, 25)]


async def semaphore_demo() -> None:
    """Semaphore 控制并发上限，常用于数据库连接池或 API 限流。"""
    title("Semaphore 限制并发")

    semaphore = asyncio.Semaphore(2)
    active = 0
    peak_active = 0

    async def limited_job(number: int) -> int:
        nonlocal active, peak_active
        async with semaphore:
            active += 1
            peak_active = max(peak_active, active)
            try:
                await asyncio.sleep(0.005)
                return number * 10
            finally:
                active -= 1

    results = await asyncio.gather(*(limited_job(number) for number in range(5)))
    print("任务结果:", results)
    print("观测到的最大并发数:", peak_active)
    assert peak_active == 2


async def cancellation_demo() -> None:
    """取消通过 CancelledError 注入任务；清理后通常应继续传播该异常。"""
    title("Task 取消")

    events: list[str] = []

    async def long_running_job() -> None:
        try:
            events.append("开始")
            await asyncio.Event().wait()  # 永远等待，直到外部取消。
        finally:
            events.append("清理")

    task = asyncio.create_task(long_running_job(), name="cancellable-job")
    await asyncio.sleep(0)  # 让子任务执行到等待点。
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        events.append("已取消")

    print("取消过程:", events)
    print("Task 状态:", f"done={task.done()}", f"cancelled={task.cancelled()}")


async def async_main() -> None:
    await gather_demo()
    await task_demo()
    await timeout_demo()
    await queue_demo()
    await semaphore_demo()
    await cancellation_demo()


def main() -> None:
    # asyncio.run 创建事件循环，执行顶层协程，最后关闭循环。
    # 在已有事件循环的 Jupyter 单元格中，直接写 `await async_main()`。
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
