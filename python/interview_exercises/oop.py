"""面向对象面试题：封装、组合、多态、描述符和上下文管理器。"""

from __future__ import annotations

import sys

if __package__ in (None, "") and sys.path:
    # dataclasses 等标准库内部会导入 collections。
    sys.path.pop(0)

from abc import ABC, abstractmethod
from dataclasses import dataclass
from math import hypot
from types import TracebackType
from typing import Generic, Literal, TypeVar


class Temperature:
    """题目：使用 property 封装温度，并提供替代构造函数。

    绝对零度校验集中在 setter，避免对象进入非法状态。
    属性读取、写入和单位转换的时间与空间复杂度都是 O(1)。
    """

    ABSOLUTE_ZERO_CELSIUS = -273.15

    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < self.ABSOLUTE_ZERO_CELSIUS:
            raise ValueError("温度不能低于绝对零度")
        self._celsius = float(value)

    @property
    def fahrenheit(self) -> float:
        return self.celsius * 9 / 5 + 32

    @classmethod
    def from_fahrenheit(cls, value: float) -> Temperature:
        return cls((value - 32) * 5 / 9)


@dataclass(frozen=True)
class Vector2D:
    """题目：实现不可变二维向量及常用魔术方法。

    ``frozen=True`` 让对象可哈希，也能避免向量作为字典键后被修改。
    所有操作的时间、空间复杂度均为 O(1)。
    """

    x: float
    y: float

    def __add__(self, other: Vector2D) -> Vector2D:
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: float) -> Vector2D:
        return Vector2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Vector2D:
        return self * scalar

    def __abs__(self) -> float:
        return hypot(self.x, self.y)


@dataclass(frozen=True)
class Product:
    """不可变商品值对象，价格使用整数分，避免浮点金额误差。"""

    name: str
    unit_price_cents: int

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("商品名不能为空")
        if self.unit_price_cents < 0:
            raise ValueError("价格不能为负数")


@dataclass(frozen=True)
class CartLine:
    product: Product
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("数量必须为正整数")

    @property
    def subtotal_cents(self) -> int:
        return self.product.unit_price_cents * self.quantity


class DiscountPolicy(ABC):
    """题目：用策略模式替换庞大的 if/elif 折扣判断。"""

    @abstractmethod
    def discount_cents(self, subtotal_cents: int) -> int:
        """返回应减免的金额（整数分）。"""


class NoDiscount(DiscountPolicy):
    def discount_cents(self, subtotal_cents: int) -> int:
        return 0


class PercentageDiscount(DiscountPolicy):
    """按整数百分比打折，结果向下取整到分。"""

    def __init__(self, percent: int) -> None:
        if not 0 <= percent <= 100:
            raise ValueError("折扣百分比必须位于 0 到 100 之间")
        self.percent = percent

    def discount_cents(self, subtotal_cents: int) -> int:
        return subtotal_cents * self.percent // 100


class ThresholdDiscount(DiscountPolicy):
    """满 threshold_cents 减 reduction_cents。"""

    def __init__(self, threshold_cents: int, reduction_cents: int) -> None:
        if threshold_cents <= 0 or reduction_cents < 0:
            raise ValueError("门槛必须为正数，减免不能为负数")
        self.threshold_cents = threshold_cents
        self.reduction_cents = reduction_cents

    def discount_cents(self, subtotal_cents: int) -> int:
        if subtotal_cents < self.threshold_cents:
            return 0
        return min(subtotal_cents, self.reduction_cents)


class ShoppingCart:
    """组合商品条目与折扣策略。

    计算小计和总价的时间复杂度为 O(n)，空间复杂度为 O(1)。
    """

    def __init__(self, discount_policy: DiscountPolicy | None = None) -> None:
        self._lines: list[CartLine] = []
        self.discount_policy = discount_policy or NoDiscount()

    def add(self, product: Product, quantity: int = 1) -> None:
        self._lines.append(CartLine(product, quantity))

    @property
    def subtotal_cents(self) -> int:
        return sum(line.subtotal_cents for line in self._lines)

    @property
    def total_cents(self) -> int:
        subtotal = self.subtotal_cents
        return subtotal - self.discount_policy.discount_cents(subtotal)

    def __len__(self) -> int:
        return sum(line.quantity for line in self._lines)


