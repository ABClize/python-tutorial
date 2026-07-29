"""Project-style asyncio patterns frequently discussed in interviews."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from time import monotonic
from typing import Generic, TypeVar, cast

T = TypeVar("T")
R = TypeVar("R")
K = TypeVar("K")
V = TypeVar("V")


async def map_bounded(
    values: Iterable[T],
    worker: Callable[[T], Awaitable[R]],
    *,
    limit: int,
) -> list[R]:
    """Run I/O concurrently while bounding pressure on the downstream service."""
    if limit < 1:
        raise ValueError("limit 必须大于 0")

    semaphore = asyncio.Semaphore(limit)

    async def run_one(value: T) -> R:
        async with semaphore:
            return await worker(value)

    tasks: list[asyncio.Task[R]] = []
    async with asyncio.TaskGroup() as task_group:
        for value in values:
            tasks.append(task_group.create_task(run_one(value)))
    return [task.result() for task in tasks]


async def with_timeout(awaitable: Awaitable[R], seconds: float) -> R:
    """Apply a deadline and expose the built-in ``TimeoutError`` to the caller."""
    async with asyncio.timeout(seconds):
        return await awaitable


async def retry_async(
    operation: Callable[[], Awaitable[R]],
    *,
    attempts: int,
    base_delay: float = 0.01,
    retry_for: tuple[type[Exception], ...] = (OSError,),
) -> R:
    """Retry transient failures with exponential backoff.

    Cancellation is not caught because ``CancelledError`` derives from
    ``BaseException``. That is intentional: callers must be able to stop work.
    """
    if attempts < 1:
        raise ValueError("attempts 必须大于 0")

    for attempt in range(attempts):
        try:
            return await operation()
        except retry_for:
            if attempt == attempts - 1:
                raise
            await asyncio.sleep(base_delay * 2**attempt)
    raise AssertionError("循环一定会返回或抛出异常")


async def first_success(operations: Iterable[Awaitable[R]]) -> R:
    """Return the first successful result and cancel remaining work."""
    tasks: list[asyncio.Future[R]] = [asyncio.ensure_future(operation) for operation in operations]
    if not tasks:
        raise ValueError("至少需要一个操作")

    errors: list[Exception] = []
    try:
        for completed in asyncio.as_completed(tasks):
            try:
                return cast(R, await completed)
            except Exception as error:
                errors.append(error)
        raise ExceptionGroup("所有操作都失败", errors)
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


@dataclass(slots=True)
class CacheEntry(Generic[V]):
    value: V
    expires_at: float


class AsyncSingleFlightCache(Generic[K, V]):
    """TTL cache that coalesces concurrent cache misses for the same key."""

    def __init__(self, ttl_seconds: float, clock: Callable[[], float] = monotonic) -> None:
        if ttl_seconds <= 0:
            raise ValueError("TTL 必须大于 0")
        self.ttl_seconds = ttl_seconds
        self.clock = clock
        self._entries: dict[K, CacheEntry[V]] = {}
        self._locks: dict[K, asyncio.Lock] = {}
        self._locks_guard = asyncio.Lock()

    def _fresh_value(self, key: K) -> V | None:
        entry = self._entries.get(key)
        if entry is None or entry.expires_at <= self.clock():
            return None
        return entry.value

    async def _lock_for(self, key: K) -> asyncio.Lock:
        async with self._locks_guard:
            return self._locks.setdefault(key, asyncio.Lock())

    async def get_or_create(
        self,
        key: K,
        factory: Callable[[], Awaitable[V]],
    ) -> V:
        cached = self._fresh_value(key)
        if cached is not None:
            return cached

        lock = await self._lock_for(key)
        async with lock:
            cached = self._fresh_value(key)
            if cached is not None:
                return cached
            value = await factory()
            self._entries[key] = CacheEntry(
                value=value,
                expires_at=self.clock() + self.ttl_seconds,
            )
            return value


async def queue_worker(
    queue: asyncio.Queue[T | None],
    handler: Callable[[T], Awaitable[None]],
) -> None:
    """Consume until a sentinel is received and always balance ``task_done``."""
    while True:
        item = await queue.get()
        try:
            if item is None:
                return
            await handler(item)
        finally:
            queue.task_done()


async def run_queue_pipeline(
    values: list[T],
    handler: Callable[[T], Awaitable[None]],
    *,
    worker_count: int,
) -> None:
    if worker_count < 1:
        raise ValueError("worker_count 必须大于 0")

    queue: asyncio.Queue[T | None] = asyncio.Queue()
    workers = [
        asyncio.create_task(queue_worker(queue, handler), name=f"worker:{index}")
        for index in range(worker_count)
    ]
    for value in values:
        await queue.put(value)
    for _ in workers:
        await queue.put(None)
    await queue.join()
    await asyncio.gather(*workers)


async def _demo() -> None:
    active = 0
    max_active = 0

    async def double(value: int) -> int:
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        await asyncio.sleep(0)
        active -= 1
        return value * 2

    assert await map_bounded(range(10), double, limit=3) == [
        0,
        2,
        4,
        6,
        8,
        10,
        12,
        14,
        16,
        18,
    ]
    assert max_active <= 3


if __name__ == "__main__":
    asyncio.run(_demo())
    print("asyncio 项目模式检查通过")
