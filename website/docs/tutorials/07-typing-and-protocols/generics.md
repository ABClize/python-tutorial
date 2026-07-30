# Python TypeVar、Generic 与 Self

泛型用于让多个位置使用同一种类型。例如，一个函数接收整数序列时返回整数，接收字符串序列时返回
字符串。`TypeVar` 表示这次调用中需要保持一致的类型。

<p class="source-note">对应源码：<code>python/python_interview_practice/11_typing_protocols.py</code></p>

## TypeVar 让输入和输出使用同一类型

下面的 `first()` 返回序列中的第一个元素。返回类型与序列元素类型相同：

```python
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def first(items: Sequence[T]) -> T:
    if not items:
        raise ValueError("序列不能为空")
    return items[0]
```

同一个 `T` 出现在参数元素和返回值位置：

- 传入 `list[int]`，返回 int；
- 传入 `tuple[str, ...]`，返回 str。

如果返回类型写成 `object`，具体元素类型会丢失；写成 `Any` 则会放弃后续检查。

## 多个参数共享同一类型

`TypeVar` 也可以让多个参数和返回值保持相同类型：

```python
from typing import TypeVar

T = TypeVar("T")


def choose(
    first_value: T,
    second_value: T,
    use_first: bool,
) -> T:
    return first_value if use_first else second_value


print(choose("左", "右", use_first=False))
```

运行结果：

```text
右
```

示例返回 `"右"`。在这次调用中，两个候选值和返回值都是 `str`。

## TypeVar 上界

上界要求具体类型是某个父类型或其子类。下面的函数只接收 `Animal` 及其子类：

```python
from typing import TypeVar


class Animal:
    def speak(self) -> str:
        return "..."


AnimalT = TypeVar("AnimalT", bound=Animal)


def louder(animal: AnimalT) -> AnimalT:
    print(animal.speak().upper())
    return animal
```

`bound=Animal` 允许 Animal 的任意子类，返回值仍保留具体子类类型。

## 受约束 TypeVar

有限的一组允许类型可以写成约束：

```python
from typing import TypeVar

NumberT = TypeVar("NumberT", int, float)


def clamp(
    value: NumberT,
    lower: NumberT,
    upper: NumberT,
) -> NumberT:
    if lower > upper:
        raise ValueError("lower 不能大于 upper")
    return max(lower, min(value, upper))


print(clamp(120, 0, 100))
print(clamp(3.75, 0.0, 3.0))
```

运行结果：

```text
100
3.0
```

约束表示每次调用选择候选类型之一；上界则允许某个父类型的任意子类。如果函数不需要保留输入输出关系，
直接使用联合类型通常更简单。

## Generic 自定义泛型类

自定义类也可以保存元素类型。下面实现一个后进先出的泛型栈：

```python
from collections.abc import Iterable, Iterator
from typing import Generic, TypeVar

T = TypeVar("T")


class Stack(Generic[T]):
    def __init__(self, values: Iterable[T] = ()) -> None:
        self._values = list(values)

    def push(self, value: T) -> None:
        self._values.append(value)

    def pop(self) -> T:
        if not self._values:
            raise IndexError("不能从空栈中弹出元素")
        return self._values.pop()

    def __iter__(self) -> Iterator[T]:
        return reversed(self._values)


numbers = Stack[int]([10, 20])
numbers.push(30)

print(numbers.pop())
print(list(numbers))
```

运行结果：

```text
30
[20, 10]
```

对 `Stack[int]`，检查器知道 `push()` 只接收 int，`pop()` 和迭代都产生 int。运行时
`Stack[int]` 不会自动校验加入的值。

## Self 表示当前实例类型

返回当前实例的链式方法可以使用 `Self`。下面的 `where()` 每次都返回当前查询对象：

```python
from typing import Self


class Query:
    def __init__(self, table: str) -> None:
        self.table = table
        self.conditions: list[str] = []

    def where(self, condition: str) -> Self:
        self.conditions.append(condition)
        return self

    def build(self) -> str:
        sql = f"SELECT * FROM {self.table}"
        if self.conditions:
            sql += " WHERE " + " AND ".join(self.conditions)
        return sql


query = Query("users").where("active = true").where("age >= 18")
print(query.build())
```

运行结果：

```text
SELECT * FROM users WHERE active = true AND age >= 18
```

`Self` 比写死 `-> Query` 更适合继承。子类调用 `where()` 后，检查器仍能保留子类类型。

## 泛型使用注意事项

- `TypeVar` 用于让多个位置保持同一种类型，不是所有联合类型都需要改成泛型。
- 泛型参数通常不会在运行时自动校验。
- 空容器可能让检查器难以推断类型，可以显式写 `Stack[int]()`。
- 输入和输出没有类型关联时，普通具体类型或联合类型更容易理解。
- 高级泛型应让公共接口更清楚，而不是只为了消除检查器错误。
