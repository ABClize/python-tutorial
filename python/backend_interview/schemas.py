"""Pydantic v2 request, response, and polymorphic models."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Any, Generic, Literal, Self, TypeVar
from uuid import UUID

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
    model_validator,
)

from backend_interview.domain import Order, OrderStatus, OrderSummary


def normalize_sku(value: Any) -> Any:
    """先规范化原始输入，再执行字符串和正则约束。"""
    if isinstance(value, str):
        return value.strip().upper()
    return value


Sku = Annotated[
    str,
    BeforeValidator(normalize_sku),
    StringConstraints(pattern=r"^[A-Z0-9-]{3,20}$"),
]
Quantity = Annotated[int, Field(gt=0, le=100)]


class CreateOrderItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sku: Sku
    quantity: Quantity


class CreateOrderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    customer_email: EmailStr
    items: Annotated[list[CreateOrderItem], Field(min_length=1, max_length=20)]

    @field_validator("items")
    @classmethod
    def require_unique_skus(cls, items: list[CreateOrderItem]) -> list[CreateOrderItem]:
        skus = [item.sku for item in items]
        if len(skus) != len(set(skus)):
            raise ValueError("同一个 SKU 只能出现一次")
        return items


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sku: str
    product_name: str
    quantity: int
    unit_price: Decimal

    @computed_field
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_email: EmailStr
    items: list[OrderItemResponse]
    status: OrderStatus
    created_at: str
    version: int
    total: Decimal

    @classmethod
    def from_domain(cls, order: Order) -> OrderResponse:
        payload = {
            "id": order.id,
            "customer_email": order.customer_email,
            "items": order.items,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "version": order.version,
            "total": order.total,
        }
        return cls.model_validate(payload)


class CreateOrderResponse(BaseModel):
    order: OrderResponse
    created: bool


class BulkOrderEntry(BaseModel):
    idempotency_key: Annotated[str, StringConstraints(min_length=8, max_length=64)]
    order: CreateOrderRequest


class BulkCreateOrderRequest(BaseModel):
    entries: Annotated[list[BulkOrderEntry], Field(min_length=1, max_length=20)]


class UpdateOrderStatusRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: OrderStatus


class OrderSummaryResponse(BaseModel):
    order: OrderResponse
    risk_level: Literal["low", "medium", "high"]
    product_labels: dict[str, str]

    @classmethod
    def from_domain(cls, summary: OrderSummary) -> OrderSummaryResponse:
        return cls(
            order=OrderResponse.from_domain(summary.order),
            risk_level=summary.risk_level,
            product_labels=summary.product_labels,
        )


T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1)


class CardPayment(BaseModel):
    kind: Literal["card"]
    last_four: Annotated[str, StringConstraints(pattern=r"^\d{4}$")]


class WalletPayment(BaseModel):
    kind: Literal["wallet"]
    provider: Literal["alipay", "wechat"]
    account_id: Annotated[str, StringConstraints(min_length=3, max_length=64)]


PaymentMethod = Annotated[CardPayment | WalletPayment, Field(discriminator="kind")]


class CheckoutRequest(BaseModel):
    order_id: UUID
    payment: PaymentMethod

    @model_validator(mode="after")
    def require_supported_payment(self) -> Self:
        if isinstance(self.payment, CardPayment) and self.payment.last_four == "0000":
            raise ValueError("测试卡号 0000 不允许支付")
        return self


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
    request_id: str