class PositiveNumber:
    """题目：实现可复用的数据描述符，统一验证多个数字字段。"""

    def __set_name__(self, owner: type[object], name: str) -> None:
        self.storage_name = f"_{name}"

    def __get__(self, instance: object | None, owner: type[object]) -> float | PositiveNumber:
        if instance is None:
            return self
        return float(getattr(instance, self.storage_name))

    def __set__(self, instance: object, value: float) -> None:
        if value <= 0:
            raise ValueError("数值必须大于 0")
        setattr(instance, self.storage_name, float(value))


class Rectangle:
    """宽和高共享 PositiveNumber 的验证逻辑。"""

    width = PositiveNumber()
    height = PositiveNumber()

    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    @property
    def area(self) -> float:
        return self.width * self.height  # type: ignore[operator]


T = TypeVar("T")


class TransactionalList(Generic[T]):
    """题目：实现支持提交与异常回滚的上下文管理器。

    进入上下文时浅拷贝列表；正常退出保留修改，异常退出恢复原内容。
    创建快照和回滚均为 O(n)，额外空间为 O(n)。
    """

    def __init__(self, values: list[T] | None = None) -> None:
        self.values = list(values or [])
        self._snapshot: list[T] | None = None

    def __enter__(self) -> list[T]:
        if self._snapshot is not None:
            raise RuntimeError("不支持嵌套事务")
        self._snapshot = self.values.copy()
        return self.values

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        if exception_type is not None and self._snapshot is not None:
            self.values[:] = self._snapshot
        self._snapshot = None
        return False


def run_tests() -> None:
    freezing = Temperature(0)
    assert freezing.fahrenheit == 32
    assert round(Temperature.from_fahrenheit(212).celsius, 8) == 100
    try:
        Temperature(-300)
    except ValueError:
        pass
    else:
        raise AssertionError("低于绝对零度应该抛出 ValueError")

    vector = Vector2D(3, 4)
    assert abs(vector) == 5
    assert vector + Vector2D(1, -1) == Vector2D(4, 3)
    assert 2 * vector == Vector2D(6, 8)
    assert {vector: "可作为字典键"}[Vector2D(3, 4)] == "可作为字典键"

    keyboard = Product("键盘", 20_000)
    mouse = Product("鼠标", 10_000)
    cart = ShoppingCart(PercentageDiscount(10))
    cart.add(keyboard)
    cart.add(mouse, 2)
    assert len(cart) == 3
    assert cart.subtotal_cents == 40_000
    assert cart.total_cents == 36_000

    threshold_cart = ShoppingCart(ThresholdDiscount(30_000, 5_000))
    threshold_cart.add(keyboard, 2)
    assert threshold_cart.total_cents == 35_000

    rectangle = Rectangle(3, 4)
    assert rectangle.area == 12
    try:
        rectangle.width = 0
    except ValueError:
        pass
    else:
        raise AssertionError("非正宽度应该抛出 ValueError")

    values = TransactionalList([1, 2])
    with values as current:
        current.append(3)
    assert values.values == [1, 2, 3]

    try:
        with values as current:
            current.append(4)
            raise RuntimeError("模拟事务失败")
    except RuntimeError:
        pass
    assert values.values == [1, 2, 3]


def main() -> None:
    run_tests()
    cart = ShoppingCart(PercentageDiscount(20))
    cart.add(Product("Python 面试书", 8_800), 2)
    print(f"购物车原价：{cart.subtotal_cents / 100:.2f} 元")
    print(f"购物车实付：{cart.total_cents / 100:.2f} 元")
    print("oop.py：全部测试通过")


if __name__ == "__main__":
    main()
