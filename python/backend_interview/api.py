"""FastAPI routes: validation, dependencies, pagination, and concurrency."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, status

from backend_interview.dependencies import (
    ServiceDep,
    audit_request,
    require_api_key,
)
from backend_interview.schemas import (
    BulkCreateOrderRequest,
    CheckoutRequest,
    CreateOrderRequest,
    CreateOrderResponse,
    OrderResponse,
    OrderSummaryResponse,
    Page,
    UpdateOrderStatusRequest,
)

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    dependencies=[Depends(require_api_key), Depends(audit_request)],
)


@router.post(
    "",
    response_model=CreateOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    command: CreateOrderRequest,
    service: ServiceDep,
    idempotency_key: Annotated[
        str,
        Header(alias="Idempotency-Key", min_length=8, max_length=64),
    ],
) -> CreateOrderResponse:
    result = await service.create_order(command, idempotency_key)
    return CreateOrderResponse(
        order=OrderResponse.from_domain(result.order),
        created=result.created,
    )


@router.post("/bulk", response_model=list[CreateOrderResponse])
async def bulk_create_orders(
    command: BulkCreateOrderRequest,
    service: ServiceDep,
) -> list[CreateOrderResponse]:
    results = await service.bulk_create(
        [(entry.order, entry.idempotency_key) for entry in command.entries]
    )
    return [
        CreateOrderResponse(
            order=OrderResponse.from_domain(result.order),
            created=result.created,
        )
        for result in results
    ]


@router.post("/payment/validate", response_model=CheckoutRequest)
async def validate_payment(command: CheckoutRequest) -> CheckoutRequest:
    """Echo a validated discriminated union for Pydantic interview practice."""
    return command


@router.get("", response_model=Page[OrderResponse])
async def list_orders(
    service: ServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> Page[OrderResponse]:
    orders, total = await service.list_orders(offset, limit)
    return Page(
        items=[OrderResponse.from_domain(order) for order in orders],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: UUID, service: ServiceDep) -> OrderResponse:
    return OrderResponse.from_domain(await service.get_order(order_id))


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: UUID,
    command: UpdateOrderStatusRequest,
    service: ServiceDep,
    expected_version: Annotated[int, Header(alias="X-Expected-Version", ge=1)],
) -> OrderResponse:
    order = await service.change_status(order_id, command.status, expected_version)
    return OrderResponse.from_domain(order)


@router.get("/{order_id}/summary", response_model=OrderSummaryResponse)
async def get_order_summary(
    order_id: UUID,
    service: ServiceDep,
) -> OrderSummaryResponse:
    return OrderSummaryResponse.from_domain(await service.build_summary(order_id))
