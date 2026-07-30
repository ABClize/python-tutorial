# Python Protocol、Callable 与 ParamSpec

Protocol 描述对象需要具备的能力，Callable 描述可调用对象的参数和返回值。它们适合定义依赖边界、
高阶函数和装饰器，而不要求所有实现继承同一个基类。

<p class="source-note">对应源码：<code>python/python_interview_practice/11_typing_protocols.py</code></p>

## Protocol 与结构化类型

```python
from typing import Protocol


class Notifier(Protocol):
    def send(self, message: str) -> None: ...


class ConsoleNotifier:
    def send(self, message: str) -> None:
        print(message)


def welcome(name: str, notifier: Notifier) -> None:
    notifier.send(f"欢迎，{name}")


welcome("小林", ConsoleNotifier())
```

运行结果：

```text
欢迎，小林
```

`ConsoleNotifier` 没有继承 `Notifier`，但它提供兼容的 `send()`，静态上满足协议。这种按成员结构匹配
的方式称为结构化子类型。

Protocol 适合：

- 依赖注入中的仓储、网关和通知器；
- 多个第三方类型共有的最小能力；
- 测试 Fake 与生产实现共享的边界。

协议只声明调用方真正使用的成员。接口过大时，每个实现和测试替身都被迫提供无关方法。

## runtime_checkable

Protocol 默认主要供静态检查。需要有限的 `isinstance()` 检查时，可以添加
`@runtime_checkable`：

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class Describable(Protocol):
    name: str

    def describe(self) -> str: ...


class Candidate:
    def __init__(self, name: str) -> None:
        self.name = name

    def describe(self) -> str:
        return self.name


print(isinstance(Candidate("小林"), Describable))
```

运行结果：

```text
True
```

运行时检查主要确认成员是否存在，不会完整验证参数和返回类型，因此不能替代 Mypy。

## Callable 描述可调用对象

```python
from collections.abc import Callable

PriceRule = Callable[[float], float]


def apply_rule(price: float, rule: PriceRule) -> float:
    return rule(price)


def vip_discount(price: float) -> float:
    return price * 0.8


print(apply_rule(100.0, vip_discount))
print(apply_rule(100.0, lambda value: value - 10))
```

运行结果：

```text
80.0
90.0
```

函数、lambda、绑定方法和实现 `__call__()` 的实例都可以满足 Callable。

`Callable[..., str]` 只约束返回 str，不检查参数列表。已知参数时应尽量写完整签名。

## 可调用对象

```python
class Multiplier:
    def __init__(self, factor: int) -> None:
        self.factor = factor

    def __call__(self, value: int) -> int:
        return value * self.factor


double = Multiplier(2)
print(double(5))
```

运行结果：

```text
10
```

需要保存配置和状态的可调用行为可以使用类；简单无状态处理通常直接使用函数。

## ParamSpec 保留调用签名

装饰器要转发任意参数，并保留原函数签名：

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def logged(function: Callable[P, R]) -> Callable[P, R]:
    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        result = function(*args, **kwargs)
        print(f"{function.__name__} -> {result!r}")
        return result

    return wrapper


@logged
def greet(name: str, punctuation: str = "!") -> str:
    return f"你好，{name}{punctuation}"


print(greet("小林", punctuation="！"))
```

运行结果：

```text
greet -> '你好，小林！'
你好，小林！
```

TypeVar `R` 保留返回类型，ParamSpec `P` 保留完整参数列表。如果只写 `Callable[..., R]`，装饰后的
函数会失去参数名称和参数类型信息。

## Protocol 与抽象基类

| 需求 | Protocol | 抽象基类 |
| --- | --- | --- |
| 不修改已有实现即可匹配 | 适合 | 通常需要继承或注册 |
| 只描述调用方需要的能力 | 适合 | 可以 |
| 共享实现代码 | 不负责 | 适合 |
| 运行时强制不能实例化 | 不负责 | 适合 |

两者不是互斥选择。一个框架可以在运行时使用抽象基类共享实现，同时对外暴露更小的 Protocol。
