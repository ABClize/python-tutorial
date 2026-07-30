# 联合类型、TypeAdapter 与对象输入

联合类型表示一个值可以属于多种类型。判别联合根据固定标记选择模型。`TypeAdapter` 可以校验没有
`BaseModel` 外壳的任意类型，`RootModel` 为顶层列表等值定义模型，`from_attributes` 从对象属性
读取数据。

<!-- 对应源码：python/backend_interview/schemas.py、python/backend_interview/pydantic_patterns.py -->

## 普通联合的问题

假设支付方式有卡和钱包两种：

```python
class CardPayment(BaseModel):
    kind: Literal["card"]
    last_four: str


class WalletPayment(BaseModel):
    kind: Literal["wallet"]
    provider: Literal["alipay", "wechat"]
    account_id: str
```

直接使用 `CardPayment | WalletPayment` 时，Pydantic 需要尝试联合分支。分支越多、结构越相似，错误
信息越难理解。

## 判别联合按标记选择模型

把公共标记 `kind` 声明为 discriminator：

```python
from typing import Annotated, Literal

from pydantic import BaseModel, Field

PaymentMethod = Annotated[
    CardPayment | WalletPayment,
    Field(discriminator="kind"),
]


class CheckoutRequest(BaseModel):
    order_id: UUID
    payment: PaymentMethod
```

```python
request = CheckoutRequest.model_validate(
    {
        "order_id": (
            "9a02be38-13fe-459e-8629-12d451227bbc"
        ),
        "payment": {
            "kind": "wallet",
            "provider": "alipay",
            "account_id": "user-1",
        },
    }
)

print(type(request.payment).__name__)
print(request.payment.provider)
```

```text
WalletPayment
alipay
```

Pydantic 读取 `kind="wallet"` 后直接选择 `WalletPayment`。每个分支必须为判别字段使用唯一的 Literal
值，输入缺少 `kind` 或使用未知值都会产生明确错误。

仓库中的 `order_id` 是 UUID。合法 UUID 字符串可以被解析，`"order-1"` 不能通过。

## TypeAdapter 校验任意类型

不是所有数据都需要定义外层 `BaseModel`。校验一个整数列表可以直接使用：

```python
from pydantic import TypeAdapter

integer_list = TypeAdapter(list[int])
values = integer_list.validate_python(
    ["1", 2, 3]
)

print(values)
```

```text
[1, 2, 3]
```

常用方法包括：

- `validate_python()`；
- `validate_json()`；
- `dump_python()`；
- `dump_json()`；
- `json_schema()`。

TypeAdapter 会构建校验器和 Schema。反复使用时应复用同一个实例，不要在热路径中每次重建。

## 用 TypeAdapter 校验事件列表

仓库中的领域事件也使用判别联合：

```python
DomainEvent = Annotated[
    UserCreated | OrderPaid,
    Field(discriminator="kind"),
]

event_adapter = TypeAdapter(
    list[DomainEvent]
)


def parse_events(payload):
    return event_adapter.validate_python(payload)
```

示例输入：

```python
events = parse_events(
    [
        {
            "kind": "user.created",
            "user_id": 1,
            "email": "ada@example.com",
        },
        {
            "kind": "order.paid",
            "order_id": (
                "9a02be38-13fe-459e-8629-12d451227bbc"
            ),
            "amount": "59.90",
        },
    ]
)
```

列表中每项会根据 `kind` 分别创建 `UserCreated` 或 `OrderPaid`。

## RootModel 给顶层值一个模型名字

如果 JSON 顶层就是列表，可以使用：

```python
from pydantic import RootModel


class IntegerList(RootModel[list[int]]):
    pass


numbers = IntegerList.model_validate(
    ["1", 2, 3]
)
print(numbers.root)
```

```text
[1, 2, 3]
```

仓库中的 `EventBatch` 是 `RootModel[list[DomainEvent]]`。

TypeAdapter 与 RootModel 都能处理顶层列表：

- 只需要校验和序列化某个类型时，TypeAdapter 更轻；
- 需要一个明确模型名字、自定义方法或作为其他字段复用时，RootModel 更合适。

## 从普通对象的属性读取

默认模型通常从字典键读取。开启 `from_attributes=True` 后，可以读取对象属性：

```python
from pydantic import BaseModel, ConfigDict


class LegacyUser:
    def __init__(
        self,
        user_id: int,
        display_name: str,
    ):
        self.user_id = user_id
        self.display_name = display_name


class PublicUser(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    user_id: int
    display_name: str
```

```python
public = PublicUser.model_validate(
    LegacyUser(1, "Ada")
)
print(public.model_dump())
```

```text
{'user_id': 1, 'display_name': 'Ada'}
```

这是 Pydantic v2 从 ORM 或普通对象属性读取数据的方式。

## 自动读取还是显式映射

`from_attributes` 适合字段名和含义高度一致的简单对象。API 响应与领域对象差异较大时，显式转换更清楚：

```python
@classmethod
def from_domain(
    cls,
    order: Order,
) -> "OrderResponse":
    return cls.model_validate(
        {
            "id": order.id,
            "customer_email": order.customer_email,
            "items": order.items,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "version": order.version,
            "total": order.total,
        }
    )
```

显式映射可以重命名、计算和筛选字段，也不会要求领域对象为了 API 结构而改变。便利性与边界清晰度之间，
要根据模型差异选择。
