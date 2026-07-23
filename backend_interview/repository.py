"""Async repository abstraction and race-safe in-memory implementation."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from dataclasses import replace
from typing import Protocol
from uuid import UUID

from backend_interview.domain import Order
from backend_interview.exceptions import OptimisticLockError, OrderNotFoundError


class OrderRepository(Protocol):
    async def find_by_idempotency_key(self, key: str) -> Order | None: ...

    async def create(self, order: Order, idempotency_key: str) -> tuple[Order, bool]: ...

    async def get(self, order_id: UUID) -> Order | None: ...

    async def list(self, offset: int, limit: int) -> list[Order]: ...

    async def count(self) -> int: ...

    async def save(self, order: Order, expected_version: int) -> Order: ...

    async def close(self) -> None: ...


class InMemoryOrderRepository:
    """A deterministic repository for interviews and tests.

    The lock makes the idempotency check and insert atomic. In production this
    invariant should normally be enforced by a database unique constraint too.
    """

    def __init__(self) -> None:
        self._orders: dict[UUID, Order] = {}
        self._order_id_by_idempotency_key: dict[str, UUID] = {}
        self._lock = asyncio.Lock()
        self.closed = False

    def _ensure_open(self) -> None:
        if self.closed:
            raise RuntimeError("仓储已经关闭")

    async def find_by_idempotency_key(self, key: str) -> Order | None:
        self._ensure_open()
        async with self._lock:
            order_id = self._order_id_by_idempotency_key.get(key)
            order = self._orders.get(order_id) if order_id is not None else None
            return deepcopy(order)

    async def create(self, order: Order, idempotency_key: str) -> tuple[Order, bool]:
        self._ensure_open()
        async with self._lock:
            existing_id = self._order_id_by_idempotency_key.get(idempotency_key)
            if existing_id is not None:
                return deepcopy(self._orders[existing_id]), False

            self._orders[order.id] = deepcopy(order)
            self._order_id_by_idempotency_key[idempotency_key] = order.id
            return deepcopy(order), True

    async def get(self, order_id: UUID) -> Order | None:
        self._ensure_open()
        async with self._lock:
            return deepcopy(self._orders.get(order_id))

    async def list(self, offset: int, limit: int) -> list[Order]:
        self._ensure_open()
        async with self._lock:
            ordered = sorted(
                self._orders.values(),
                key=lambda order: (order.created_at, str(order.id)),
            )
            return deepcopy(ordered[offset : offset + limit])

    async def count(self) -> int:
        self._ensure_open()
        async with self._lock:
            return len(self._orders)

    async def save(self, order: Order, expected_version: int) -> Order:
        self._ensure_open()
        async with self._lock:
            existing = self._orders.get(order.id)
            if existing is None:
                raise OrderNotFoundError(str(order.id))
            if existing.version != expected_version:
                raise OptimisticLockError(expected_version, existing.version)

            saved = replace(order, version=existing.version + 1)
            self._orders[order.id] = deepcopy(saved)
            return deepcopy(saved)

    async def close(self) -> None:
        async with self._lock:
            self.closed = True
