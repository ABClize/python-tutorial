# Python dataclass 与特殊方法

`dataclass` 用于编写主要保存数据的类。它可以自动生成初始化、显示和比较方法。特殊方法则让自定义
对象支持 `len()`、`print()`、加法和相等比较等 Python 语法。

<p class="source-note">对应源码：<code>python/python_interview_practice/05_oop_magic_methods.py</code>、<code>python/python_interview_practice/10_data_model_descriptors.py</code></p>

## `dataclass`

主要用于保存数据的类往往需要重复编写 `__init__()`、`__repr__()` 和 `__eq__()`。
`@dataclass` 可以生成这些方法。下面定义学生数据：

```python
from dataclasses import dataclass, field


@dataclass
class Student:
    name: str
    score: int
    skills: list[str] = field(default_factory=list)


student = Student("小林", 82)
print(student)
print(student == Student("小林", 82))
```

运行结果：

```text
Student(name='小林', score=82, skills=[])
True
```

第一行是自动生成的显示形式。第二行是 `True`，因为两个实例的字段值相同。
`default_factory=list` 会为每个实例调用一次 `list()`，避免共享可变默认值。

需要初始化后处理时可以定义 `__post_init__()`。下面生成一个用于降序排列分数的隐藏字段：

```python
from dataclasses import dataclass, field


@dataclass(order=True)
class Student:
    sort_index: int = field(init=False, repr=False)
    name: str
    score: int

    def __post_init__(self) -> None:
        self.sort_index = -self.score


students = [Student("小林", 82), Student("小周", 91)]
print(sorted(students))
```

运行结果：

```text
[Student(name='小周', score=91), Student(name='小林', score=82)]
```

`order=True` 根据字段顺序生成比较方法。隐藏的 `sort_index` 放在第一位，因此控制主要排序规则。

dataclass 不会自动校验外部输入，也不会默认成为不可变对象。`frozen=True` 会禁止普通字段重新赋值，
但字段引用的可变对象仍需单独处理。

## 特殊方法与 Python 语法

双下划线特殊方法通常由语法或内置函数触发。下面让购物车支持长度、迭代、成员判断和下标读取：

```python
class Cart:
    def __init__(self, items: dict[str, int]) -> None:
        self._items = dict(items)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __contains__(self, item: object) -> bool:
        return item in self._items

    def __getitem__(self, item: str) -> int:
        return self._items[item]


cart = Cart({"Python 书": 2, "笔记本": 3})

print(len(cart))
print(list(cart))
print("Python 书" in cart)
print(cart["笔记本"])
```

运行结果：

```text
2
['Python 书', '笔记本']
True
3
```

四行输出分别来自 `__len__()`、`__iter__()`、`__contains__()` 和 `__getitem__()`。

| Python 写法 | 相关特殊方法 |
| --- | --- |
| `len(obj)` | `obj.__len__()` |
| `repr(obj)` | `obj.__repr__()` |
| `str(obj)` | `obj.__str__()` |
| `for value in obj` | `obj.__iter__()` |
| `value in obj` | `obj.__contains__()` 或迭代协议 |
| `obj[key]` | `obj.__getitem__(key)` |
| `obj(...)` | `obj.__call__(...)` |

特殊方法应遵循用户熟悉的语义。例如 `__len__()` 必须返回非负整数，索引越界应抛出
`IndexError`。

## `__repr__()` 和 `__str__()`

`__repr__()` 面向开发者，目标是明确、无歧义；`__str__()` 面向最终用户。下面为二维向量定义两种文本：

```python
class Vector2D:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Vector2D({self.x!r}, {self.y!r})"

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"


vector = Vector2D(3, 4)
print(repr(vector))
print(str(vector))
```

运行结果：

```text
Vector2D(3, 4)
(3, 4)
```

交互式解释器、容器显示和调试日志常使用 `repr()`。没有定义 `__str__()` 时，`str()` 会退回
`__repr__()`。

## 运算符重载与 `NotImplemented`

特殊方法可以让对象参与运算。下面用 `__add__()` 实现两个二维向量相加：

```python
from __future__ import annotations


class Vector2D:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Vector2D({self.x}, {self.y})"

    def __add__(self, other: object) -> Vector2D:
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x + other.x, self.y + other.y)


print(Vector2D(1, 2) + Vector2D(3, 4))
```

运行结果：

```text
Vector2D(4, 6)
```

两个向量的横坐标和纵坐标分别相加，所以结果是 `Vector2D(4, 6)`。

不支持某种操作数时应返回 `NotImplemented`，让 Python 尝试另一个操作数的反向方法；双方都不支持
时，Python 再抛出 `TypeError`。`NotImplemented` 是特殊单例，不是异常类，也不同于
`NotImplementedError`。

## 相等与哈希

定义值相等时，应同时考虑对象是否可变，以及对象是否需要放进 set 或作为 dict key。下面让坐标按
`x` 和 `y` 比较：

```python
class Coordinate:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Coordinate):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))


first = Coordinate(1, 2)
second = Coordinate(1, 2)

print(first == second)
print(len({first, second}))
```

运行结果：

```text
True
1
```

两个坐标相等，并且在 set 中只保留一个。相等对象必须具有相同哈希值。上例只有在坐标不会改变时才安全；
对象放入 set 后再改变参与哈希的字段，
容器将无法可靠找到它。可变值对象通常应保持不可哈希。

只定义 `__eq__()` 时，Python 通常会把 `__hash__` 设为 `None`，防止错误地使用基于身份的哈希。
