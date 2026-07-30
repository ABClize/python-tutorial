# 输入规范化、模型配置与严格模式

规范化是把等价输入转换成统一形式，例如去掉空格或把 SKU 转成大写。`ConfigDict` 用来配置整个
Pydantic 模型。严格模式会拒绝原本可能被自动转换的类型。

这些规则应集中写在输入模型中，避免业务代码到处调用 `strip()` 和 `int()`。

<p class="source-note">对应源码：<code>python/backend_interview/schemas.py</code>、<code>python/backend_interview/pydantic_patterns.py</code></p>

## 先规范化，再执行约束

仓库中的 SKU 需要去空格、转大写，再检查格式。它被定义成可复用类型：

```python
from typing import Annotated, Any

from pydantic import BeforeValidator, StringConstraints


def normalize_sku(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip().upper()
    return value


Sku = Annotated[
    str,
    BeforeValidator(normalize_sku),
    StringConstraints(
        pattern=r"^[A-Z0-9-]{3,20}$"
    ),
]
```

```python
from backend_interview.schemas import CreateOrderItem

item = CreateOrderItem.model_validate(
    {
        "sku": " py-book ",
        "quantity": 2,
    }
)

print(item.sku)
```

```text
PY-BOOK
```

`BeforeValidator` 得到原始输入，所以规范化发生在字符串类型和正则约束之前。非字符串输入被原样返回，
让后续类型校验生成准确错误，而不是在自定义函数里意外调用不存在的方法。

## 规范化不是偷偷猜测

合理的规范化通常不改变业务含义，例如：

- 去掉两端空白；
- 统一不区分大小写的标识符；
- 把约定好的逗号分隔文本拆成列表；
- 把时区明确的时间转为 UTC。

下面的“转换”则可能改变语义：

- 把任何非空字符串当成 `True`；
- 猜测 `01/02/03` 的日期顺序；
- 自动截断超长文本；
- 把未知枚举映射到某个默认值。

边界越宽松，越要清楚记录转换规则。无法确定意图时，明确报错通常比猜测安全。

## ConfigDict 配置整个模型

Pydantic v2 使用 `model_config`：

```python
from pydantic import BaseModel, ConfigDict


class CreateOrderRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    customer_email: str
```

仓库中涉及的常见选项：

| 配置 | 作用 |
| --- | --- |
| `extra="forbid"` | 拒绝未声明字段 |
| `extra="ignore"` | 忽略未声明字段 |
| `str_strip_whitespace=True` | 去除字符串两端空白 |
| `strict=True` | 默认拒绝类型转换 |
| `from_attributes=True` | 允许从对象属性读取字段 |

`extra="forbid"` 能发现调用方把 `customer_email` 拼成 `customer_emial` 的错误。但在需要兼容未来字段的
数据消费场景中，`ignore` 可能更合适。这是接口兼容策略，不是固定答案。

## 默认模式会解析部分类型

下面演示默认模式把字符串数字转换成整数：

```python
from pydantic import BaseModel


class Metric(BaseModel):
    name: str
    value: int


metric = Metric.model_validate(
    {
        "name": "requests",
        "value": "12",
    }
)

print(metric.value)
```

```text
12
```

默认模式适合天然以字符串传入的边界，例如环境变量、URL Query 和 HTML 表单。解析不是“关闭校验”，
`"twelve"` 仍不能变成整数。

## 严格模式拒绝隐式转换

下面开启严格模式，让整数字段只接受真正的整数：

```python
from pydantic import BaseModel, ConfigDict


class StrictMetric(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
    )

    name: str
    value: int
```

```python
StrictMetric.model_validate(
    {
        "name": "requests",
        "value": "12",
    }
)
```

错误类型是 `int_type`，因为严格模式要求输入本身就是整数。

严格模式更适合内部事件、计费数据和指标协议：上游本应已经产生正确类型，收到字符串往往表示协议出现
问题。也可以只对某个字段使用 `Field(strict=True)`，不必让整个模型严格。

## JSON 输入与 Python 输入可能不同

JSON 本身只有有限的数据类型，没有 Python 的 `datetime`、UUID 或 tuple。Pydantic 从 JSON 文本读取
时，会根据目标类型解析字符串：

```python
class Event(BaseModel):
    event_id: UUID
    occurred_at: datetime
```

```python
event = Event.model_validate_json(
    """
    {
      "event_id": "ac5ab09c-e31c-4b2d-a945-e10f061ef3cc",
      "occurred_at": "2026-07-30T08:00:00Z"
    }
    """
)
```

选择严格策略时要结合输入媒介测试，不能只凭字段类型推断所有入口行为。

## 规范化会影响后续规则

订单请求在检查重复 SKU 前，子模型已经把 SKU 转成大写：

```text
" py-book " ──规范化──> "PY-BOOK"
"PY-BOOK"   ──规范化──> "PY-BOOK"
```

因此二者会被识别为重复商品。若先检查原始字符串再规范化，同一商品可能绕过重复检查。

校验顺序也是数据契约的一部分：原始输入处理、类型解析、字段校验和模型级校验各自看到的数据不同。

## 根据输入来源选择模式

选择前先看输入从哪里来：

| 输入来源 | 常见选择 |
| --- | --- |
| Query、表单、环境变量 | 允许明确的字符串解析 |
| 外部 JSON API | 明确 extra 策略，并限制格式和范围 |
| 内部事件或计费协议 | 倾向 strict 与 `extra="forbid"` |
| 人工录入标识符 | 可以做可解释的空白和大小写规范化 |

宽松与严格都不是目的。目标是让“哪些输入会被接受，接受后变成什么”保持可预测。
