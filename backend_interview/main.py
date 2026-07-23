"""FastAPI application factory with lifespan, middleware, and exception mapping."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from contextvars import ContextVar
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from backend_interview.api import router
from backend_interview.config import Settings, get_settings
from backend_interview.exceptions import (
    BackendInterviewError,
    InsufficientInventoryError,
    InvalidStatusTransitionError,
    OptimisticLockError,
    OrderNotFoundError,
    ProductUnavailableError,
    UpstreamTimeoutError,
)
from backend_interview.gateways import (
    FakeCatalogGateway,
    FakeInventoryGateway,
    FakeRiskGateway,
)
from backend_interview.repository import InMemoryOrderRepository

request_id_context: ContextVar[str] = ContextVar("request_id", default="unknown")


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        repository = InMemoryOrderRepository()
        application.state.order_repository = repository
        application.state.catalog_gateway = FakeCatalogGateway()
        application.state.inventory_gateway = FakeInventoryGateway()
        application.state.risk_gateway = FakeRiskGateway()
        application.state.audit_log = []
        try:
            yield
        finally:
            await repository.close()

    application = FastAPI(
        title=resolved_settings.app_name,
        version="1.0.0",
        lifespan=lifespan,
    )
    application.state.settings = resolved_settings
    application.include_router(router)

    @application.middleware("http")
    async def request_context_middleware(
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid4().hex
        request.state.request_id = request_id
        token = request_id_context.set(request_id)
        started = perf_counter()
        try:
            response = await call_next(request)
        finally:
            request_id_context.reset(token)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{perf_counter() - started:.6f}"
        return response

    @application.exception_handler(BackendInterviewError)
    async def backend_error_handler(
        request: Request,
        exception: BackendInterviewError,
    ) -> JSONResponse:
        status_by_type: dict[type[BackendInterviewError], int] = {
            OrderNotFoundError: status.HTTP_404_NOT_FOUND,
            ProductUnavailableError: status.HTTP_409_CONFLICT,
            InsufficientInventoryError: status.HTTP_409_CONFLICT,
            InvalidStatusTransitionError: status.HTTP_409_CONFLICT,
            OptimisticLockError: status.HTTP_409_CONFLICT,
            UpstreamTimeoutError: status.HTTP_504_GATEWAY_TIMEOUT,
        }
        response_status = status_by_type.get(type(exception), status.HTTP_400_BAD_REQUEST)
        return JSONResponse(
            status_code=response_status,
            content={
                "error": {"code": exception.code, "message": str(exception)},
                "request_id": getattr(request.state, "request_id", "unknown"),
            },
        )

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exception: RequestValidationError,
    ) -> JSONResponse:
        errors = [
            {
                "location": list(error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exception.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "error": {"code": "request_validation_error", "details": errors},
                "request_id": getattr(request.state, "request_id", "unknown"),
            },
        )

    @application.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {
            "status": "ok",
            "environment": resolved_settings.environment,
        }

    return application


app = create_app()
