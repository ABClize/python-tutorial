"""Framework-independent order domain model."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Literal
from uuid import UUID, uuid4

from backend_interview.exceptions import InvalidStatusTransitionError


class OrderStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


RiskLevel = Literal["low", "medium", "high"]


@dataclass(frozen=True, slots=True)
class OrderItem:
    sku: str
    product_name: str
    quantity: int
    unit_price: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass(frozen=True, slots=True)
class Order:
    id: UUID
    customer_email: str
    items: tuple[OrderItem, ...]
    status: OrderStatus
    created_at: datetime
    version: int

    @classmethod
    def create(cls, customer_email: str, items: tuple[OrderItem, ...]) -> Order:
        return cls(
            id=uuid4(),
            customer_email=customer_email,
            items=items,
            status=OrderStatus.PENDING,
            created_at=datetime.now(UTC),
            version=1,
        )

    @property
    def total(self) -> Decimal:
        return sum((item.subtotal for item in self.items), start=Decimal("0"))

    def transition_to(self, target: OrderStatus) -> Order:
        allowed = {
            OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
            OrderStatus.CONFIRMED: {OrderStatus.CANCELLED},
            OrderStatus.CANCELLED: set(),
        }
        if target == self.status:
            return self
        if target not in allowed[self.status]:
            raise InvalidStatusTransitionError(self.status, target)
        return replace(self, status=target)


@dataclass(frozen=True, slots=True)
class OrderSummary:
    order: Order
    risk_level: RiskLevel
    product_labels: dict[str, str]


@dataclass(frozen=True, slots=True)
class Principal:
    subject: str
    roles: frozenset[str]
