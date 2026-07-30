# Python 闭包、装饰器与递归

闭包是能够记住外层变量的函数。装饰器用一个函数包装另一个函数。递归则是函数调用自身。
这三种写法都以普通函数为基础。

<!-- 对应源码：python/python_interview_practice/02_functions_scope.py -->

## 闭包

内层函数引用外层函数的变量，并且被返回到外部后，这些变量仍会被保留。下面创建一个八折价格函数：

```python
def make_discount(discount: float):
    def apply(price: float) -> float:
        return round(price * discount, 2)

    return apply


vip_price = make_discount(0.8)
print(vip_price(100))
print(vip_price(250))
```

运行结果：

```text
80.0
200.0
```

两个结果分别是 `100 × 0.8` 和 `250 × 0.8`。虽然 `make_discount()` 已经执行结束，
返回的 `apply()` 仍能读取当时的 `discount`。这个函数和它保存的外层变量共同构成闭包。

不同调用会产生彼此独立的闭包：

```python
vip_price = make_discount(0.8)
member_price = make_discount(0.9)

print(vip_price(100))
print(member_price(100))
```

运行结果：

```text
80.0
90.0
```

## 装饰器

装饰器接收一个可调用对象，并返回另一个可调用对象。常见用途包括日志、计时、缓存和权限检查。
下面的装饰器会在函数调用前后打印信息：

```python
from functools import wraps


def trace(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        print(f"调用 {function.__name__}")
        result = function(*args, **kwargs)
        print(f"返回 {result}")
        return result

    return wrapper


@trace
def add(left: int, right: int) -> int:
    return left + right


add(2, 3)
```

运行结果：

```text
调用 add
返回 5
```

调用 `add(2, 3)` 时，实际先进入 `wrapper()`。它打印函数名，调用原来的 `add()`，再打印返回值。

`@trace` 等价于：

```python
def add(left: int, right: int) -> int:
    return left + right


add = trace(add)
```

`wrapper` 通过闭包保存原函数。`functools.wraps()` 会复制原函数的名称、文档和其他元数据；省略它会
让调试信息和自动生成的文档只看到 `wrapper`。

多个装饰器按靠近函数的顺序先应用：

```python
@outer
@inner
def process():
    pass
```

这等价于 `process = outer(inner(process))`。

## 递归函数

函数调用自身，这种写法称为递归。下面用递归计算 `5!`：

```python
def factorial(number: int) -> int:
    if number <= 1:
        return 1
    return number * factorial(number - 1)


print(factorial(5))
```

运行结果：

```text
120
```

`factorial(5)` 会依次计算 `5 × 4 × 3 × 2 × 1`，所以结果是 `120`。`number <= 1`
是终止条件；没有它，函数会不断调用自身。

Python 没有尾递归优化，递归层数也受调用栈限制。处理很深的数据时，显式 stack 和循环通常更稳妥。
