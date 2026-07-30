# Python 描述器、属性查找与 __slots__

描述器（descriptor，社区中也常译为“描述符”）是控制属性读取、赋值或删除的对象。读取
`obj.name` 时，Python 还可能检查实例字典、类属性和 `__getattr__()`。`__slots__` 则可以声明实例
允许使用的属性。

<!-- 对应源码：python/python_interview_practice/10_data_model_descriptors.py -->

## 描述器

描述器定义 `__get__()`、`__set__()` 或 `__delete__()`。它放在类属性上，可以复用属性访问规则。
下面用一个描述器校验工资和奖金都不能为负数：

```python
class NonNegativeNumber:
    def __set_name__(self, owner, name: str) -> None:
        self.public_name = name
        self.storage_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance, value: int | float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{self.public_name} 必须是数字")
        if value < 0:
            raise ValueError(f"{self.public_name} 不能为负数")
        setattr(instance, self.storage_name, value)


class Employee:
    salary = NonNegativeNumber()
    bonus = NonNegativeNumber()

    def __init__(self, salary: int, bonus: int = 0) -> None:
        self.salary = salary
        self.bonus = bonus


employee = Employee(12_000, 2_000)
print(employee.salary, employee.bonus)
```

运行结果：

```text
12000 2000
```

创建实例时，两个赋值都会经过 `__set__()`。结果是 `12000 2000`。
`__set_name__()` 在创建 `Employee` 类时收到属性名，使同一个描述器类能够用于 `salary` 和
`bonus`。`property` 本身也是描述器。

## 数据描述器与非数据描述器

- 定义了 `__set__()` 或 `__delete__()` 的对象是数据描述器；
- 只定义 `__get__()` 的对象是非数据描述器。

数据描述器优先于同名实例属性。非数据描述器可以被同名实例属性遮蔽。下面先读取非数据描述器，
再给实例设置同名属性：

```python
class DisplayName:
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return f"{owner.__name__}<{instance.name}>"


class Profile:
    display_name = DisplayName()

    def __init__(self, name: str) -> None:
        self.name = name


profile = Profile("Ada")
print(profile.display_name)

profile.display_name = "实例自己的名称"
print(profile.display_name)
```

运行结果：

```text
Profile<Ada>
实例自己的名称
```

普通函数也是非数据描述器。访问 `instance.method` 时，函数的 `__get__()` 返回绑定方法，这就是实例
方法会自动收到 `self` 的基础机制。

## 属性查找与 `__getattr__()`

读取 `obj.name` 时，简化后的查找顺序是：

1. 类及基类中的数据描述器；
2. 实例的 `__dict__`；
3. 类及基类中的普通属性和非数据描述器；
4. 常规查找失败后调用 `__getattr__()`。

`__getattr__()` 可以为缺失属性提供动态值。下面优先读取用户覆盖值，否则读取默认值：

```python
class Settings:
    defaults = {"theme": "light", "language": "zh-CN"}

    def __init__(self, **overrides: str) -> None:
        self._overrides = overrides

    def __getattr__(self, name: str) -> str:
        if name in self._overrides:
            return self._overrides[name]
        if name in self.defaults:
            return self.defaults[name]
        raise AttributeError(f"没有属性 {name!r}")


settings = Settings(language="en-US")
print(settings.language)
print(settings.theme)
```

运行结果：

```text
en-US
light
```

找不到属性时必须抛出 `AttributeError`，这样 `hasattr()`、调试器和框架才能正确识别失败。
`__getattribute__()` 会拦截几乎所有属性读取，容易造成无限递归，通常不应为简单默认值重写它。

## `__slots__`

类可以使用 `__slots__` 声明允许的实例属性。下面的 `Point` 只声明 `x` 和 `y`：

```python
class Point:
    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


point = Point(1, 2)
print(point.x, point.y)
```

运行结果：

```text
1 2
```

没有额外设置时，这类实例通常不再拥有普通 `__dict__`，大量小实例可能节省内存，也会阻止随意添加
新属性。`__slots__` 会影响继承、弱引用和序列化，不能只把它当作“禁止拼错属性”的开关。

## 面向对象使用注意事项

- 类适合组织长期存在的状态和与状态紧密相关的行为；简单数据变换通常用函数即可。
- 可变实例属性应在 `__init__()` 或 `default_factory` 中创建。
- property 不应隐藏数据库、网络等昂贵副作用。
- 继承用于可替代关系，复用实现不一定需要继承。
- `super()` 沿 MRO 查找下一个实现，不固定指向某个父类。
- 特殊方法要符合 Python 对它规定的通常行为。
- 值相等、可变性和哈希必须一起设计。
- 描述器适合复用属性规则；只校验一个字段时，property 通常更简单。
