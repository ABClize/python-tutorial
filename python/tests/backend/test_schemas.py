"""Pydantic v2 validation and serialization tests."""

from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend_interview.pydantic_patterns import (
    EventBatch,
    PublicUser,
    RegistrationRequest,
    StrictMetric,
    UserCreated,
    calculate_discount,
    parse_events,
)
from backend_interview.schemas import CheckoutRequest, CreateOrderRequest


def test_order_schema_normalizes_sku_and_email() -> None:
    command = CreateOrderRequest.model_validate(
        {
            "customer_email": "learner@example.com",
            "items": [{"sku": " py-book ", "quantity": 2}],
        }
    )

    assert command.items[0].sku == "PY-BOOK"
    assert str(command.customer_email) == "learner@example.com"


@pytest.mark.parametrize(
    "payload",
    [
        {
            "customer_email": "invalid",
            "items": [{"sku": "PY-BOOK", "quantity": 1}],
        },
        {
            "customer_email": "ok@example.com",
            "items": [{"sku": "??", "quantity": 1}],
        },
        {
            "customer_email": "ok@example.com",
            "items": [{"sku": "PY-BOOK", "quantity": 0}],
        },
        {
            "customer_email": "ok@example.com",
            "items": [
                {"sku": "PY-BOOK", "quantity": 1},
                {"sku": "py-book", "quantity": 2},
            ],
        },
    ],
)
def test_order_schema_rejects_invalid_boundaries(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        CreateOrderRequest.model_validate(payload)


def test_registration_model_validates_across_fields_and_hides_repeat() -> None:
    registration = RegistrationRequest.model_validate(
        {
            "email": "user@example.com",
            "password": "long-password",
            "password_repeat": "long-password",
            "tags": "Python,FastAPI,python",
        }
    )

    assert registration.tags == ["python", "fastapi"]
    assert registration.email_domain == "example.com"
    dumped = registration.model_dump()
    assert "password_repeat" not in dumped

    with pytest.raises(ValidationError, match="两次密码不一致"):
        RegistrationRequest.model_validate(
            {
                "email": "user@example.com",
                "password": "long-password",
                "password_repeat": "other-password",
            }
        )


def test_discriminated_union_reports_unknown_kind() -> None:
    with pytest.raises(ValidationError) as error:
        CheckoutRequest.model_validate(
            {
                "order_id": "9b4d61d8-f460-43ef-a734-23ba4a37c486",
                "payment": {"kind": "cash"},
            }
        )

    assert error.value.errors()[0]["type"] == "union_tag_invalid"


def test_type_adapter_and_root_model_parse_events() -> None:
    payload = [
        {
            "kind": "user.created",
            "user_id": 1,
            "occurred_at": "2026-01-01T00:00:00Z",
        },
        {"kind": "order.paid", "order_id": "o-1", "amount": "10.50"},
    ]

    events = parse_events(payload)
    batch = EventBatch.model_validate(payload)

    assert isinstance(events[0], UserCreated)
    assert isinstance(events[0].occurred_at, datetime)
    assert batch.model_dump(mode="json")[1]["amount"] == "10.50"


def test_from_attributes_reads_legacy_object() -> None:
    class Legacy:
        user_id = 42
        display_name = "Grace"

    user = PublicUser.model_validate(Legacy())
    assert user.model_dump() == {"user_id": 42, "display_name": "Grace"}


def test_strict_model_rejects_numeric_string() -> None:
    with pytest.raises(ValidationError):
        StrictMetric.model_validate({"name": "latency", "value": "1.25"})

    metric = StrictMetric.model_validate({"name": "latency", "value": 1.25})
    assert metric.value == 1.25


def test_validate_call_checks_function_boundaries() -> None:
    assert calculate_discount(Decimal("100"), Decimal("0.2")) == Decimal("20.00")
    with pytest.raises(ValidationError):
        calculate_discount("100", "0.2")  # type: ignore[arg-type]
