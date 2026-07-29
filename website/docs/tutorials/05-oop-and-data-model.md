# 面向对象与 Python 数据模型

Python 的面向对象不只是 `class`、继承和封装。更重要的是对象如何参与语言协议：属性查找、
迭代、比较、运算符、上下文管理器都由数据模型中的特殊方法连接。

<p class="source-note">对应源码：<code>python/python_interview_practice/05_oop_magic_methods.py</code>、<code>python/python_interview_practice/10_data_model_descriptors.py</code></p>

## 类对象与实例对象

类本身也是对象。创建实例时，Python 先通过 `__new__` 构造对象，再用 `__init__` 初始化。
普通属性通常保存在实例的 `__dict__`，类属性则由所有实例通过类共享查找。

```python
class Animal:
    category = "animal"

    def __init__(self, name: str) -> None:
        self.name = name
```

读取 `animal.category` 时，实例没有同名属性，才沿类和继承关系查找。给实例赋值
`animal.category = "pet"` 通常只是创建同名实例属性，不会修改类属性。

### `__new__` 与 `__init__` 分工

`__new__` 接收类并返回实例，负责“创建”；`__init__` 接收已经创建的实例，负责“初始化”，返回值
必须是 `None`。不可变类型的子类如果要改变值，通常需要在 `__new__` 中处理，因为到了
`__init__` 时值已经建立。

元类则负责创建类对象。绝大多数业务无需自定义元类；类装饰器、`__init_subclass__`、描述符和普通
工厂通常更简单。只有需要系统性控制类创建协议时，元类才值得使用。

## 组合通常比继承更直接

继承适合真实的“is-a”关系和可替换性；组合适合“has-a”关系，让对象把工作委托给明确依赖。

```python
class CheckoutService:
    def __init__(self, inventory, payment) -> None:
        self.inventory = inventory
        self.payment = payment
```

组合能让依赖更容易替换和测试。为了复用几行代码而建立深继承树，通常会把状态和覆盖规则变得
难以理解。

## 实例方法、类方法和静态方法

```python
class User:
    def rename(self, name: str) -> None:
        self.name = name

    @classmethod
    def from_email(cls, email: str) -> "User":
        return cls(email.partition("@")[0])

    @staticmethod
    def valid_name(name: str) -> bool:
        return bool(name.strip())
```

- 实例方法需要对象状态；
- classmethod 接收实际调用的类，适合可继承的替代构造器；
- staticmethod 只是放在类命名空间中的普通函数。

如果函数与类状态完全无关，也不构成该类型的明确概念，放在模块级通常更自然。

## property 把属性访问变成协议

`property` 允许保留 `temperature.celsius` 的读取形式，同时在赋值时校验不变量。

```python
class Temperature:
    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("温度不能低于绝对零度")
        self._celsius = value
```

`property` 本身是一种数据描述符。描述符把属性访问逻辑放在类成员中，可复用于多个字段；
ORM 字段、校验字段和绑定方法都建立在同一机制上。

## 属性查找顺序

对 `instance.name` 的常见查找可以压缩为：

<div class="concept-map">
  <div class="concept-step"><small>类及 MRO</small><strong>数据描述符</strong></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>实例自身</small><code>__dict__</code></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>类及 MRO</small><strong>普通属性 / 非数据描述符</strong></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>仍未找到</small><code>__getattr__</code></div>
</div>

数据描述符定义了 `__set__` 或 `__delete__`，优先于实例字典；只有 `__get__` 的非数据描述符
可以被同名实例属性遮蔽。

## MRO 与 `super()`

多继承使用 C3 算法生成方法解析顺序。`super()` 的准确含义是“沿当前 MRO 寻找下一个实现”，
不是固定调用某个父类。

```python
class Diamond(Left, Right):
    def trace(self) -> list[str]:
        return ["Diamond", *super().trace()]


Diamond.mro()
# [Diamond, Left, Right, Root, object]
```

合作式多继承要求链上的方法使用兼容签名，并继续调用 `super()`，否则链可能被提前截断。

## 特殊方法让对象融入语法

| 语法 | 对应协议 |
| --- | --- |
| `repr(obj)` | `obj.__repr__()` |
| `len(obj)` | `obj.__len__()` |
| `for x in obj` | `iter(obj)` / `obj.__iter__()` |
| `obj[key]` | `obj.__getitem__(key)` |
| `left + right` | `left.__add__(right)`，必要时尝试反向方法 |
| `if obj` | `obj.__bool__()` 或 `obj.__len__()` |

运算符遇到不支持的类型时通常返回 `NotImplemented`，让 Python 尝试对方的反向协议；直接抛异常
会过早终止协商。

## dataclass 解决样板代码

`@dataclass` 自动生成 `__init__`、`__repr__` 和可选比较方法，适合主要承载数据且不变量清晰的对象。
业务行为丰富的领域对象也可以使用 dataclass，但不应因此退化成没有行为的数据袋。

`frozen=True` 会阻止普通属性赋值，但并不会递归冻结字段指向的可变对象；`slots=True` 减少实例
字典开销；`field(default_factory=list)` 防止共享可变默认值。排序字段、展示字段和初始化字段
可以分别用 `compare`、`repr`、`init` 控制。

## 抽象基类与 Protocol

抽象基类适合需要共享实现、运行时注册或强制继承关系的框架；Protocol 适合只描述调用方需要的
结构能力。两者都能表达接口，但耦合方式不同：

- ABC：名义子类型，类型明确声明“我是这个家族”；
- Protocol：结构子类型，只要成员满足即可；
- 普通鸭子类型：完全在运行时约定，最灵活也最晚发现错误。

设计依赖边界时，优先暴露调用方实际需要的最小接口，避免一个庞大基类迫使所有实现携带无关方法。

## `__slots__` 不只是性能开关

`__slots__` 声明实例允许的属性存储，通常取消 `__dict__`，从而减少大量实例的内存。但继承链、
弱引用、序列化和动态属性行为都会受影响。它首先改变对象布局协议，其次才可能带来性能收益。

## 常见误区

### 下划线属性就是强制私有

单下划线是协作约定；双下划线主要触发名称改写，避免子类无意冲突，并非安全边界。

### 定义 `__eq__` 后对象仍可安全哈希

可变对象有值相等语义时，通常不应作为哈希 key。只有相等所依赖的状态不可变，才适合同时定义
一致的 `__hash__`。

### `super()` 就是父类

它依赖调用位置和实际对象的 MRO。在菱形继承中，下一个实现可能是兄弟分支，而不是源码中直观的
“父类”。

## 面试时怎么表述

> Python 对象通过数据模型协议参与语言语法。属性查找会考虑描述符、实例字典和 MRO；
> `super()` 沿 MRO 调用下一个实现。设计上优先组合，只有存在稳定可替换关系时使用继承，
> 特殊方法则应遵守对应协议的返回值和错误语义。
