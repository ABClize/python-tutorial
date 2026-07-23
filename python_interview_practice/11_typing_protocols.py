"""Python 3.11 类型标注：泛型、Protocol、Callable 与 TypeVar。

类型标注的主要价值是帮助 IDE、pyright、mypy 等工具在运行前发现问题。
CPython 默认不会因为参数标注错误而阻止函数运行，因此面试时要区分：

- 静态类型检查：分析代码，不执行代码。
- 运行时检查：``isinstance``、显式校验或第三方校验库。
- 类型标注不会自动改变值，也不会自动做类型转换。

本文件只使用 Python 3.11 标准库，所有例子都能直接运行。
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Sequence
from functools import wraps
from typing import (
    Any,
    Generic,
    NotRequired,
    ParamSpec,
    Protocol,
    Self,
    TypeAlias,
    TypedDict,
    TypeGuard,
    TypeVar,
    get_type_hints,
    runtime_checkable,
)


def title(text: str) -> None:
    print(f"\n--- {text} ---")


T = TypeVar("T")
NumberT = TypeVar("NumberT", int, float)


class Stack(Generic[T]):
    """泛型栈：Stack[int] 与 Stack[str] 复用同一份实现。"""

    def __init__(self, values: Iterable[T] = ()) -> None:
        self._values = list(values)

    def push(self, value: T) -> None:
        self._values.append(value)

    def pop(self) -> T:
        if not self._values:
            raise IndexError("不能从空栈中弹出元素")
        return self._values.pop()

    def peek(self) -> T:
        if not self._values:
            raise IndexError("空栈没有栈顶元素")
        return self._values[-1]

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self) -> Iterator[T]:
        # 从栈顶向栈底迭代。
        return reversed(self._values)

    def __repr__(self) -> str:
        return f"Stack({self._values!r})"


def first(items: Sequence[T]) -> T:
    """返回类型与序列元素类型保持一致。"""
    if not items:
        raise ValueError("序列不能为空")
    return items[0]


def choose(first_value: T, second_value: T, use_first: bool) -> T:
    """同一个 TypeVar 表示参数和返回值之间存在类型关系。"""
    return first_value if use_first else second_value


def clamp(value: NumberT, lower: NumberT, upper: NumberT) -> NumberT:
    """受约束 TypeVar：只接受 int 或 float，并保留具体数字类型。"""
    if lower > upper:
        raise ValueError("lower 不能大于 upper")
    return max(lower, min(value, upper))


@runtime_checkable
class Describable(Protocol):
    """结构化子类型：实现这些成员即可，不要求显式继承。"""

    name: str

    def describe(self) -> str: ...


class Candidate:
    def __init__(self, name: str, skills: list[str]) -> None:
        self.name = name
        self.skills = skills

    def describe(self) -> str:
        return f"{self.name}: {', '.join(self.skills)}"


class Project:
    def __init__(self, name: str) -> None:
        self.name = name

    # 故意没有 describe，用于展示 Protocol 检查失败。


def print_description(value: Describable) -> None:
    print("结构化类型:", value.describe())


T_contra = TypeVar("T_contra", contravariant=True)


class Serializer(Protocol[T_contra]):
    """消费 T 的泛型 Protocol，因此类型参数声明为逆变。"""

    def serialize(self, value: T_contra) -> str: ...


class CsvIntSerializer:
    def serialize(self, value: int) -> str:
        return f"value,{value}"


def dump(value: T, serializer: Serializer[T]) -> str:
    return serializer.serialize(value)


BinaryOperation: TypeAlias = Callable[[int, int], int]


def calculate(left: int, right: int, operation: BinaryOperation) -> int:
    """Callable 可以描述函数、lambda 和实现了 __call__ 的对象。"""
    return operation(left, right)


class Multiplier:
    def __init__(self, factor: int) -> None:
        self.factor = factor

    def __call__(self, value: int) -> int:
        return value * self.factor


def make_power(exponent: int) -> Callable[[int], int | float]:
    def power(base: int) -> int | float:
        result = base**exponent
        return float(result) if exponent < 0 else int(result)

    return power


def pipeline(value: T, steps: Iterable[Callable[[T], T]]) -> T:
    """多个 T -> T 的函数可组合成处理流水线。"""
    for step in steps:
        value = step(value)
    return value


P = ParamSpec("P")
R = TypeVar("R")


def logged(function: Callable[P, R]) -> Callable[P, R]:
    """ParamSpec 保留被装饰函数的参数签名，TypeVar 保留返回类型。"""

    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        result = function(*args, **kwargs)
        print(f"调用记录: {function.__name__} -> {result!r}")
        return result

    return wrapper


@logged
def greet(name: str, punctuation: str = "!") -> str:
    return f"你好，{name}{punctuation}"


class Query:
    """Self 适合返回当前类实例的链式 API。"""

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


class CandidateRecord(TypedDict):
    """TypedDict 描述字典的键类型；运行时仍然只是普通 dict。"""

    name: str
    skills: list[str]
    years: NotRequired[int]


class ExperiencedCandidate(TypedDict):
    name: str
    skills: list[str]
    years: int


def has_experience(record: CandidateRecord) -> TypeGuard[ExperiencedCandidate]:
    """TypeGuard 告诉类型检查器：True 分支中的类型已经被缩窄。"""
    return isinstance(record.get("years"), int)


def annotation_name(annotation: Any) -> str:
    """把 get_type_hints 的结果转换成稳定、易读的名称。"""
    return getattr(annotation, "__name__", str(annotation))


def generic_demo() -> None:
    title("Generic 与 TypeVar")

    numbers = Stack[int]([10, 20])
    numbers.push(30)
    print("整数栈:", numbers, "栈顶 =", numbers.peek())
    print("迭代顺序:", list(numbers))
    print("弹出元素:", numbers.pop(), "剩余长度 =", len(numbers))

    words = Stack[str]()
    words.push("Python")
    print("字符串栈:", words.peek())

    print("first 保留元素类型:", first(["A", "B"]))
    print("choose 关联输入输出:", choose("左", "右", use_first=False))
    print("约束 TypeVar:", clamp(120, 0, 100), clamp(3.75, 0.0, 3.0))


def protocol_demo() -> None:
    title("Protocol 与鸭子类型")

    candidate = Candidate("小周", ["Python", "SQL"])
    project = Project("招聘系统")
    print_description(candidate)
    print("Candidate 满足协议:", isinstance(candidate, Describable))
    print("Project 满足协议:", isinstance(project, Describable))
    print("泛型序列化协议:", dump(42, CsvIntSerializer()))
    print("提示: runtime_checkable 只检查成员是否存在，不校验完整签名")


def callable_demo() -> None:
    title("Callable 与高阶函数")

    def add(left: int, right: int) -> int:
        return left + right

    print("函数作为参数:", calculate(3, 4, add))
    print("可调用对象:", calculate(5, 6, lambda a, b: Multiplier(a)(b)))

    cube = make_power(3)
    print("函数作为返回值:", cube(4))

    cleaned = pipeline(
        "  python typing  ",
        [str.strip, str.title, lambda text: text.replace(" ", "-")],
    )
    print("函数流水线:", cleaned)
    print("保留装饰器签名:", greet("面试者", punctuation="！"))


def modern_typing_demo() -> None:
    title("Self、TypedDict 与 TypeGuard")

    query = Query("candidates").where("years >= 3").where("city = 'Shanghai'")
    print("链式 Self:", query.build())

    record: CandidateRecord = {
        "name": "Ada",
        "skills": ["Python", "算法"],
        "years": 5,
    }
    if has_experience(record):
        print("TypeGuard 缩窄后:", record["name"], record["years"])
    print("TypedDict 运行时类型:", type(record).__name__)

    hints = get_type_hints(clamp)
    readable_hints = {key: annotation_name(value) for key, value in hints.items()}
    print("运行时读取标注:", readable_hints)
    print("注意: 标注本身不会在运行时自动拒绝错误类型")


def main() -> None:
    generic_demo()
    protocol_demo()
    callable_demo()
    modern_typing_demo()


if __name__ == "__main__":
    main()
