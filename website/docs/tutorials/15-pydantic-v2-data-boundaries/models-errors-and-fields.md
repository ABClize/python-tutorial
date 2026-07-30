# 模型、校验错误与字段约束

Python 类型标注通常只帮助编辑器和静态检查器，并不会在运行时自动拒绝错误数据。Pydantic 模型会真正
读取输入、转换允许的类型，并在不符合约束时给出结构化错误。

<p class="source-note">对应源码：<code>python/backend_interview/schemas.py</code></p>

> 运行直接导入 `backend_interview` 的例子前，请先在仓库根目录执行 `cd python`。

## 定义第一个模型

继承 `BaseModel`，再用类型标注声明字段：

```python
from pydantic import BaseModel


class OrderItem(BaseModel):
    sku: str
    quantity: int
```

模型可以直接通过关键字参数创建，也可以显式调用 `model_validate()`：

```python
item = OrderItem.model_validate(
    {
        "sku": "PY-BOOK",
        "quantity": "2",
    }
)

print(item)
print(type(item.quantity))
```

输出：

```text
sku='PY-BOOK' quantity=2
<class 'int'>
```

输入中的 `"2"` 是字符串，模型中的 `quantity` 已经是整数。Pydantic 默认允许一部分明确的类型转换，
但转换有边界，例如 `"many"` 无法变成整数。

## 校验与导出的常用入口

| API | 输入或输出 |
| --- | --- |
| `Model.model_validate(data)` | 校验字典、模型或允许的 Python 对象 |
| `Model.model_validate_json(text)` | 解析并校验 JSON 字符串或 bytes |
| `model.model_dump()` | 导出包含 Python 对象的字典 |
| `model.model_dump(mode="json")` | 导出只含 JSON 兼容值的 Python 数据 |
| `model.model_dump_json()` | 导出 JSON 文本 |
| `Model.model_json_schema()` | 生成 JSON Schema |

```python
print(item.model_dump())
print(item.model_dump_json())
```

```text
{'sku': 'PY-BOOK', 'quantity': 2}
{"sku":"PY-BOOK","quantity":2}
```

`model_dump()` 不等同于 JSON。它可能包含 `datetime`、`Decimal` 和 UUID 等 Python 对象；需要直接
写入网络或文件时，应根据目标选择 JSON 模式或 JSON 文本。

## 读取 ValidationError

无法校验时，Pydantic 抛出 `ValidationError`：

```python
from pydantic import ValidationError

try:
    OrderItem.model_validate(
        {
            "sku": "PY-BOOK",
            "quantity": "many",
        }
    )
except ValidationError as error:
    first = error.errors()[0]
    print(first["loc"])
    print(first["type"])
    print(first["msg"])
```

输出类似：

```text
('quantity',)
int_parsing
Input should be a valid integer, unable to parse string as an integer
```

`error.errors()` 是一个列表，因为一次校验可能同时发现多个问题。每项常见字段如下：

| 字段 | 含义 |
| --- | --- |
| `loc` | 错误在嵌套输入中的位置 |
| `type` | 机器可识别的错误类型 |
| `msg` | 供人阅读的说明 |
| `input` | 导致错误的原始输入 |
| `ctx` | 某些约束附带的参数 |

程序逻辑不要依赖完整英文 `msg`。稳定接口一般把 `loc` 与 `type` 映射为自己的错误结构，再把 `msg`
作为展示信息。

## 用 Field 声明数值与长度约束

只有 `int` 还不能表达“数量必须在 1 到 100 之间”。可以用 `Field`：

```python
from typing import Annotated

from pydantic import BaseModel, Field

Quantity = Annotated[
    int,
    Field(gt=0, le=100),
]


class OrderItem(BaseModel):
    sku: Annotated[
        str,
        Field(min_length=3, max_length=20),
    ]
    quantity: Quantity
```

`Annotated` 保留基础类型，同时附加 Pydantic 元数据。`Quantity` 可以被多个模型复用，范围也会进入
JSON Schema。

常见约束包括：

| 参数 | 含义 |
| --- | --- |
| `gt` / `ge` | 大于 / 大于等于 |
| `lt` / `le` | 小于 / 小于等于 |
| `min_length` / `max_length` | 字符串、列表等的长度 |
| `pattern` | 字符串正则格式 |
| `multiple_of` | 数值必须是指定值的倍数 |
| `max_digits` | Decimal 的最大总位数 |
| `decimal_places` | Decimal 的最大小数位数 |

```python
OrderItem.model_validate(
    {
        "sku": "PY",
        "quantity": 0,
    }
)
```

这个输入会同时产生 SKU 过短和数量必须大于 0 两个错误。

## 必填字段、可空字段和默认值

下面三种声明含义不同：

```python
class Example(BaseModel):
    required_name: str
    nullable_name: str | None
    optional_name: str | None = None
```

- `required_name` 必须提供，而且不能为 `None`；
- `nullable_name` 必须提供，但允许值为 `None`；
- `optional_name` 可以省略，省略时使用默认值 `None`。

“类型里有 `None`”只表示值可以为空，不自动表示字段可以不传。判断是否必填，要看有没有默认值。

## 嵌套模型会递归校验

订单请求包含订单项列表：

```python
class CreateOrderRequest(BaseModel):
    customer_email: str
    items: list[OrderItem]
```

Pydantic 会先创建每个 `OrderItem`，再创建外层模型。错误位置可能是：

```text
("items", 0, "quantity")
```

它表示第一个订单项的 `quantity` 有问题。这种结构化位置正是 Web 表单和 API 错误提示能够定位字段的
基础。

## 模型校验能保证什么

模型成功只说明输入满足模型能够看到的规则：

```text
能够检查
  字段是否存在、类型能否解析、长度和格式是否正确

不能单独检查
  商品是否存在、库存是否足够、用户是否有权限、数据库是否冲突
```

后一类问题依赖系统当前状态，应由服务、领域对象、仓储或权限组件负责。
