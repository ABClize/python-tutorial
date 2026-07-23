"""FastAPI dependency graph, authentication, and yield cleanup."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated, cast

from fastapi import Depends, Header, HTTPException, Request, status

from backend_interview.config import Settings
from backend_interview.domain import Principal
from backend_interview.repository import OrderRepository
from backend_interview.service import OrderService


def get_app_settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)


def get_repository(request: Request) -> OrderRepository:
    return cast(OrderRepository, request.app.state.order_repository)


SettingsDep = Annotated[Settings, Depends(get_app_settings)]
RepositoryDep = Annotated[OrderRepository, Depends(get_repository)]


def get_order_service(
    request: Request,
    settings: SettingsDep,
    repository: RepositoryDep,
) -> OrderService:
    return OrderService(
        repository=repository,
        catalog=request.app.state.catalog_gateway,
        inventory=request.app.state.inventory_gateway,
        risk=request.app.state.risk_gateway,
        timeout_seconds=settings.request_timeout_seconds,
        max_concurrency=settings.max_concurrency,
    )


ServiceDep = Annotated[OrderService, Depends(get_order_service)]


async def require_api_key(
    settings: SettingsDep,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> Principal:
    """Authentication dependency; production systems should use constant-time checks."""
    if x_api_key != settings.api_key.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return Principal(subject="interview-user", roles=frozenset({"orders:read", "orders:write"}))


async def audit_request(request: Request) -> AsyncIterator[None]:
    """A ``yield`` dependency demonstrates setup and guaranteed cleanup."""
    path = request.url.path
    request.app.state.audit_log.append(("start", path))
    try:
        yield
    finally:
        request.app.state.audit_log.append(("finish", path))
