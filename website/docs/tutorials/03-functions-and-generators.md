# 函数、闭包与生成器

Python 的函数不只是“可以调用的一段代码”，它本身也是对象；生成器则是在函数对象和执行帧之间
再加了一种可暂停的执行状态。理解这两点，闭包、装饰器和惰性迭代就能连成一条线。

<p class="source-note">对应源码：<code>python/python_interview_practice/02_functions_scope.py</code>、<code>python/python_interview_practice/04_iterators_generators.py</code></p>

## 先掌握定义、调用和返回值

`def` 创建函数对象，函数体只有在调用时才执行。参数把调用方的数据带入函数，`return` 结束调用并
把结果交还给调用方；没有显式 `return` 时，结果是 `None`。

```python
def calculate_total(price: float, quantity: int = 1) -> float:
    """计算商品总价。"""
    return price * quantity


single = calculate_total(19.9)
multiple = calculate_total(price=19.9, quantity=3)

print(single, multiple)
```

```text
19.9 59.699999999999996
```

这个输出也提醒我们：函数逻辑正确不代表 `float` 适合金额。生产代码应使用 `Decimal` 或整数分，
数值模型要和业务精度要求一致。

调用时要区分位置参数和关键字参数。关键字参数更容易读，但一个位置参数之后不能再出现普通位置
参数：

```python
calculate_total(19.9, quantity=3)  # 合法
# calculate_total(price=19.9, 3)   # SyntaxError
```

短小、单表达式的函数可以写成 `lambda`，例如 `sorted(rows, key=lambda row: row["score"])`。
一旦需要分支、异常处理或清晰文档，就使用普通 `def`。

## 函数是一等对象

函数可以被变量引用、作为参数传入、作为返回值返回，也可以放进容器。

```python
def greet(name: str) -> str:
    return f"你好，{name}"


formatter = greet
callbacks = [greet, str.upper]

print(formatter("小林"))
print(callbacks[1]("python"))
```

`formatter = greet` 没有调用函数，只是让另一个名字指向同一个函数对象。真正调用需要括号。
高阶函数、回调和装饰器都建立在这个基础上。

## 参数绑定发生在函数体之前

Python 调用时会先把实参绑定到形参，绑定失败时函数体一行都不会执行。常见参数种类为：

```python
def request(
    method,                 # 位置或关键字参数
    url,
    /,                      # 前面只能按位置传
    timeout=3,
    *,                      # 后面只能按关键字传
    retries=0,
    **metadata,
):
    ...
```

`*args` 收集额外位置参数为 tuple，`**kwargs` 收集额外关键字参数为 dict。`/` 和 `*` 能把公开
API 的调用方式固定下来，避免参数名变更意外成为兼容性承诺。

默认值在定义函数时计算一次；实参表达式则在调用前、从左到右求值。参数绑定细节可以通过
`inspect.signature()` 观察，装饰器也应尽量保留原签名。

## 闭包保存词法作用域

内部函数会记住定义位置可见的自由变量，即使外部函数已经返回。

```python
def make_multiplier(factor: int):
    def multiply(value: int) -> int:
        return value * factor

    return multiply


double = make_multiplier(2)
print(double(5))  # 10
```

`factor` 不是每次调用时临时猜出来的，而是保存在闭包 cell 中。若要在内部函数里重新绑定它，
需要 `nonlocal factor`；如果只是读取，什么都不用声明。

### LEGB 与赋值规则

名字解析通常按 Local、Enclosing、Global、Builtins 搜索。只要函数体中存在对某名字的赋值，
该名字默认就是局部变量，即使赋值语句位于读取之后：

```python
count = 10


def broken():
    print(count)  # UnboundLocalError
    count = 11
```

`global` 让赋值绑定模块级名字，`nonlocal` 让赋值绑定最近的外层函数作用域。二者都应谨慎使用；
显式返回新状态或封装成对象通常更易测试。

### 装饰器是闭包的工程化应用

