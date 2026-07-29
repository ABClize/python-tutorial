"""Application service layer: orchestration, concurrency, and business rules."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from uuid import UUID

from backend_interview.domain import Order, OrderItem, OrderStatus, OrderSummary
from backend_interview.exceptions import (
    BackendInterviewError,
    OrderNotFoundError,
    UpstreamTimeoutError,
)
from backend_interview.gateways import CatalogGateway, InventoryGateway, RiskGateway
from backend_interview.repository import OrderRepository
from backend_interview.schemas import CreateOrderRequest


@dataclass(frozen=True, slots=True)
class CreateOrderResult:
    """Return value for create operations.

    ``created`` mirrors the HTTP/API contract: ``False`` means the request was
    a safe idempotent replay and the existing order is returned.
    """

    order: Order
    created: bool


class OrderService:
    """Use-case layer that coordinates repositories and external gateways.

    The service deliberately does not import FastAPI classes. That keeps
    business orchestration testable without an ASGI client and makes it easier
    to reuse the same use cases from a CLI, worker, or message consumer.
    """

    def __init__(
        self,
        repository: OrderRepository,
        catalog: CatalogGateway,
        inventory: InventoryGateway,
        risk: RiskGateway,
        *,
        timeout_seconds: float,
        max_concurrency: int,
    ) -> None:
        self.repository = repository
        self.catalog = catalog
        self.inventory = inventory
        self.risk = risk
        self.timeout_seconds = timeout_seconds
        self._bulk_semaphore = asyncio.Semaphore(max_concurrency)

    async def create_order(
        self,
        command: CreateOrderRequest,
        idempotency_key: str,
    ) -> CreateOrderResult:
        # Fast path for retries that arrive after the first request completed.
        # The repository still repeats this check atomically to handle races.
        existing = await self.repository.find_by_idempotency_key(idempotency_key)
        if existing is not None:
            return CreateOrderResult(existing, created=False)

        product_tasks: dict[str, asyncio.Task] = {}
        try:
            async with asyncio.timeout(self.timeout_seconds):
                try:
                    # TaskGroup gives structured concurrency: if catalog or
                    # inventory fails, sibling tasks are cancelled as a group.
                    async with asyncio.TaskGroup() as task_group:
                        for item in command.items:
                            product_tasks[item.sku] = task_group.create_task(
                                self.catalog.get_product(item.sku),
                                name=f"catalog:{item.sku}",
                            )
                            task_group.create_task(
                                self.inventory.ensure_available(item.sku, item.quantity),
                                name=f"inventory:{item.sku}",
                            )
                except* BackendInterviewError as error_group:
                    raise error_group.exceptions[0] from None
        except TimeoutError:
            raise UpstreamTimeoutError() from None

        items = tuple(
            OrderItem(
                sku=item.sku,
                product_name=product_tasks[item.sku].result().name,
                quantity=item.quantity,
                unit_price=product_tasks[item.sku].result().price,
            )
            for item in command.items
        )
        # Pydantic validates the boundary request; the domain object owns
        # business defaults such as initial status, UUID, timestamp, and version.
        candidate = Order.create(str(command.customer_email), items)
        saved, created = await self.repository.create(candidate, idempotency_key)
        return CreateOrderResult(saved, created)

    async def get_order(self, order_id: UUID) -> Order:
        order = await self.repository.get(order_id)
        if order is None:
            raise OrderNotFoundError(str(order_id))
        return order

    async def list_orders(self, offset: int, limit: int) -> tuple[list[Order], int]:
        # Listing and counting are independent reads, so they can run together.
        orders, total = await asyncio.gather(
            self.repository.list(offset, limit),
            self.repository.count(),
        )
        return orders, total

    async def change_status(
        self,
        order_id: UUID,
        target: OrderStatus,
        expected_version: int,
    ) -> Order:
        order = await self.get_order(order_id)
        changed = order.transition_to(target)
        if changed is order:
            return order
        return await self.repository.save(changed, expected_version)

    async def build_summary(self, order_id: UUID) -> OrderSummary:
        order = await self.get_order(order_id)
        product_tasks: dict[str, asyncio.Task] = {}
        risk_task: asyncio.Task | None = None

        try:
            async with asyncio.timeout(self.timeout_seconds):
                try:
                    async with asyncio.TaskGroup() as task_group:
                        risk_task = task_group.create_task(
                            self.risk.assess(order),
                            name=f"risk:{order.id}",
                        )
                        for item in order.items:
                            product_tasks[item.sku] = task_group.create_task(
                                self.catalog.get_product(item.sku),
                                name=f"catalog-label:{item.sku}",
                            )
                except* BackendInterviewError as error_group:
                    raise error_group.exceptions[0] from None
        except TimeoutError:
            raise UpstreamTimeoutError() from None

        if risk_task is None:
            raise RuntimeError("风险任务未创建")
        labels = {sku: task.result().name for sku, task in product_tasks.items()}
        return OrderSummary(
            order=order,
            risk_level=risk_task.result(),
            product_labels=labels,
        )

    async def bulk_create(
        self,
        commands: list[tuple[CreateOrderRequest, str]],
    ) -> list[CreateOrderResult]:
        async def create_bounded(
            command: CreateOrderRequest,
            key: str,
        ) -> CreateOrderResult:
            # Bound fan-out from one bulk request so a single client cannot
            # create unbounded upstream catalog/inventory pressure.
            async with self._bulk_semaphore:
                return await self.create_order(command, key)

        return list(
            await asyncio.gather(*(create_bounded(command, key) for command, key in commands))
        )
