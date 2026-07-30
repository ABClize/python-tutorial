# Python 作用域与函数对象

函数内部出现的名字从哪里查找，离开函数后局部变量为什么会消失，这些都由作用域规则决定。与此同时，函数本身也是对象，可以赋值、传参和作为返回值。本页把这两个概念连起来理解。

<p class="source-note">对应源码：<code>python/python_interview_practice/02_functions_scope.py</code></p>

## 函数的作用域

在函数内创建的名字通常是局部变量：

```python
message = "模块变量"


def show_scope() -> None:
    message = "局部变量"
    print(message)


show_scope()
print(message)
```

运行结果：

```text
局部变量
模块变量
```

Python 查找名字时遵循 LEGB 顺序：

1. Local：当前函数的局部作用域；
2. Enclosing：外层函数的作用域；
3. Global：当前模块的全局作用域；
4. Builtins：`len`、`print` 等内置名字。

内层作用域可以读取外层同名变量。函数中只要出现对某个名字的赋值，Python 通常就把它视为局部变量：

```python
count = 10


def read_count() -> int:
    return count


print(read_count())
```

运行结果：

```text
10
```

不要把变量命名为 `list`、`str`、`sum` 等内置名字，否则同一作用域内的内置对象会被遮蔽。

## `global` 和 `nonlocal`

`global` 表示要重新绑定模块级变量：

```python
request_count = 0


def record_request() -> None:
    global request_count
    request_count += 1


record_request()
print(request_count)
```

运行结果：

```text
1
```

`nonlocal` 用于重新绑定最近一层外部函数中的变量：

```python
def make_counter():
    count = 0

    def increment(step: int = 1) -> int:
        nonlocal count
        count += step
        return count

    return increment


counter = make_counter()
print(counter())
print(counter(3))
```

运行结果：

```text
1
4
```

大量修改全局状态会让调用顺序影响结果，通常应改为参数、返回值或对象属性。`nonlocal` 常用于小型闭包，
但状态复杂时使用类会更清楚。

## 函数是一等对象

Python 函数可以赋给变量、放进容器、作为参数传入，也可以由另一个函数返回：

```python
def add_tax(price: float) -> float:
    return round(price * 1.06, 2)


def apply_rule(price: float, rule) -> float:
    return rule(price)


formatter = add_tax
print(formatter(100))
print(apply_rule(200, add_tax))
```

运行结果：

```text
106.0
212.0
```

`formatter = add_tax` 没有圆括号，表示保存函数对象；`add_tax(100)` 才是调用函数。排序的 `key`、
事件回调、中间件和装饰器都依赖这一特性。

`lambda` 可以创建只包含一个表达式的匿名函数：

```python
students = [
    {"name": "小林", "score": 82},
    {"name": "小周", "score": 91},
]

ordered = sorted(students, key=lambda student: student["score"])
print([student["name"] for student in ordered])
```

运行结果：

```text
['小林', '小周']
```

出现多步处理、分支或需要文档时，应使用普通 `def`。
