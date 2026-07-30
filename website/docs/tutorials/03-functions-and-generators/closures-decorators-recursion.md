# Python 闭包、装饰器与递归

函数可以返回另一个函数，也可以接收函数并包装它，还可以在自己的执行过程中再次调用自己。闭包、装饰器和递归看起来不同，本质上都建立在函数对象与调用栈之上。

<p class="source-note">对应源码：<code>python/python_interview_practice/02_functions_scope.py</code></p>

## 闭包

内层函数引用外层函数的变量，并且被返回到外部后，这些变量仍会被保留：

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

`make_discount()` 已经执行结束，但返回的 `apply()` 仍能读取当时的 `discount`。函数对象与它引用的
外层环境共同构成闭包。

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

装饰器接收一个可调用对象，并返回另一个可调用对象。它适合添加日志、计时、缓存、权限检查等横切行为。

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

函数可以调用自身，这种写法称为递归：

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

递归必须有终止条件，并且每次调用都要更接近终止条件。Python 没有尾递归优化，递归层数还受调用栈
限制。遍历很深的数据时，显式 stack 和循环通常更稳妥。
