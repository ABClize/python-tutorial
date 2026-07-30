# Python 继承、MRO 与抽象基类

继承让子类使用父类的属性和方法，也允许子类重写方法。MRO 是方法解析顺序，规定多重继承时按什么顺序
查找。抽象基类用来声明子类必须实现的方法。

<!-- 对应源码：python/python_interview_practice/05_oop_magic_methods.py、python/python_interview_practice/10_data_model_descriptors.py -->

## 继承和方法重写

继承用于表达“子类是父类的一种”。下面的 `Dog` 继承 `Animal`，并重写 `speak()`：

```python
class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return "..."


class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name}：汪汪"


dog = Dog("Lucky")
print(dog.speak())
print(isinstance(dog, Animal))
```

运行结果：

```text
Lucky：汪汪
True
```

`dog.speak()` 调用子类方法，`isinstance()` 说明 `dog` 也是 `Animal` 的实例。

需要继续执行父类初始化或方法时使用 `super()`：

```python
class TrainedDog(Dog):
    def __init__(self, name: str, skill: str) -> None:
        super().__init__(name)
        self.skill = skill

    def speak(self) -> str:
        return f"{super().speak()}，会{self.skill}"


print(TrainedDog("Lucky", "握手").speak())
```

运行结果：

```text
Lucky：汪汪，会握手
```

只为复用几行实现而继承，容易把不相关的概念绑定在一起。优先检查子类能否在所有需要父类的地方正确
替代父类；不能满足时通常应使用组合。

## MRO 与 `super()`

多继承中，Python 按 MRO 查找属性。下面构造一个菱形继承结构：

```python
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
    def trace(self) -> list[str]:
        return ["Diamond", *super().trace()]


print([item.__name__ for item in Diamond.mro()])
print(Diamond().trace())
```

运行结果：

```text
['Diamond', 'Left', 'Right', 'Root', 'object']
['Diamond', 'Left', 'Right', 'Root']
```

第一行直接显示 MRO。第二行说明每个 `trace()` 都按照同一顺序调用下一个实现。
`super()` 表示沿当前 MRO 继续查找，并不简单等于“调用直接父类”。合作式多继承要求各层
方法使用兼容签名，并继续调用 `super()`。

## 抽象基类

抽象基类可以声明子类必须实现的方法。下面要求所有存储类都实现 `save()`：

```python
from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    def save(self, value: str) -> None:
        raise NotImplementedError


class MemoryStorage(Storage):
    def __init__(self) -> None:
        self.values: list[str] = []

    def save(self, value: str) -> None:
        self.values.append(value)


storage = MemoryStorage()
storage.save("Python")
print(storage.values)
```

运行结果：

```text
['Python']
```

`MemoryStorage` 实现 `save()`，所以可以创建实例并保存 `"Python"`。带未实现抽象方法的类不能实例化。
抽象基类强调显式继承关系；只关心对象是否具有某组方法时，还可以
使用结构化类型 `Protocol`，见[类型标注与 Protocol](../07-typing-and-protocols)。
