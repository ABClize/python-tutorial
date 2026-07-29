# 类型标注、泛型与 Protocol

Python 类型标注主要服务于静态分析和阅读者。它不会自动校验、转换或加速运行时对象。理解这一边界，
才能正确使用 Generic、TypeVar、Protocol 和 TypedDict。

<p class="source-note">对应源码：<code>python/python_interview_practice/11_typing_protocols.py</code></p>

## 静态检查与运行时校验是两件事

```python
def repeat(text: str, count: int) -> str:
    return text * count
```

Mypy 可以在执行前发现 `repeat(3, "x")`，但 CPython 默认不会根据标注阻止调用。API 输入仍需
Pydantic、显式检查或其他运行时校验。

类型标注的价值在于：

- 把输入输出契约放在定义附近；
- 让 IDE 提供补全和重构支持；
- 在分支和数据流中提前发现不可能的组合；
- 让接口之间的类型关系可以被验证。

## TypeVar 表达“类型之间的关系”

如果只写 `object`，检查器只知道“可以是任何对象”，不知道输入和输出必须保持一致。

```python
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def first(items: Sequence[T]) -> T:
    return items[0]
```

传入 `Sequence[str]` 时返回值是 `str`；传入 `Sequence[int]` 时返回值是 `int`。TypeVar 的重点
不是“未知”，而是多个位置共享同一类型变量。

## Generic 让容器保留元素类型

```python
from typing import Generic


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._values: list[T] = []

    def push(self, value: T) -> None:
        self._values.append(value)

    def pop(self) -> T:
        return self._values.pop()
```

`Stack[int]` 与 `Stack[str]` 复用同一实现，但检查器能阻止向整数栈压入字符串。

## Protocol 描述能力而非血缘

Protocol 是静态鸭子类型：对象只要拥有要求的成员即可，无需显式继承。

```python
from typing import Protocol


class Describable(Protocol):
    name: str

    def describe(self) -> str: ...


def print_description(value: Describable) -> None:
    print(value.describe())
```

这非常适合仓储、网关、序列化器等端口。业务服务依赖小接口，生产实现和测试 Fake 都可以自然满足。

<div class="concept-map">
  <div class="concept-step"><small>业务服务依赖</small><strong>Protocol</strong></div>
  <span class="concept-arrow">←</span>
  <div class="concept-step"><small>运行时实现</small><strong>真实数据库</strong></div>
  <span class="concept-arrow">+</span>
  <div class="concept-step"><small>测试实现</small><strong>Fake / Mock</strong></div>
</div>

`@runtime_checkable` 只允许粗略 `isinstance` 成员检查，通常不会完整验证签名和类型，不能替代静态检查。

## Callable、ParamSpec 与装饰器

`Callable[[int, int], int]` 描述可调用对象。装饰器若要保留任意参数签名，可使用 ParamSpec：

```python
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def logged(function: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return function(*args, **kwargs)

    return wrapper
```

只写 `Callable[..., object]` 会丢失调用参数和返回值关系，让类型检查失去很多价值。

## TypedDict 描述字典形状

```python
from typing import NotRequired, TypedDict


class CandidateRecord(TypedDict):
    name: str
    skills: list[str]
    years: NotRequired[int]
```

运行时它仍是普通 dict，不会自动验证 key。内部临时数据或既有 dict API 很适合 TypedDict；
需要运行时校验、方法和不变量时，dataclass 或 Pydantic 模型通常更合适。

## 类型缩窄

`isinstance()`、`is None` 和 TypeGuard 能让检查器在分支中获得更具体的类型。不要用大量 `cast()`
压制真实不确定性；cast 只告诉检查器“相信我”，运行时什么也不做。

## Union、Literal 与穷尽分支

`str | None` 明确表示可能缺失，调用方必须先处理 None。`Literal` 可以把字符串状态收窄为有限集合，
配合判别联合表达不同数据形状：

```python
class CardPayment(TypedDict):
    kind: Literal["card"]
    last_four: str


class WalletPayment(TypedDict):
    kind: Literal["wallet"]
    provider: str


Payment = CardPayment | WalletPayment
```

读取 `payment["kind"]` 后，检查器可以缩窄具体分支。`assert_never()` 还能让新增状态时遗漏的分支
在静态检查阶段暴露。

## overload 描述多种调用关系

当返回类型由参数形态决定时，可以用 `@overload` 为检查器列出签名，最后提供一个运行时实现：

```python
@overload
def parse(value: bytes) -> str: ...


@overload
def parse(value: str) -> str: ...


def parse(value: bytes | str) -> str:
    return value.decode() if isinstance(value, bytes) else value
```

overload 不会创建多个运行时函数，也不应拿来描述任意复杂业务分支。若不同输入代表完全不同职责，
拆分函数通常更清晰。

## 协变、逆变与不变

可以用“生产者协变、消费者逆变”记忆：

- 只返回 `T` 的只读生产者，常可对 T 协变；
- 只接收 `T` 的消费者，常可对 T 逆变；
- 同时读写 T 的可变容器通常不变。

例如 `Sequence[Dog]` 可以在只读场景当作 `Sequence[Animal]`，但 `list[Dog]` 不能当作
`list[Animal]`，否则调用方可能向其中加入 Cat，破坏原列表契约。

## Self 与链式 API

`Self` 表示当前实际类，适合返回自身的构造器和链式方法。相比写死基类名称，子类调用后仍能保留
子类类型。它不是“任意与当前类相似的类型”，而是与接收者绑定的类型关系。

## 类型别名与 NewType

类型别名只给复杂类型起易读名称，不创造新运行时类型；`NewType` 则让静态检查器区分相同底层类型
的不同业务含义，例如 `UserId` 和 `OrderId`。需要运行时行为和校验时，应使用真正的值对象。

## 常见误区

### 标注越复杂越安全

无法解释和维护的类型技巧会降低价值。先把公共接口、None 分支和容器元素标清，再引入高级泛型。

### Protocol 必须继承才能满足

Protocol 默认是结构化匹配；这正是它与抽象基类的主要区别。

### `Any` 等于 `object`

`object` 接受任何值，但使用前必须缩窄；`Any` 会跳过大部分检查并向外传播，应集中在不可信边界。

## 面试时怎么表述

> 类型标注是静态契约，不自动做运行时校验。TypeVar 表达输入输出之间的类型关系，Generic 把这种
> 关系带入类，Protocol 用结构化子类型描述对象能力。工程中我会在边界做运行时校验，在内部用
> 类型检查器维护数据流一致性。