```python
from collections.abc import Callable
from functools import wraps


def trace(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("调用前")
        result = func(*args, **kwargs)
        print("调用后")
        return result

    return wrapper
```

`wrapper` 通过闭包保存 `func`，再替代原函数对外暴露。`@wraps(func)` 会保留名称、文档字符串
等元数据，不只是“为了好看”。

带参数装饰器实际上多一层函数：`@retry(attempts=3)` 先执行 `retry(attempts=3)` 得到真正装饰器，
再把目标函数传入。多个装饰器从下到上应用，调用时则从最外层包装进入。

## 生成器保存执行帧

函数体中出现 `yield` 后，调用函数只会创建生成器对象，不会立即执行函数体。每次 `next()`
让它从上次暂停的位置继续，遇到下一个 `yield` 再暂停。

```python
def fibonacci():
    left, right = 0, 1
    while True:
        yield left
        left, right = right, left + right
```

<GeneratorFrame />

### 暂停时保存了什么

生成器暂停时会保留：

- 当前执行位置，也就是下一次应该从哪里继续；
- 局部变量和对外部对象的引用；
- 异常处理、`finally` 等执行上下文。

它不会提前把所有结果放进列表，因此适合流式数据和大规模序列。但“惰性”不等于“免费”：
每个生成器仍有执行帧开销，反复切换也会消耗时间。

### `send()`、`throw()` 与 `close()`

生成器不仅能向外 `yield`，还可以接收调用方送回的值：

```python
def accumulator():
    total = 0
    while True:
        value = yield total
        total += value


generator = accumulator()
next(generator)       # 先推进到第一个 yield
generator.send(3)     # 返回 3
generator.send(4)     # 返回 7
```

`throw()` 在暂停点注入异常，`close()` 注入 `GeneratorExit`。生成器中的 `finally` 会在正常耗尽、
关闭或垃圾回收时尝试执行，但资源管理仍应优先使用显式 `with`，不要依赖回收时机。

## 可迭代对象、迭代器和生成器

三者不要混为一谈：

- **可迭代对象**：能通过 `iter(obj)` 得到迭代器，例如列表；
- **迭代器**：实现 `__next__()`，每次返回下一个值，耗尽时抛出 `StopIteration`；
- **生成器**：由生成器函数或生成器表达式产生，是一种自动实现迭代器协议的对象。

```python
values = [10, 20]
iterator = iter(values)

next(iterator)  # 10
next(iterator)  # 20
next(iterator)  # 抛出 StopIteration
```

列表通常可以重复迭代；迭代器和生成器通常是一次性的。对同一个生成器第二次 `for` 循环，
不会自动从头开始。

## `yield from` 在做什么

`yield from iterable` 不只是把一个 `for` 循环写短。它会把值、异常和 `send()` 通道委托给
子迭代器，并接收子生成器 `return` 携带的结果。普通数据管道只需要记住“逐个转发”；涉及
协作式生成器时，才需要完整协议。

## 常见误区

### 创建生成器就会执行函数体

不会。直到第一次 `next()` 或进入 `for` 循环，函数体才开始执行。这也是为什么参数校验放在
生成器函数体开头时，异常可能比调用点更晚出现。

### `return value` 会再产出一个值

生成器中的 `return value` 会结束迭代，并把 `value` 放进 `StopIteration.value`，不会像
`yield value` 一样成为普通迭代元素。

### 生成器一定比列表更快

生成器的主要优势是惰性和低峰值内存，不保证单次遍历更快。数据量很小、需要重复读取或随机访问时，
列表可能更简单。

## 面试时怎么表述

> 函数在 Python 中是一等对象，因此可以被传递和返回；闭包让内部函数保留定义作用域中的自由变量。
> 生成器则把执行帧保留下来，每次 `next()` 从上次 `yield` 后继续，所以它能惰性地产出值，
> 但通常只能顺序消费一次。

如果继续追问实现，可以补充迭代器协议、`StopIteration`、生成器的 `send()` / `throw()` /
`close()`，但应先把“对象、状态、暂停位置”这条主线讲清楚。
