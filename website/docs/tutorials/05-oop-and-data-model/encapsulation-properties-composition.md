# Python 封装、property 与组合

对象通常不应把内部状态毫无限制地暴露给调用者。命名约定可以表达使用边界，property 可以在读取或赋值时加入校验，组合则让一个对象通过持有其他对象来复用能力。

<p class="source-note">对应源码：<code>python/python_interview_practice/05_oop_magic_methods.py</code></p>

## 封装与命名约定

Python 没有 Java 风格的强制私有属性。单下划线表示“内部使用”的约定：

```python
class Account:
    def __init__(self, balance: int) -> None:
        self._balance = balance

    def deposit(self, amount: int) -> None:
        self._balance += amount
```

外部代码技术上仍能访问 `_balance`，但调用者应把它视为非公开实现。

双下划线会触发名称改写：

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

property 允许外部继续使用属性语法，同时在读取或写入时执行规则：

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

初始化中的 `self.celsius = celsius` 也会经过 setter，因此创建和后续修改复用同一条校验规则。
只有 getter 而没有 setter 的 property 是只读属性：

```python
# temperature.fahrenheit = 80
# AttributeError: property 'fahrenheit' of 'Temperature' object has no setter
```

property 适合快速、无明显副作用的计算和校验。数据库查询、网络请求或耗时处理应写成显式方法，避免
一个看似普通的属性访问产生昂贵操作。

## 组合

组合表示一个对象持有或使用另一个对象：

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

`Course` 与通知器是“uses-a”关系，而不是“is-a”关系，所以组合比继承更符合含义。组合也便于替换为
邮件通知器、测试替身或其他实现。
