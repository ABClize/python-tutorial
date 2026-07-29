"""面向对象、数据类、属性和常见魔术方法。"""

from dataclasses import dataclass, field


class Animal:
    category = "animal"  # 类属性：所有实例共享

    def __init__(self, name):
        self.name = name  # 实例属性：每个实例各自拥有

    def speak(self):
        return "..."


class Dog(Animal):
    def speak(self):
        return f"{self.name}: 汪汪"


class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("温度不能低于绝对零度")
        self._celsius = value

    @property
    def fahrenheit(self):
        return self.celsius * 9 / 5 + 32


@dataclass(order=True)
class Student:
    # sort_index 不显示在 repr 中，但参与排序。
    sort_index: int = field(init=False, repr=False)
    name: str
    score: int

    def __post_init__(self):
        self.sort_index = -self.score


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __len__(self):
        # len() 必须返回非负整数；此处返回向量坐标绝对值之和。
        return abs(self.x) + abs(self.y)


def main():
    dog = Dog("Lucky")
    print("继承和重写:", dog.speak(), isinstance(dog, Animal))

    temperature = Temperature(25)
    print("属性:", temperature.celsius, temperature.fahrenheit)
    try:
        temperature.celsius = -300
    except ValueError as error:
        print("属性校验:", error)

    students = [Student("Alice", 88), Student("Bob", 95), Student("Carol", 90)]
    print("数据类排序:", sorted(students))

    first = Vector(1, 2)
    second = Vector(3, 4)
    print("魔术方法:", first + second, len(first))


if __name__ == "__main__":
    main()
