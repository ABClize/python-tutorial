"""Tests for cancellation-safe and backpressure-aware asyncio patterns."""

import asyncio

import pytest

from backend_interview.async_patterns import (
    AsyncSingleFlightCache,
    first_success,
    map_bounded,
    retry_async,
    run_queue_pipeline,
    with_timeout,
)


@pytest.mark.asyncio
async def test_bounded_map_preserves_order_and_limits_active_work() -> None:
    active = 0
    max_active = 0

    async def worker(value: int) -> int:
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        await asyncio.sleep(0.001)
        active -= 1
        return value * 2

    results = await map_bounded(range(10), worker, limit=3)

    assert results == [value * 2 for value in range(10)]
    assert max_active == 3


@pytest.mark.asyncio
async def test_timeout_cancels_slow_operation() -> None:
    cleaned_up = asyncio.Event()

    async def slow() -> None:
        try:
            await asyncio.sleep(1)
        finally:
            cleaned_up.set()

    with pytest.raises(TimeoutError):
        await with_timeout(slow(), 0.001)
    assert cleaned_up.is_set()


@pytest.mark.asyncio
async def test_retry_eventually_succeeds() -> None:
    calls = 0

    async def flaky() -> str:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise OSError("temporary")
        return "ok"

    assert await retry_async(flaky, attempts=3, base_delay=0) == "ok"
    assert calls == 3


@pytest.mark.asyncio
async def test_retry_does_not_retry_programming_error() -> None:
    async def broken() -> str:
        raise ValueError("not transient")

    with pytest.raises(ValueError):
        await retry_async(broken, attempts=3, base_delay=0)


@pytest.mark.asyncio
async def test_first_success_cancels_slower_tasks() -> None:
    cancelled = asyncio.Event()

    async def fail() -> str:
        raise OSError("first failed")

    async def succeed() -> str:
        await asyncio.sleep(0)
        return "winner"

    async def slow() -> str:
        try:
            await asyncio.sleep(10)
            return "late"
        finally:
            cancelled.set()

    result = await first_success([fail(), slow(), succeed()])

    assert result == "winner"
    assert cancelled.is_set()


@pytest.mark.asyncio
async def test_single_flight_coalesces_concurrent_misses() -> None:
    cache: AsyncSingleFlightCache[str, str] = AsyncSingleFlightCache(ttl_seconds=10)
    calls = 0

    async def factory() -> str:
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.001)
        return "value"

    values = await asyncio.gather(*(cache.get_or_create("same-key", factory) for _ in range(20)))

    assert values == ["value"] * 20
    assert calls == 1


@pytest.mark.asyncio
async def test_single_flight_refreshes_after_ttl() -> None:
    now = 0.0
    cache: AsyncSingleFlightCache[str, int] = AsyncSingleFlightCache(
        ttl_seconds=5,
        clock=lambda: now,
    )
    calls = 0

    async def factory() -> int:
        nonlocal calls
        calls += 1
        return calls

    assert await cache.get_or_create("key", factory) == 1
    now = 6
    assert await cache.get_or_create("key", factory) == 2


@pytest.mark.asyncio
async def test_queue_pipeline_processes_each_item_once() -> None:
    processed: list[int] = []

    async def handler(value: int) -> None:
        await asyncio.sleep(0)
        processed.append(value)

    await run_queue_pipeline(list(range(20)), handler, worker_count=4)

    assert sorted(processed) == list(range(20))
    assert len(processed) == 20
