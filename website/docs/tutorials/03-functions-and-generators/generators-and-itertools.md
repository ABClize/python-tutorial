# Python 生成器与 itertools

生成器按需产生数据，不必一次把所有结果放进内存。理解 yield 如何暂停函数、next() 如何恢复执行之后，就能自然看懂生成器表达式、yield from 和 itertools 中的惰性工具。

<p class="source-note">对应源码：<code>python/python_interview_practice/04_iterators_generators.py</code></p>

## 生成器函数

函数体中出现 `yield`，它就是生成器函数：

```python
def squares(limit: int):
    for number in range(limit):
        yield number * number


generator = squares(4)
print(next(generator))
print(next(generator))
print(list(generator))
```

运行结果：

```text
0
1
[4, 9]
```

调用 `squares(4)` 只创建生成器对象。第一次 `next()` 才开始执行函数体，运行到 `yield` 后返回一个
值并暂停；下一次 `next()` 从暂停位置继续。

生成器本身就是迭代器。前两个值已经被 `next()` 消费，因此后面的 `list(generator)` 只能取得剩余的
`4` 和 `9`。

## 生成器如何暂停和继续

无限斐波那契数列无法预先做成完整列表，但可以按需计算：

```python
def fibonacci():
    left, right = 0, 1
    while True:
        yield left
        left, right = right, left + right
```

下面的图可以逐次调用 `next()`。注意当前高亮的代码行、生成器状态和局部变量
`left`、`right`：每次暂停时，这些信息都会保留在生成器的执行帧中。

<GeneratorFrame />

图中的“已挂起”不表示线程被阻塞，而是生成器把控制权交还给调用方。下一次请求值时，它才从上次
`yield` 之后继续执行。

无限生成器必须由调用方限制消费数量：

```python
from itertools import islice


print(list(islice(fibonacci(), 7)))
```

运行结果：

```text
[0, 1, 1, 2, 3, 5, 8]
```

## 生成器表达式

把列表推导式的方括号换成圆括号，可以得到生成器表达式：

```python
squares = (number * number for number in range(5))

print(squares)
print(sum(squares))
```

运行结果：

```text
<generator object <genexpr> at 0x...>
30
```

生成器表达式不会立即保存全部结果。`sum()`、`max()`、`any()` 等只需要顺序消费数据的函数经常可以
直接接收生成器表达式：

```python
total = sum(number * number for number in range(1_000))
print(total)
```

运行结果：

```text
332833500
```

数据很小且需要重复访问时，列表推导式往往更直观。生成器的主要优势是惰性计算和较低峰值内存，并不
保证单次执行更快。

## `yield from`

一个生成器要逐个转发另一个可迭代对象的元素时，可以使用 `yield from`：

```python
def flatten(groups: list[list[int]]):
    for group in groups:
        yield from group


print(list(flatten([[1, 2], [3], [4, 5]])))
```

运行结果：

```text
[1, 2, 3, 4, 5]
```

在这个例子中，`yield from group` 等价于对 `group` 循环并逐个 `yield`。对于生成器协作，
`yield from` 还会转发 `send()`、`throw()`、`close()` 和子生成器的返回值。

## `send()`、`throw()` 和 `close()`

生成器暂停在 `yield` 时，`send(value)` 可以把值送回生成器：

```python
def accumulator():
    total = 0
    while True:
        value = yield total
        total += value


generator = accumulator()
print(next(generator))
print(generator.send(3))
print(generator.send(4))
```

运行结果：

```text
0
3
7
```

生成器刚创建时没有暂停在 `yield`，所以要先调用 `next()` 或 `send(None)`。此外：

- `throw(error)` 在当前暂停位置抛入异常；
- `close()` 在暂停位置抛入 `GeneratorExit`，请求生成器结束；
- 生成器中的 `return value` 会结束迭代，`value` 保存在 `StopIteration.value` 中，不是一个
  普通迭代元素。

常规数据处理只需使用 `for`、`next()` 和 `yield`。这些双向接口适合需要协作控制的高级场景。

## `itertools` 常用工具

标准库 `itertools` 提供惰性迭代工具：

```python
from itertools import chain, islice, pairwise


print(list(chain([1, 2], [3, 4], [5])))
print(list(islice(range(100), 3, 8)))
print(list(pairwise([10, 20, 30, 40])))
```

运行结果：

```text
[1, 2, 3, 4, 5]
[3, 4, 5, 6, 7]
[(10, 20), (20, 30), (30, 40)]
```

- `chain()` 顺序连接多个可迭代对象；
- `islice()` 对迭代器做切片，不支持负数索引；
- `pairwise()` 产生相邻元素对。

这些函数通常返回迭代器。调试时可以转换成 list 查看结果，处理大量数据时则应直接顺序消费。

## 函数和生成器的注意事项

- 函数尽量只负责一件事，名称应描述结果或动作。
- 公共函数应说明输入、返回值以及可能抛出的异常。
- 不要为了省一行代码滥用 `lambda`、`*args` 或 `**kwargs`。
- 默认参数中的可变对象会被多次调用共享。
- 迭代器和生成器通常只能向前消费一次。
- 无限生成器必须由调用方设置数量、条件或超时边界。
- 需要随机访问、重复遍历或完整结果时，list 通常比生成器合适。
