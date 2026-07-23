"""External service protocols and deterministic fake adapters."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from backend_interview.domain import Order, RiskLevel
from backend_interview.exceptions import (
    InsufficientInventoryError,
    ProductUnavailableError,
)


@dataclass(frozen=True, slots=True)
class Product:
    sku: str
    name: str
    price: Decimal


class CatalogGateway(Protocol):
    async def get_product(self, sku: str) -> Product: ...


class InventoryGateway(Protocol):
    async def ensure_available(self, sku: str, quantity: int) -> None: ...


class RiskGateway(Protocol):
    async def assess(self, order: Order) -> RiskLevel: ...


class FakeCatalogGateway:
    def __init__(
        self,
        products: dict[str, Product] | None = None,
        latency: float = 0,
    ) -> None:
        self.products = products or {
            "PY-BOOK": Product("PY-BOOK", "Python Interview Book", Decimal("59.90")),
            "API-COURSE": Product("API-COURSE", "FastAPI Course", Decimal("199.00")),
            "ASYNC-LAB": Product("ASYNC-LAB", "Asyncio Practice Lab", Decimal("89.50")),
        }
        self.latency = latency

    async def get_product(self, sku: str) -> Product:
        await asyncio.sleep(self.latency)
        try:
            return self.products[sku]
        except KeyError:
            raise ProductUnavailableError(sku) from None


class FakeInventoryGateway:
    def __init__(
        self,
        stock: dict[str, int] | None = None,
        latency: float = 0,
    ) -> None:
        self.stock = stock or {
            "PY-BOOK": 100,
            "API-COURSE": 1000,
            "ASYNC-LAB": 20,
        }
        self.latency = latency
        self.active_calls = 0
        self.max_active_calls = 0
        self._metrics_lock = asyncio.Lock()

    async def ensure_available(self, sku: str, quantity: int) -> None:
        async with self._metrics_lock:
            self.active_calls += 1
            self.max_active_calls = max(self.max_active_calls, self.active_calls)
        try:
            await asyncio.sleep(self.latency)
            available = self.stock.get(sku, 0)
            if available < quantity:
                raise InsufficientInventoryError(sku, quantity, available)
        finally:
            async with self._metrics_lock:
                self.active_calls -= 1


class FakeRiskGateway:
    def __init__(self, latency: float = 0) -> None:
        self.latency = latency

    async def assess(self, order: Order) -> RiskLevel:
        await asyncio.sleep(self.latency)
        if "risk" in order.customer_email:
            return "high"
        if order.total >= Decimal("500"):
            return "medium"
        return "low"
