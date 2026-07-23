"""HTTPX async tests with explicit ASGI lifespan handling."""

from typing import Any

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_async_client_calls_real_asgi_app(
    app: FastAPI,
    order_payload: dict[str, Any],
) -> None:
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            created = await client.post(
                "/orders",
                headers={
                    "X-API-Key": "test-api-key",
                    "Idempotency-Key": "async-order-001",
                },
                json=order_payload,
            )
            assert created.status_code == 201

            order_id = created.json()["order"]["id"]
            fetched = await client.get(
                f"/orders/{order_id}",
                headers={"X-API-Key": "test-api-key"},
            )

    assert fetched.status_code == 200
    assert fetched.json()["id"] == order_id
