"""Python 数据模型进阶：描述符、属性查找、MRO 与魔术方法。

建议学习方式：
1. 先遮住输出，猜测每一段会打印什么。
2. 在 ``__get__``、``__getattr__`` 和 ``super()`` 所在行设置断点。
3. 观察实例的 ``__dict__``、类的 ``__dict__`` 和 ``type(obj).mro()``。

面试重点：
- 数据描述符（定义了 ``__set__`` 或 ``__delete__``）优先于实例属性。
- 非数据描述符只有 ``__get__``，可以被同名实例属性遮蔽。
- ``__getattr__`` 只在常规属性查找失败后调用。
- ``super()`` 表示“沿 MRO 查找下一个实现”，不简单等于“调用父类”。
- 运算符重载遇到不支持的类型时，通常应返回 ``NotImplemented``。
"""

from __future__ import annotations

import math
from collections.abc import Iterator
from typing import Any, cast, overload


def title(text: str) -> None:
    """打印分节标题，让命令行输出更容易阅读。"""
    print(f"\n--- {text} ---")


class NonNegativeNumber:
    """验证非负数的数据描述符。

    同一个描述符类可以复用于多个字段。``__set_name__`` 会在创建宿主类时
    告诉描述符自己绑定到哪个属性，因此值可以保存在不同的私有属性中。
    """

    def __set_name__(self, owner: type[Any], name: str) -> None:
        self.public_name = name
        self.storage_name = f"_{name}"

    @overload
    def __get__(
        self,
        instance: None,
        owner: type[Any] | None = None,
    ) -> NonNegativeNumber: ...

    @overload
    def __get__(
        self,
        instance: Any,
        owner: type[Any] | None = None,
    ) -> int | float: ...

    def __get__(
        self,
        instance: Any | None,
        owner: type[Any] | None = None,
    ) -> NonNegativeNumber | int | float:
        if instance is None:
            # 通过 Employee.salary 访问时，返回描述符自身。
            return self
        return cast(int | float, getattr(instance, self.storage_name))

    def __set__(self, instance: Any, value: int | float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{self.public_name} 必须是数字")
        if value < 0:
            raise ValueError(f"{self.public_name} 不能为负数")
        setattr(instance, self.storage_name, value)


class Employee:
    """salary 和 bonus 共用描述符逻辑，避免重复编写 property。"""

    salary = NonNegativeNumber()
    bonus = NonNegativeNumber()

    def __init__(self, name: str, salary: int, bonus: int = 0) -> None:
        self.name = name
        self.salary = salary
        self.bonus = bonus

    @property
    def total_income(self) -> int | float:
        """property 本身也是一种数据描述符。"""
        return self.salary + self.bonus


class DisplayName:
    """只有 ``__get__``，所以它是非数据描述符。"""

    def __get__(
        self,
        instance: Profile | None,
        owner: type[Profile] | None = None,
    ) -> DisplayName | str:
        if instance is None:
            return self
        owner_name = owner.__name__ if owner is not None else type(instance).__name__
        return f"{owner_name}<{instance.name}>"


class Profile:
    display_name = DisplayName()

    def __init__(self, name: str) -> None:
        self.name = name


class Settings:
    """用 ``__getattr__`` 为缺失属性提供只读默认值。"""

    defaults = {"theme": "light", "language": "zh-CN"}

    def __init__(self, **overrides: str) -> None:
        self._overrides = overrides

    def __getattr__(self, name: str) -> str:
        # 只有 object.__getattribute__ 没找到 name，才会进入这里。
        if name in self._overrides:
            return self._overrides[name]
        if name in self.defaults:
            return self.defaults[name]
        raise AttributeError(f"{type(self).__name__!s} 没有属性 {name!r}")


class Root:
    def trace(self) -> list[str]:
        return ["Root"]


class Left(Root):
    def trace(self) -> list[str]:
        return ["Left", *super().trace()]


class Right(Root):
    def trace(self) -> list[str]:
        return ["Right", *super().trace()]


class Diamond(Left, Right):
    """菱形继承：每一层都合作式调用 super()。"""

    def trace(self) -> list[str]:
        return ["Diamond", *super().trace()]


class Vector2D:
    """实现多个常见协议的不可变二维向量。

    Python 的特殊方法通常由 ``len(v)``、``v + other`` 等语法隐式调用，
    而不是在业务代码中直接写 ``v.__len__()``。
    """

    __slots__ = ("_x", "_y")

    def __init__(self, x: int | float, y: int | float) -> None:
        self._x = x
        self._y = y

    @property
    def x(self) -> int | float:
        return self._x

    @property
    def y(self) -> int | float:
        return self._y

    def __repr__(self) -> str:
        # repr 面向开发者，理想情况下应明确且可用于重建对象。
        return f"Vector2D({self.x!r}, {self.y!r})"

    def __str__(self) -> str:
        # str 面向用户；没有定义时会退回 repr。
        return f"({self.x}, {self.y})"

    def __iter__(self) -> Iterator[int | float]:
        # 支持 tuple(vector) 和 x, y = vector。
        yield self.x
        yield self.y

    def __len__(self) -> int:
        # 这里表达向量固定有两个维度。
        return 2

    def __getitem__(self, index: int) -> int | float:
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        raise IndexError("二维向量索引只能是 0 或 1")

    def __add__(self, other: object) -> Vector2D:
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: object) -> Vector2D:
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: object) -> Vector2D:
        # 让 3 * vector 也能工作。
        return self * scalar

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2D):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        # 定义了相等语义且对象不可变，便可安全地作为字典键或集合元素。
        return hash((self.x, self.y))

    def __abs__(self) -> float:
        return math.hypot(self.x, self.y)

    def __bool__(self) -> bool:
        return self.x != 0 or self.y != 0


