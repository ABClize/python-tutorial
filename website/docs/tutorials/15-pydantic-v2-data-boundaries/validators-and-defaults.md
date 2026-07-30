# 字段校验器、模型校验器与默认值

validator 是自定义校验函数。字段校验器处理一个字段，模型校验器可以比较多个字段。长度、范围和
正则等通用规则优先写在 `Field` 中。

validator 应快速、确定，只依赖当前输入。数据库查询和网络请求应放在业务服务中。

<p class="source-note">对应源码：<code>python/backend_interview/schemas.py</code>、<code>python/backend_interview/pydantic_patterns.py</code></p>

## 字段校验器处理一个字段

订单中同一 SKU 只能出现一次：

```python
from pydantic import BaseModel, field_validator


class CreateOrderRequest(BaseModel):
    customer_email: str
    items: list[CreateOrderItem]

    @field_validator("items")
    @classmethod
    def require_unique_skus(
        cls,
        items: list[CreateOrderItem],
    ) -> list[CreateOrderItem]:
        skus = [item.sku for item in items]
        if len(skus) != len(set(skus)):
            raise ValueError("同一个 SKU 只能出现一次")
        return items
```

这里使用默认的 after 模式。`items` 已是 `CreateOrderItem` 列表，每个 SKU 也完成了去空格和大写
规范化。因此 `"py-book"` 和 `"PY-BOOK"` 会被判定为重复。

validator 必须返回校验后的值。忘记 `return` 会让字段值变成 `None`，随后出现难以理解的问题。

## before 与 after 的区别

项目的注册模型允许标签使用逗号分隔字符串：

```python
@field_validator("tags", mode="before")
@classmethod
def parse_comma_separated_tags(cls, value):
    if isinstance(value, str):
        return [
            part.strip()
            for part in value.split(",")
            if part.strip()
        ]
    return value
```

before validator 得到原始输入，适合把一种明确的外部表示转换成模型期望的结构。

第二个 validator 使用默认 after 模式：

```python
@field_validator("tags")
@classmethod
def normalize_tags(
    cls,
    tags: list[str],
) -> list[str]:
    return list(
        dict.fromkeys(
            tag.casefold() for tag in tags
        )
    )
```

此时 `tags` 已经是 `list[str]`，函数只负责统一大小写并按首次出现顺序去重。

```text
"Python, API, python"
        ↓ before：拆成列表
["Python", "API", "python"]
        ↓ after：规范化和去重
["python", "api"]
```

这张流程图说明 before validator 处理原始字符串，after validator 处理已经解析好的列表。

## Field 能表达的规则不要改写成 validator

数量大于 0 应写成：

```python
quantity: int = Field(gt=0)
```

而不是手写：

```python
@field_validator("quantity")
@classmethod
def validate_quantity(cls, value: int) -> int:
    if value <= 0:
        raise ValueError("数量错误")
    return value
```

`Field` 会生成更准确的错误类型和 JSON Schema，也更容易被 FastAPI 文档识别。validator 留给通用约束
表达不了的规则。

## 模型校验器比较多个字段

密码与重复密码要一致，单独看任一字段都无法判断：

```python
from typing import Self

from pydantic import BaseModel, model_validator


class RegistrationRequest(BaseModel):
    password: str
    password_repeat: str

    @model_validator(mode="after")
    def passwords_must_match(self) -> Self:
        if self.password != self.password_repeat:
            raise ValueError("两次密码不一致")
        return self
```

after model validator 得到字段校验已通过的模型实例，也必须返回模型。

项目中的支付请求还会拒绝测试卡号：

```python
@model_validator(mode="after")
def require_supported_payment(self) -> Self:
    if (
        isinstance(self.payment, CardPayment)
        and self.payment.last_four == "0000"
    ):
        raise ValueError("测试卡号 0000 不允许支付")
    return self
```

这条规则只依赖当前请求内容，所以可以放在模型中。

## validator 不应访问外部系统

下面这些检查不适合 validator：

- 邮箱是否已注册；
- 商品是否存在；
- 库存是否足够；
- 用户是否有权限；
- 数据库唯一索引是否冲突。

把网络或数据库调用放入 validator 会造成：

- 模型构造不再是快速、确定的同步过程；
- 相同模型难以在 CLI、测试和后台任务中复用；
- 错误重试、超时和事务边界没有合适位置；
- 校验顺序变化可能意外触发额外 I/O。

模型负责输入内部能判断的关系，外部状态由服务层和仓储处理。

## 固定默认值

不可变默认值可以直接声明：

```python
class Job(BaseModel):
    status: str = "pending"
    priority: int = 0
```

调用者省略字段时使用默认值；显式传入错误类型时仍会校验。

需要注意：默认值是否执行与外部输入完全相同的校验流程，取决于模型配置。复杂默认值若必须验证，可
开启相应配置或让工厂直接返回正确类型。

## `default_factory` 为每个实例创建新值

列表、字典和动态值应通过工厂创建：

```python
from pydantic import BaseModel, Field


class RegistrationRequest(BaseModel):
    tags: list[str] = Field(default_factory=list)
```

```python
first = RegistrationRequest()
second = RegistrationRequest()

print(first.tags is second.tags)
```

```text
False
```

每次模型创建都会调用 `list`。动态默认值也可以使用：

```python
from datetime import UTC, datetime
from uuid import UUID, uuid4


class Event(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
```

不要写 `occurred_at: datetime = datetime.now(UTC)`，因为这个表达式在类定义时只执行一次，后续实例
可能共享同一个旧时间。

## 错误应该放在哪一层

可以按规则所需信息判断：

| 规则 | 合适位置 |
| --- | --- |
| 数量范围、字符串长度 | `Field` |
| 单字段规范化 | `BeforeValidator` 或 field validator |
| 当前输入中的字段关系 | model validator |
| 商品、库存、权限 | 服务或网关 |
| 唯一性、版本冲突 | 仓储和数据库 |

Pydantic 只处理当前输入能判断的通用规则。需要外部状态或并发保证的规则应放到业务服务或仓储。
