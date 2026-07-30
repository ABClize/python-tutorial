# 序列化、配置读取与领域模型边界

序列化是把 Pydantic 模型转换成字典或 JSON。`BaseSettings` 用相同的校验机制读取环境变量。领域
对象则保存业务状态和业务规则，不必承担 HTTP 字段别名或 JSON 格式。

输入时执行校验，输出时执行序列化。环境变量本质上也是外部字符串，同样需要解析和范围检查。

<!-- 对应源码：python/backend_interview/schemas.py、python/backend_interview/pydantic_patterns.py、python/backend_interview/config.py -->

## 计算字段进入输出

`computed_field` 可以把由其他字段算出的属性加入序列化结果：

```python
from decimal import Decimal

from pydantic import BaseModel, computed_field


class OrderLine(BaseModel):
    quantity: int
    unit_price: Decimal

    @computed_field
    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.unit_price
```

```python
line = OrderLine(
    quantity=2,
    unit_price=Decimal("59.90"),
)
print(line.model_dump())
```

```text
{
  'quantity': 2,
  'unit_price': Decimal('59.90'),
  'subtotal': Decimal('119.80')
}
```

调用方不用传 `subtotal`，它由模型中的可靠输入计算。仓库中的 `OrderItemResponse.subtotal` 和
`RegistrationRequest.email_domain` 都采用这种方式。

## 字段序列化器控制输出形式

项目把事件时间统一输出为 UTC，并用 `Z` 表示零时区：

```python
@field_serializer("occurred_at")
def serialize_datetime(
    self,
    value: datetime,
) -> str:
    return (
        value.astimezone(UTC)
        .isoformat()
        .replace("+00:00", "Z")
    )
```

方向要分清：

- validator：外部输入怎样变成模型值；
- serializer：模型值怎样变成输出。

不要为了控制 JSON 输出而在 validator 中提前把 `datetime` 永久改回字符串。

## 三种导出目标

下面分别导出 Python 字典、JSON 兼容字典和 JSON 字符串：

```python
python_data = model.model_dump()
json_ready = model.model_dump(mode="json")
json_text = model.model_dump_json()
```

| 方法 | 结果 |
| --- | --- |
| `model_dump()` | Python 字典，可保留 Decimal、UUID、datetime |
| `model_dump(mode="json")` | Python 字典，但值可直接编码为 JSON |
| `model_dump_json()` | JSON 字符串 |

把模型交给另一个 Python 函数时通常使用普通字典；写入 JSON 列或发送 HTTP 时需要 JSON 兼容形式。

## `SecretStr` 只遮蔽展示

下面使用 `SecretStr`，避免密码在日志和普通输出中直接显示：

```python
from pydantic import SecretStr

password = SecretStr("correct-horse")

print(password)
print(repr(password))
print(password.get_secret_value())
```

```text
**********
SecretStr('**********')
correct-horse
```

明文必须通过 `get_secret_value()` 显式取得。这能减少日志和调试输出中的意外泄露，但不能替代：

- 密码哈希；
- 传输和静态加密；
- Secret Manager；
- 文件权限和日志访问控制。

仓库还把 `password_repeat` 标记为 `exclude=True`，让它不进入常规导出。排除输出不等于从内存中销毁
值。

## `validate_call` 校验函数边界

公共函数也可以按类型标注执行运行时校验：

```python
from decimal import Decimal
from typing import Annotated

from pydantic import (
    ConfigDict,
    Field,
    validate_call,
)


@validate_call(config=ConfigDict(strict=True))
def calculate_discount(
    amount: Annotated[Decimal, Field(gt=0)],
    rate: Annotated[
        Decimal,
        Field(ge=0, le=1),
    ],
) -> Decimal:
    return (amount * rate).quantize(
        Decimal("0.01")
    )
```

```python
print(
    calculate_discount(
        Decimal("100"),
        Decimal("0.15"),
    )
)
```

```text
15.00
```

它适合确实需要保护的公共调用边界。每次调用都有校验成本，内部私有函数若只接收可信模型，不需要机械
装饰。

## BaseSettings 读取环境变量

Pydantic v2 把设置管理放在独立包 `pydantic-settings`：

```python
from pydantic import Field, SecretStr
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="INTERVIEW_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "development"
    api_key: SecretStr = SecretStr(
        "development-only-key"
    )
    request_timeout_seconds: float = Field(
        default=0.25,
        gt=0,
        le=30,
    )
    max_concurrency: int = Field(
        default=4,
        ge=1,
        le=100,
    )
```

Shell 中设置：

```bash
export INTERVIEW_MAX_CONCURRENCY=8
export INTERVIEW_REQUEST_TIMEOUT_SECONDS=1.5
```

创建 `Settings()` 时，字符串环境变量会被解析并检查范围。`env_prefix` 决定变量名前缀，`env_file`
允许本地读取 `.env`。

项目的 `get_settings()` 使用 `@lru_cache`，让同一进程只解析一次。测试既可以把自定义 `Settings`
传给 `create_app()`，也可以在改变环境变量后清理缓存。

`.env` 仍不应提交真实密钥。`SecretStr` 只改变展示，不会加密环境变量或文件。

## Pydantic 模型与领域对象各管什么

项目中的职责分布如下：

| 对象 | 负责 |
| --- | --- |
| `CreateOrderRequest` | 邮箱、SKU、数量、重复 SKU |
| `Order.transition_to()` | 订单状态能否转换 |
| `OrderService` | 协调商品、库存与仓储 |
| `InMemoryOrderRepository` | 幂等创建和版本冲突 |
| `OrderResponse` | API 允许公开的输出 |

Pydantic 模型校验成功，不表示一次业务操作必然可以执行。库存和权限会随时间变化，唯一约束还涉及并发，
这些规则不能只靠创建模型解决。

## Pydantic v1 到 v2 的常见名称

| v1 | v2 |
| --- | --- |
| `parse_obj()` | `model_validate()` |
| `parse_raw()` | `model_validate_json()` |
| `dict()` | `model_dump()` |
| `json()` | `model_dump_json()` |
| `schema()` | `model_json_schema()` |
| `class Config` | `model_config = ConfigDict(...)` |
| `@validator` | `@field_validator` |
| `@root_validator` | `@model_validator` |
| `orm_mode = True` | `from_attributes=True` |
| `pydantic.BaseSettings` | `pydantic_settings.BaseSettings` |

迁移不能只批量替换名称。validator 模式、严格转换、配置键和序列化行为也要按照 v2 的实际行为重新
测试。

## Pydantic 数据处理检查清单

- 类型标注本身不会自动校验普通 Python 对象；
- 默认模式会转换部分输入，严格边界需显式配置；
- Field 能表达的约束优先使用 Field；
- before validator 处理原始输入，after validator 处理已解析值；
- validator 不做数据库或网络 I/O；
- 判别联合的分支需要唯一 Literal；
- `model_dump()` 不是 JSON 文本；
- `SecretStr` 不是加密；
- Pydantic 不替代领域规则、权限和持久化约束。