class ShoppingCart:
    """用容器魔术方法实现一个小型只读视图。"""

    def __init__(self, items: dict[str, int]) -> None:
        self._items = dict(items)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[str]:
        return iter(self._items)

    def __contains__(self, item: object) -> bool:
        return item in self._items

    def __getitem__(self, item: str) -> int:
        return self._items[item]

    def __call__(self, item: str, quantity: int = 1) -> int:
        """实例也可以像函数一样调用，计算某商品的总数量。"""
        return self._items.get(item, 0) * quantity


def descriptor_demo() -> None:
    title("数据描述符与非数据描述符")

    employee = Employee("小林", salary=12_000, bonus=2_000)
    print("员工收入:", employee.salary, employee.bonus, employee.total_income)
    print("描述符存储名:", Employee.salary.storage_name)
    print("实例字典:", employee.__dict__)

    # 即使强行塞入同名实例属性，数据描述符仍优先返回 _salary。
    employee.__dict__["salary"] = 999_999
    print("同名实例属性不能遮蔽数据描述符:", employee.salary)

    try:
        employee.bonus = -1
    except ValueError as error:
        print("描述符校验:", error)

    profile = Profile("Ada")
    print("非数据描述符:", profile.display_name)
    profile.display_name = "实例自己的名称"
    print("被实例属性遮蔽:", profile.display_name)
    del profile.display_name
    print("删除实例属性后恢复:", profile.display_name)


def attribute_lookup_demo() -> None:
    title("属性查找与 __getattr__")

    settings = Settings(language="en-US")
    # 这里故意演示运行时动态属性；静态检查器无法预先知道该属性存在。
    settings.project = "interview"  # type: ignore[attr-defined]
    print("普通实例属性:", settings.project)
    print("覆盖值:", settings.language)
    print("默认值:", settings.theme)

    try:
        print(settings.missing)
    except AttributeError as error:
        print("查找失败:", error)

    print("hasattr 会捕获 AttributeError:", hasattr(settings, "missing"))


def mro_demo() -> None:
    title("MRO 与合作式 super")

    mro_names = [item.__name__ for item in Diamond.mro()]
    print("方法解析顺序:", " -> ".join(mro_names))
    print("实际调用链:", " -> ".join(Diamond().trace()))


def magic_method_demo() -> None:
    title("魔术方法与 Python 协议")

    vector = Vector2D(3, 4)
    other = Vector2D(1, 2)
    print("repr / str:", repr(vector), str(vector))
    print("序列协议:", len(vector), tuple(vector), vector[0])
    print("运算符:", vector + other, vector * 2, 2 * vector)
    print("绝对值与真值:", abs(vector), bool(vector), bool(Vector2D(0, 0)))
    print("相等与哈希容器:", len({vector, Vector2D(3, 4), other}))

    cart = ShoppingCart({"Python书": 2, "笔记本": 3})
    print("容器协议:", len(cart), list(cart), "Python书" in cart, cart["笔记本"])
    print("可调用实例:", cart("Python书", quantity=4))

    try:
        _ = vector + 1
    except TypeError as error:
        # 返回 NotImplemented 后，Python 尝试反向运算；仍不支持才抛 TypeError。
        print("不支持的运算:", type(error).__name__)


def main() -> None:
    descriptor_demo()
    attribute_lookup_demo()
    mro_demo()
    magic_method_demo()


if __name__ == "__main__":
    main()
