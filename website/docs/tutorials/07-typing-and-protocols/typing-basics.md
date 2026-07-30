# Python 类型标注基础

Python 是动态类型语言，变量名可以在运行时绑定不同类型的对象。类型标注用于描述预期类型，静态检查器
可以在代码运行前发现一部分不一致调用。

<p class="source-note">对应源码：<code>python/python_interview_practice/11_typing_protocols.py</code></p>

## 函数参数与返回值

参数标注写在参数名后，返回值标注写在 `->` 后：

```python
def calculate_total(price: float, quantity: int) -> float:
    return price * quantity


total = calculate_total(19.9, 3)
print(total)
```

运行结果：

```text
59.699999999999996
```

这里表示 `price` 预期是 float，`quantity` 预期是 int，函数预期返回 float。输出中的小数误差来自
二进制浮点表示，与类型标注无关。

没有返回值的函数通常标注为 `-> None`：

```python
def show_message(message: str) -> None:
    print(message)
```

局部变量也可以标注：

```python
score: int = 82
names: list[str] = []
```

右侧已经能清楚推断类型时，不必给每个局部变量重复写标注。

## 类型标注不会自动校验

CPython 默认不会因为实参不符合标注而拒绝调用：

```python
def repeat(text: str, count: int) -> str:
    return text * count


print(repeat("Py", 3))
print(repeat(3, 2))
```

运行结果：

```text
PyPyPy
6
```

第二次调用不符合标注，但整数乘法在运行时仍然有效。标注也不会把字符串 `"3"` 自动转换为整数。

本项目使用 Mypy 做静态检查：

```bash
cd python
uv run mypy run_all.py interview_exercises python_interview_practice backend_interview
```

静态检查器分析代码但不执行代码。HTTP、配置文件和数据库等外部数据仍需 `isinstance()`、显式判断、
Pydantic 或其他运行时校验。

## 内置容器类型

Python 3.9+ 可以直接给内置容器加类型参数：

```python
def average(scores: list[int]) -> float:
    return sum(scores) / len(scores)


def score_by_name(
    records: list[tuple[str, int]],
) -> dict[str, int]:
    return dict(records)
```

常用写法：

| 数据结构 | 类型标注 |
| --- | --- |
| 整数列表 | `list[int]` |
| 字符串到整数的映射 | `dict[str, int]` |
| 字符串集合 | `set[str]` |
| 任意长度的整数 tuple | `tuple[int, ...]` |
| 固定两个元素的 tuple | `tuple[str, int]` |

`tuple[int, ...]` 中的省略号表示任意数量的 int。

## 参数优先使用所需的最小接口

函数只读取参数时，可以标注抽象接口：

```python
from collections.abc import Iterable, Sequence


def total(values: Iterable[int]) -> int:
    return sum(values)


def first(values: Sequence[str]) -> str:
    return values[0]
```

- `Iterable[int]` 表示能够依次产生 int，不保证长度和索引；
- `Sequence[str]` 表示有顺序、支持长度和整数索引的只读接口；
- `list[str]` 明确要求 list，并允许函数使用列表的可变操作。

参数标注越接近函数真正需要的能力，调用方可选择的实现越多。返回类型通常应更具体，让调用方知道得到
什么对象。

## 联合类型

竖线 `|` 表示多种可能类型：

```python
def normalize_id(value: str | int) -> str:
    return str(value).strip()


print(normalize_id(1001))
print(normalize_id(" 1002 "))
```

运行结果：

```text
1001
1002
```

可能没有结果时常用 `T | None`：

```python
def find_score(
    name: str,
    scores: dict[str, int],
) -> int | None:
    return scores.get(name)


score = find_score("小林", {"小林": 82})

if score is not None:
    print(score + 5)
```

运行结果：

```text
87
```

Python 3.10 之前常写 `Optional[int]`，它等价于 `int | None`，并不表示参数可以省略。参数是否可省略
由默认值决定。

## 类型缩窄

联合类型在使用前通常需要缩窄：

```python
def length_or_value(value: str | int) -> int:
    if isinstance(value, str):
        return len(value)
    return value
```

`isinstance()`、`is None`、`is not None` 和明确的控制流都能帮助检查器缩小可能范围：

```python
def require_name(name: str | None) -> str:
    if name is None:
        raise ValueError("name 不能为空")
    return name.upper()
```

抛出异常之后，后续路径中的 `name` 只可能是 str。

## Any 与 object

`Any` 和 `object` 都能接收未知类型，但检查强度不同：

```python
from typing import Any


def unsafe_length(value: Any) -> int:
    return value.length


def safe_length(value: object) -> int:
    if isinstance(value, str | list | tuple):
        return len(value)
    raise TypeError("对象不支持此长度规则")
```

- 对 `Any` 的大多数操作会被静态检查器放行，错误可能推迟到运行时；
- `object` 是所有 Python 对象的基类，但只能直接使用所有对象都具备的操作；
- 使用 `object` 时，必须通过判断或 Protocol 缩窄到所需能力。

第三方库缺少类型信息或渐进迁移旧代码时可以局部使用 `Any`，但不应把它作为消除类型错误的默认方法。

## 基础标注注意事项

- 标注描述约定，不会自动转换运行时数据。
- 参数使用真正需要的最小接口。
- 返回值尽量具体，避免无理由使用 `Any`。
- `T | None` 必须在使用前处理 None 分支。
- 类型检查和运行时测试解决不同问题，两者都需要。
