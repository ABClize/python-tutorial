# Python 封装、property 与组合

封装把对象的内部状态和操作状态的方法放在一起。单下划线表示内部属性，`property` 可以在属性赋值时
校验数据，组合则让一个对象使用另一个对象的功能。

<!-- 对应源码：python/python_interview_practice/05_oop_magic_methods.py -->

## 封装与命名约定

Python 没有 Java 风格的强制私有属性。单下划线表示“内部使用”的约定。下面把余额保存为内部属性：

```python
class Account:
    def __init__(self, balance: int) -> None:
        self._balance = balance

    def deposit(self, amount: int) -> None:
        self._balance += amount
```

外部代码技术上仍能访问 `_balance`，但调用者应把它视为非公开实现，不应依赖这个属性名。

双下划线会触发名称改写。下面查看实例实际保存的属性名：

```python
class Account:
    def __init__(self) -> None:
        self.__token = "secret"


account = Account()
print(account.__dict__)
```

运行结果：

```text
{'_Account__token': 'secret'}
```

名称改写主要用于避免子类意外覆盖，不是安全边界。敏感数据不能依赖下划线保护。

## property

property 允许外部继续使用属性语法，同时在读取或写入时执行规则。下面校验摄氏温度不能低于绝对零度，
并提供只读的华氏温度：

```python
class Temperature:
    def __init__(self, celsius: float) -> None:
        self.celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("温度不能低于绝对零度")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        return self.celsius * 9 / 5 + 32


temperature = Temperature(25)
print(temperature.celsius)
print(temperature.fahrenheit)
```

运行结果：

```text
25
77.0
```

摄氏温度是 `25`，换算后的华氏温度是 `77.0`。初始化中的 `self.celsius = celsius` 也会经过
setter，因此创建和后续修改使用同一条校验规则。
只有 getter 而没有 setter 的 property 是只读属性：

```python
# temperature.fahrenheit = 80
# AttributeError: property 'fahrenheit' of 'Temperature' object has no setter
```

property 适合快速、无明显副作用的计算和校验。数据库查询、网络请求或耗时处理应写成显式方法，避免
一个看似普通的属性访问产生昂贵操作。

## 组合

组合表示一个对象持有或使用另一个对象。下面让课程对象使用通知器发送报名消息：

```python
class ConsoleNotifier:
    def send(self, message: str) -> None:
        print(message)


class Course:
    def __init__(self, name: str, notifier: ConsoleNotifier) -> None:
        self.name = name
        self.notifier = notifier

    def enroll(self, student: str) -> None:
        self.notifier.send(f"{student} 已报名 {self.name}")


course = Course("Python", ConsoleNotifier())
course.enroll("小林")
```

运行结果：

```text
小林 已报名 Python
```

调用 `course.enroll("小林")` 时，课程把消息交给通知器，最终打印报名结果。

`Course` 与通知器是“uses-a”关系，而不是“is-a”关系，所以组合比继承更符合含义。组合也便于替换为
邮件通知器、测试替身或其他实现。
