"""Shared fixtures for backend interview scenarios."""

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr

from backend_interview.config import Settings
from backend_interview.main import create_app


@pytest.fixture
def app() -> FastAPI:
    return create_app(
        Settings(
            environment="test",
            api_key=SecretStr("test-api-key"),
            request_timeout_seconds=0.1,
            max_concurrency=2,
        )
    )


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {
        "X-API-Key": "test-api-key",
        "Idempotency-Key": "test-order-0001",
    }


@pytest.fixture
def order_payload() -> dict[str, Any]:
    return {
        "customer_email": "learner@example.com",
        "items": [
            {"sku": "py-book", "quantity": 2},
            {"sku": "ASYNC-LAB", "quantity": 1},
        ],
    }
