"""并发面试题：线程、锁、队列、线程池和 asyncio。

这些例子刻意让最终结果保持确定性，方便重复运行和调试。
"""

from __future__ import annotations

import sys

if __package__ in (None, "") and sys.path:
    # 防止同目录的 collections.py 遮蔽标准库。
    sys.path.pop(0)

import asyncio
import itertools
import threading
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from typing import TypeVar, cast

T = TypeVar("T")
R = TypeVar("R")


class ThreadSafeCounter:
    """题目：实现线程安全计数器。

    ``value += amount`` 是读、计算、写的组合操作，因此用 Lock 保护。
    单次增加和读取的时间复杂度、空间复杂度均为 O(1)。
    """

    def __init__(self) -> None:
        self._value = 0
        self._lock = threading.Lock()

    def increment(self, amount: int = 1) -> None:
        with self._lock:
            self._value += amount

    @property
    def value(self) -> int:
        with self._lock:
            return self._value


def count_from_threads(thread_count: int, increments_per_thread: int) -> int:
    """启动多个线程累加，并等待全部线程结束。

    时间复杂度：O(thread_count * increments_per_thread)
    空间复杂度：O(thread_count)
    """

    if thread_count < 0 or increments_per_thread < 0:
        raise ValueError("线程数和增加次数不能为负数")

    counter = ThreadSafeCounter()

    def worker() -> None:
        for _ in range(increments_per_thread):
            counter.increment()

    threads = [threading.Thread(target=worker) for _ in range(thread_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return counter.value


def parallel_map_ordered(
    function: Callable[[T], R],
    values: Iterable[T],
    max_workers: int = 4,
) -> list[R]:
    """题目：并发执行独立任务，并让结果保持输入顺序。

    ``executor.map`` 会按输入顺序产生结果，即使任务完成顺序不同。
    线程池适合存在等待的 I/O 任务；纯 Python CPU 密集任务通常受 GIL 限制。

    时间复杂度取决于 function；额外空间为 O(n + max_workers)。
    """

    if max_workers <= 0:
        raise ValueError("max_workers 必须为正整数")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(function, values))


_STOP = object()


def queue_pipeline(values: list[int], worker_count: int = 3) -> list[int]:
    """题目：用线程安全队列实现生产者—消费者模型。

    每个任务携带原下标，最后按下标组装结果，所以输出完全确定。
    ``task_done`` 与 ``join`` 配对，确保队列中的每项都已经处理。

    时间复杂度：O(n)
    空间复杂度：O(n + worker_count)
    """

    if worker_count <= 0:
        raise ValueError("worker_count 必须为正整数")

    tasks: Queue[object] = Queue()
    results: dict[int, int] = {}
    results_lock = threading.Lock()

    def worker() -> None:
        while True:
            task = tasks.get()
            try:
                if task is _STOP:
                    return
                index, value = cast(tuple[int, int], task)
                squared = value * value
                with results_lock:
                    results[index] = squared
            finally:
                tasks.task_done()

    threads = [threading.Thread(target=worker) for _ in range(worker_count)]
    for thread in threads:
        thread.start()

    for index, value in enumerate(values):
        tasks.put((index, value))
    for _ in threads:
        tasks.put(_STOP)

    tasks.join()
    for thread in threads:
        thread.join()

    return [results[index] for index in range(len(values))]


async def async_double(value: int) -> int:
    """模拟一次会主动让出控制权的异步 I/O 操作。"""

    await asyncio.sleep(0)
    return value * 2


async def async_map_ordered(values: list[int]) -> list[int]:
    """题目：并发等待多个协程，并保持输入顺序。

    ``asyncio.gather`` 的返回顺序与传入 awaitable 的顺序一致。
    创建 n 个协程需要 O(n) 额外空间。
    """

    return list(await asyncio.gather(*(async_double(value) for value in values)))


class BankAccount:
    """用于演示多把锁的固定加锁顺序。"""

    _order_source = itertools.count()

    def __init__(self, name: str, balance_cents: int) -> None:
        if balance_cents < 0:
            raise ValueError("初始余额不能为负数")
        self.name = name
        self._balance_cents = balance_cents
        self._lock = threading.Lock()
        self._lock_order = next(self._order_source)

    @property
    def balance_cents(self) -> int:
        with self._lock:
            return self._balance_cents


def transfer(source: BankAccount, target: BankAccount, amount_cents: int) -> None:
    """题目：线程安全转账，同时规避 ABBA 死锁。

    无论转账方向如何，总是按账户创建顺序获取两把锁。单次操作 O(1)。
    """

    if source is target:
        return
    if amount_cents <= 0:
        raise ValueError("转账金额必须为正数")

    first, second = sorted(
        (source, target),
        key=lambda account: account._lock_order,
    )
    with first._lock, second._lock:
        if source._balance_cents < amount_cents:
            raise ValueError("余额不足")
        source._balance_cents -= amount_cents
        target._balance_cents += amount_cents


def run_balanced_transfers(rounds: int = 500) -> tuple[int, int]:
    """让两个线程进行方向相反的等额转账，最终余额应保持不变。"""

    account_a = BankAccount("A", 100_000)
    account_b = BankAccount("B", 100_000)

    def repeat_transfer(source: BankAccount, target: BankAccount) -> None:
        for _ in range(rounds):
            transfer(source, target, 1)

    threads = [
        threading.Thread(target=repeat_transfer, args=(account_a, account_b)),
        threading.Thread(target=repeat_transfer, args=(account_b, account_a)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    return account_a.balance_cents, account_b.balance_cents


def square(value: int) -> int:
    """模块级函数便于在线程池和调试器中观察。"""

    return value * value


def run_tests() -> None:
    assert count_from_threads(4, 1_000) == 4_000
    assert count_from_threads(0, 100) == 0

    assert parallel_map_ordered(square, [3, 1, 4, 2], max_workers=2) == [
        9,
        1,
        16,
        4,
    ]
    assert queue_pipeline([5, 2, 8, 1], worker_count=2) == [25, 4, 64, 1]
    assert queue_pipeline([], worker_count=2) == []

    assert asyncio.run(async_map_ordered([3, 1, 4])) == [6, 2, 8]

    balance_a, balance_b = run_balanced_transfers()
    assert (balance_a, balance_b) == (100_000, 100_000)
    assert balance_a + balance_b == 200_000


def main() -> None:
    run_tests()
    print("线程安全计数:", count_from_threads(5, 200))
    print("队列流水线:", queue_pipeline([1, 2, 3, 4]))
    print("异步结果:", asyncio.run(async_map_ordered([10, 20, 30])))
    print("concurrency.py：全部测试通过")


if __name__ == "__main__":
    main()
