"""FastAPI endpoint and dependency integration tests."""

from typing import Any
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend_interview.dependencies import require_api_key
from backend_interview.domain import Principal


def create_order(
    client: TestClient,
    headers: dict[str, str],
    payload: dict[str, Any],
) -> dict[str, Any]:
    response = client.post("/orders", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_health_has_request_context_headers(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "request-123"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "environment": "test"}
    assert response.headers["X-Request-ID"] == "request-123"
    assert float(response.headers["X-Process-Time"]) >= 0


def test_orders_require_authentication(
    client: TestClient,
    order_payload: dict[str, Any],
) -> None:
    response = client.post(
        "/orders",
        headers={"Idempotency-Key": "unauthorized-001"},
        json=order_payload,
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "无效的 API Key"


def test_create_order_normalizes_and_calculates_total(
    client: TestClient,
    auth_headers: dict[str, str],
    order_payload: dict[str, Any],
) -> None:
    body = create_order(client, auth_headers, order_payload)

    assert body["created"] is True
    assert body["order"]["items"][0]["sku"] == "PY-BOOK"
    assert body["order"]["items"][0]["subtotal"] == "119.80"
    assert body["order"]["total"] == "209.30"
    assert body["order"]["version"] == 1


def test_idempotency_returns_original_order(
    client: TestClient,
    auth_headers: dict[str, str],
    order_payload: dict[str, Any],
) -> None:
    first = create_order(client, auth_headers, order_payload)
    second = create_order(client, auth_headers, order_payload)

    assert first["order"]["id"] == second["order"]["id"]
    assert first["created"] is True
    assert second["created"] is False

    listed = client.get("/orders", headers={"X-API-Key": "test-api-key"}).json()
    assert listed["total"] == 1


def test_request_validation_returns_stable_error_shape(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/orders",
        headers=auth_headers,
        json={
            "customer_email": "not-an-email",
            "items": [
                {"sku": "PY-BOOK", "quantity": 1},
                {"sku": "py-book", "quantity": 2},
            ],
            "unexpected": True,
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "request_validation_error"
    assert body["request_id"]
    assert len(body["error"]["details"]) >= 2


def test_missing_order_maps_domain_error_to_http(
    client: TestClient,
) -> None:
    response = client.get(
        f"/orders/{uuid4()}",
        headers={"X-API-Key": "test-api-key", "X-Request-ID": "missing-1"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "order_not_found"
    assert response.json()["request_id"] == "missing-1"


def test_status_update_and_optimistic_lock_conflict(
    client: TestClient,
    auth_headers: dict[str, str],
    order_payload: dict[str, Any],
) -> None:
    created = create_order(client, auth_headers, order_payload)["order"]
    order_id = created["id"]

    confirmed = client.patch(
        f"/orders/{order_id}/status",
        headers={"X-API-Key": "test-api-key", "X-Expected-Version": "1"},
        json={"status": "confirmed"},
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "confirmed"
    assert confirmed.json()["version"] == 2

    stale = client.patch(
        f"/orders/{order_id}/status",
        headers={"X-API-Key": "test-api-key", "X-Expected-Version": "1"},
        json={"status": "cancelled"},
    )
    assert stale.status_code == 409
    assert stale.json()["error"]["code"] == "optimistic_lock_conflict"


def test_invalid_status_transition_returns_conflict(
    client: TestClient,
    auth_headers: dict[str, str],
    order_payload: dict[str, Any],
) -> None:
    order_id = create_order(client, auth_headers, order_payload)["order"]["id"]
    cancelled = client.patch(
        f"/orders/{order_id}/status",
        headers={"X-API-Key": "test-api-key", "X-Expected-Version": "1"},
        json={"status": "cancelled"},
    )
    assert cancelled.status_code == 200

    invalid = client.patch(
        f"/orders/{order_id}/status",
        headers={"X-API-Key": "test-api-key", "X-Expected-Version": "2"},
        json={"status": "confirmed"},
    )
    assert invalid.status_code == 409
    assert invalid.json()["error"]["code"] == "invalid_status_transition"


def test_summary_fans_out_to_catalog_and_risk(
    client: TestClient,
    auth_headers: dict[str, str],
    order_payload: dict[str, Any],
) -> None:
    order_id = create_order(client, auth_headers, order_payload)["order"]["id"]

    response = client.get(
        f"/orders/{order_id}/summary",
        headers={"X-API-Key": "test-api-key"},
    )

    assert response.status_code == 200
    assert response.json()["risk_level"] == "low"
    assert response.json()["product_labels"]["PY-BOOK"] == "Python Interview Book"


def test_discriminated_payment_union(
    client: TestClient,
) -> None:
    valid = client.post(
        "/orders/payment/validate",
        headers={"X-API-Key": "test-api-key"},
        json={
            "order_id": str(uuid4()),
            "payment": {"kind": "wallet", "provider": "alipay", "account_id": "abc123"},
        },
    )
    assert valid.status_code == 200
    assert valid.json()["payment"]["kind"] == "wallet"

    invalid = client.post(
        "/orders/payment/validate",
        headers={"X-API-Key": "test-api-key"},
        json={
            "order_id": str(uuid4()),
            "payment": {"kind": "card", "last_four": "0000"},
        },
    )
    assert invalid.status_code == 422


def test_bulk_creation_preserves_input_order(
    client: TestClient,
) -> None:
    response = client.post(
        "/orders/bulk",
        headers={"X-API-Key": "test-api-key"},
        json={
            "entries": [
                {
                    "idempotency_key": "bulk-order-0001",
                    "order": {
                        "customer_email": "first@example.com",
                        "items": [{"sku": "PY-BOOK", "quantity": 1}],
                    },
                },
                {
                    "idempotency_key": "bulk-order-0002",
                    "order": {
                        "customer_email": "second@example.com",
                        "items": [{"sku": "API-COURSE", "quantity": 1}],
                    },
                },
            ]
        },
    )

    assert response.status_code == 200
    assert [entry["order"]["customer_email"] for entry in response.json()] == [
        "first@example.com",
        "second@example.com",
    ]


def test_dependency_override_bypasses_real_authentication(
    app: FastAPI,
    order_payload: dict[str, Any],
) -> None:
    async def fake_principal() -> Principal:
        return Principal("test-user", frozenset({"orders:write"}))

    app.dependency_overrides[require_api_key] = fake_principal
    try:
        with TestClient(app) as override_client:
            response = override_client.post(
                "/orders",
                headers={"Idempotency-Key": "override-order-1"},
                json=order_payload,
            )
        assert response.status_code == 201
    finally:
        app.dependency_overrides.clear()


def test_yield_dependency_runs_cleanup(
    app: FastAPI,
    client: TestClient,
) -> None:
    response = client.get("/orders", headers={"X-API-Key": "test-api-key"})
    assert response.status_code == 200
    assert app.state.audit_log[-2:] == [
        ("start", "/orders"),
        ("finish", "/orders"),
    ]
