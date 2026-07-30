# Python 类、实例与方法

类描述一类对象共有的数据和行为，实例则是按照这个描述创建出的具体对象。本页从最小类开始，说明初始化、实例属性、类属性，以及实例方法、类方法和静态方法分别怎样接收参数。

<p class="source-note">对应源码：<code>python/python_interview_practice/05_oop_magic_methods.py</code></p>

## 定义类和创建实例

使用 `class` 定义类：

```python
class Course:
    def __init__(self, name: str, price: float) -> None:
        self.name = name
        self.price = price
        self.students: list[str] = []

    def enroll(self, student: str) -> None:
        self.students.append(student)

    def revenue(self) -> float:
        return self.price * len(self.students)


course = Course("Python 入门", 99)
course.enroll("小林")
course.enroll("小周")

print(course.name)
print(course.students)
print(course.revenue())
```

运行结果：

```text
Python 入门
['小林', '小周']
198
```

这段代码中：

- `Course` 是类；
- `course` 是实例；
- `name`、`price` 和 `students` 是实例属性；
- `enroll()` 和 `revenue()` 是实例方法；
- `self` 表示当前正在操作的实例。

调用 `course.enroll("小林")` 时，Python 会把 `course` 自动绑定到 `self`，效果类似
`Course.enroll(course, "小林")`。

类名通常使用 `PascalCase`，方法名和属性名通常使用 `snake_case`。

## `__init__()` 与实例初始化

调用 `Course("Python 入门", 99)` 时，Python 先通过 `__new__()` 创建实例，再调用 `__init__()`
初始化已经创建的实例。

`__init__()` 不负责返回实例，也不应返回其他值：

```python
class User:
    def __init__(self, name: str) -> None:
        self.name = name
```

日常业务类通常只需实现 `__init__()`。自定义 `__new__()` 常见于不可变类型、单例控制和元类等进阶
场景。

在 `__init__()` 中创建可变属性，可以保证每个实例获得独立对象：

```python
class Course:
    def __init__(self, name: str) -> None:
        self.name = name
        self.students: list[str] = []


python_course = Course("Python")
sql_course = Course("SQL")

python_course.students.append("小林")

print(python_course.students)
print(sql_course.students)
```

运行结果：

```text
['小林']
[]
```

## 实例属性和类属性

直接写在类体中的属性是类属性：

```python
class Course:
    platform = "学习站"

    def __init__(self, name: str) -> None:
        self.name = name


python_course = Course("Python")
sql_course = Course("SQL")

print(Course.platform)
print(python_course.platform)
print(sql_course.platform)
```

运行结果：

```text
学习站
学习站
学习站
```

读取 `python_course.platform` 时，实例本身没有这个属性，Python 会继续到类中查找。

给实例赋值会创建同名实例属性，不会修改类属性：

```python
python_course.platform = "内部站点"

print(python_course.platform)
print(sql_course.platform)
print(Course.platform)
```

运行结果：

```text
内部站点
学习站
学习站
```

可变类属性会被所有未遮蔽它的实例共享：

```python
class BrokenCourse:
    students: list[str] = []


first = BrokenCourse()
second = BrokenCourse()
first.students.append("小林")

print(second.students)
```

运行结果：

```text
['小林']
```

除非业务上本来就需要共享状态，可变数据应作为实例属性在 `__init__()` 中创建。

## 实例方法、类方法和静态方法

```python
class Course:
    platform = "学习站"

    def __init__(self, name: str, price: float) -> None:
        self.name = name
        self.price = price

    def display(self) -> str:
        return f"{self.name}：{self.price} 元"

    @classmethod
    def free(cls, name: str):
        return cls(name, 0)

    @staticmethod
    def is_valid_price(price: float) -> bool:
        return price >= 0


course = Course.free("公开课")
print(course.display())
print(Course.is_valid_price(-1))
```

运行结果：

```text
公开课：0 元
False
```

| 方法 | 自动绑定的第一个参数 | 适用场景 |
| --- | --- | --- |
| 实例方法 | `self` | 读取或修改实例状态 |
| 类方法 | `cls` | 备用构造器、操作类级状态 |
| 静态方法 | 无 | 与类概念相关的无状态工具 |

类方法中的 `cls` 指向实际调用该方法的类，因此子类继承备用构造器时能够创建子类实例。一个函数既不
需要实例也不需要类，而且与类的概念关系不强时，写成模块级函数通常更清楚。
