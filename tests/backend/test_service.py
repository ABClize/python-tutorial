"""Service and repository tests without the HTTP layer."""

import asyncio
from decimal import Decimal

import pytest

from backend_interview.domain import OrderStatus
from backend_interview.exceptions import (
    InsufficientInventoryError,
    OptimisticLockError,
    ProductUnavailableError,
    UpstreamTimeoutError,
)
from backend_interview.gateways import (
    FakeCatalogGateway,
    FakeInventoryGateway,
    FakeRiskGateway,
)
from backend_interview.repository import InMemoryOrderRepository
from backend_interview.schemas import CreateOrderRequest
from backend_interview.service import OrderService


def command(email: str = "learner@example.com", sku: str = "PY-BOOK") -> CreateOrderRequest:
    return CreateOrderRequest.model_validate(
        {
            "customer_email": email,
            "items": [{"sku": sku, "quantity": 1}],
        }
    )


def make_service(
    *,
    repository: InMemoryOrderRepository | None = None,
    catalog: FakeCatalogGateway | None = None,
    inventory: FakeInventoryGateway | None = None,
    risk: FakeRiskGateway | None = None,
    timeout: float = 0.1,
    max_concurrency: int = 2,
) -> tuple[OrderService, InMemoryOrderRepository, FakeInventoryGateway]:
    actual_repository = repository or InMemoryOrderRepository()
    actual_inventory = inventory or FakeInventoryGateway()
    return (
        OrderService(
            repository=actual_repository,
            catalog=catalog or FakeCatalogGateway(),
            inventory=actual_inventory,
            risk=risk or FakeRiskGateway(),
            timeout_seconds=timeout,
            max_concurrency=max_concurrency,
        ),
        actual_repository,
        actual_inventory,
    )


@pytest.mark.asyncio
async def test_concurrent_idempotent_requests_create_once() -> None:
    service, repository, _ = make_service()

    results = await asyncio.gather(
        *(service.create_order(command(), "same-key-0001") for _ in range(10))
    )

    assert len({result.order.id for result in results}) == 1
    assert sum(result.created for result in results) == 1
    assert await repository.count() == 1


@pytest.mark.asyncio
async def test_unknown_product_is_unwrapped_from_task_group() -> None:
    service, _, _ = make_service()

    with pytest.raises(ProductUnavailableError):
        await service.create_order(command(sku="NOT-FOUND"), "unknown-0001")


@pytest.mark.asyncio
async def test_insufficient_inventory_is_domain_error() -> None:
    inventory = FakeInventoryGateway(stock={"PY-BOOK": 0})
    service, _, _ = make_service(inventory=inventory)

    with pytest.raises(InsufficientInventoryError):
        await service.create_order(command(), "stock-0001")


@pytest.mark.asyncio
async def test_upstream_timeout_maps_builtin_timeout() -> None:
    service, _, _ = make_service(
        catalog=FakeCatalogGateway(latency=0.05),
        timeout=0.001,
    )

    with pytest.raises(UpstreamTimeoutError):
        await service.create_order(command(), "timeout-0001")


@pytest.mark.asyncio
async def test_status_change_uses_optimistic_version() -> None:
    service, _, _ = make_service()
    created = await service.create_order(command(), "version-0001")

    confirmed = await service.change_status(
        created.order.id,
        OrderStatus.CONFIRMED,
        expected_version=1,
    )
    assert confirmed.version == 2

    with pytest.raises(OptimisticLockError):
        await service.change_status(
            created.order.id,
            OrderStatus.CANCELLED,
            expected_version=1,
        )


@pytest.mark.asyncio
async def test_summary_runs_risk_and_catalog_calls() -> None:
    service, _, _ = make_service()
    created = await service.create_order(command(email="risk@example.com"), "risk-0001")

    summary = await service.build_summary(created.order.id)

    assert summary.risk_level == "high"
    assert summary.product_labels == {"PY-BOOK": "Python Interview Book"}
    assert summary.order.total == Decimal("59.90")


@pytest.mark.asyncio
async def test_bulk_create_honors_concurrency_limit() -> None:
    inventory = FakeInventoryGateway(latency=0.005)
    service, _, _ = make_service(
        inventory=inventory,
        max_concurrency=2,
        timeout=1,
    )
    commands = [(command(), f"bulk-key-{index:04d}") for index in range(8)]

    results = await service.bulk_create(commands)

    assert len(results) == 8
    assert inventory.max_active_calls <= 2


@pytest.mark.asyncio
async def test_repository_rejects_use_after_shutdown() -> None:
    repository = InMemoryOrderRepository()
    await repository.close()

    with pytest.raises(RuntimeError, match="已经关闭"):
        await repository.count()
