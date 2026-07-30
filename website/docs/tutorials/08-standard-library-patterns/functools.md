# Python functools 函数工具

`functools` 提供一组操作函数的工具。它可以缓存函数结果、预先固定部分参数、累计处理序列，还可以
根据第一个参数的类型选择不同实现。

<!-- 对应源码：python/python_interview_practice/12_standard_library_patterns.py -->

## cache 与 lru_cache

缓存可以避免对相同参数重复计算。下面的递归斐波那契函数会保存已经算过的结果：

```python
from functools import cache


@cache
def fibonacci(number: int) -> int:
    if number < 2:
        return number
    return fibonacci(number - 1) + fibonacci(number - 2)


print(fibonacci(10))
print(fibonacci.cache_info().currsize)
```

运行结果：

```text
55
11
```

`cache` 等价于不限制容量的 `lru_cache(maxsize=None)`。输入种类持续增长时，缓存条目也会持续增长。

适合缓存的函数通常满足：

- 相同参数得到稳定结果；
- 参数可哈希；
- 结果不会因外部数据变化而悄悄过期；
- 缓存容量和清理时机明确。

`cache_clear()` 清空缓存，`cache_info()` 查看命中、未命中和当前条目数。

## partial 固定部分参数

`partial()` 可以预先填写一部分参数。下面先固定税率，再重复计算不同价格：

```python
from functools import partial

base_two = partial(int, base=2)

print(base_two("1010"))
print(base_two("1111"))
```

运行结果：

```text
10
15
```

`partial()` 返回一个新可调用对象，预先固定部分参数。它适合把通用函数调整为回调需要的接口。

## reduce

`reduce()` 把二元函数连续应用到序列：

```python
from functools import reduce
from operator import mul

print(reduce(mul, [1, 2, 3, 4], 1))
```

运行结果：

```text
24
```

求和、最大值和连接字符串应优先使用 `sum()`、`max()`、`join()` 等专用函数。归约规则确实是核心含义
时再使用 reduce。

## singledispatch

`singledispatch` 根据第一个参数的运行时类型选择实现。下面为整数和列表分别注册处理函数：

```python
from functools import singledispatch
from typing import Any


@singledispatch
def normalize(value: Any) -> str:
    return str(value)


@normalize.register
def _(value: int) -> str:
    return f"整数:{value}"


@normalize.register
def _(value: list) -> str:
    return f"列表:{','.join(map(str, value))}"


print(normalize(7))
print(normalize(["A", "B"]))
print(normalize(2.5))
```

运行结果：

```text
整数:7
列表:A,B
2.5
```

它只根据第一个参数分派，适合同一个操作支持多个彼此独立类型的情况。业务规则分派通常更适合显式对象
接口或映射。
