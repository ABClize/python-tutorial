"""Pydantic v2 patterns beyond basic request models."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated, Any, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    RootModel,
    SecretStr,
    TypeAdapter,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
    validate_call,
)


class RegistrationRequest(BaseModel):
    """Field and model validators with safe serialization."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: EmailStr
    password: SecretStr = Field(min_length=8)
    password_repeat: SecretStr = Field(min_length=8, exclude=True)
    tags: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("tags", mode="before")
    @classmethod
    def parse_comma_separated_tags(cls, value: Any) -> Any:
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str]) -> list[str]:
        return list(dict.fromkeys(tag.casefold() for tag in tags))

    @model_validator(mode="after")
    def passwords_must_match(self) -> Self:
        if self.password.get_secret_value() != self.password_repeat.get_secret_value():
            raise ValueError("两次密码不一致")
        return self

    @computed_field
    def email_domain(self) -> str:
        return str(self.email).partition("@")[2]


class UserCreated(BaseModel):
    kind: Literal["user.created"]
    user_id: int
    occurred_at: datetime

    @field_serializer("occurred_at")
    def serialize_datetime(self, value: datetime) -> str:
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


class OrderPaid(BaseModel):
    kind: Literal["order.paid"]
    order_id: str
    amount: Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]


DomainEvent = Annotated[UserCreated | OrderPaid, Field(discriminator="kind")]


class EventBatch(RootModel[list[DomainEvent]]):
    """RootModel represents a top-level list instead of an object wrapper."""


event_adapter = TypeAdapter(list[DomainEvent])


def parse_events(payload: list[dict[str, object]]) -> list[DomainEvent]:
    return event_adapter.validate_python(payload)


class LegacyUser:
    def __init__(self, user_id: int, display_name: str) -> None:
        self.user_id = user_id
        self.display_name = display_name


class PublicUser(BaseModel):
    """``from_attributes`` replaces Pydantic v1's ORM mode."""

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    display_name: str


class StrictMetric(BaseModel):
    """Strict mode rejects implicit string-to-number coercion."""

    model_config = ConfigDict(strict=True, extra="forbid")

    name: str
    value: float


@validate_call(config=ConfigDict(strict=True))
def calculate_discount(
    amount: Annotated[Decimal, Field(gt=0)],
    rate: Annotated[Decimal, Field(ge=0, le=1)],
) -> Decimal:
    return (amount * rate).quantize(Decimal("0.01"))


def demo() -> None:
    registration = RegistrationRequest.model_validate(
        {
            "email": " learner@example.com ",
            "password": "correct-horse",
            "password_repeat": "correct-horse",
            "tags": "Python, API, python",
        }
    )
    dumped = registration.model_dump()
    assert dumped["tags"] == ["python", "api"]
    assert "password_repeat" not in dumped
    assert registration.email_domain == "example.com"

    events = parse_events(
        [
            {
                "kind": "user.created",
                "user_id": 7,
                "occurred_at": "2026-01-01T00:00:00Z",
            },
            {"kind": "order.paid", "order_id": "order-1", "amount": "99.90"},
        ]
    )
    assert isinstance(events[0], UserCreated)
    assert isinstance(events[1], OrderPaid)

    public = PublicUser.model_validate(LegacyUser(1, "Ada"))
    assert public.model_dump() == {"user_id": 1, "display_name": "Ada"}
    assert calculate_discount(Decimal("100"), Decimal("0.15")) == Decimal("15.00")


if __name__ == "__main__":
    demo()
    print("Pydantic v2 项目模式检查通过")
