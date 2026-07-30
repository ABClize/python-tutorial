# Python functools、tempfile 与工具选择

`functools` 提供缓存、参数固定和单分派等函数工具，`tempfile` 安全创建临时文件与目录。本页也整理
常见问题与标准库模块的对应关系。

<p class="source-note">对应源码：<code>python/python_interview_practice/12_standard_library_patterns.py</code></p>

## cache 与 lru_cache

缓存可以避免对相同参数重复计算：

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

`singledispatch` 根据第一个参数的运行时类型选择实现：

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

## tempfile 临时目录

测试和中间处理不要手工使用固定临时文件名：

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as directory:
    root = Path(directory)
    path = root / "result.txt"
    path.write_text("完成", encoding="utf-8")
    print(path.read_text(encoding="utf-8"))
```

运行结果：

```text
完成
```

离开 `with` 后临时目录及其内容被清理。需要保留结果时，应在退出前复制到长期目录。

## 常见需求与标准库

| 问题 | 优先考虑 |
| --- | --- |
| 路径拼接和文件状态 | `pathlib` |
| JSON 数据交换 | `json` |
| 频次统计 | `collections.Counter` |
| 按 key 收集值 | `collections.defaultdict` |
| 队列和最近记录 | `collections.deque` |
| 多层配置查找 | `collections.ChainMap` |
| 时间点、时区和时长 | `datetime`、`zoneinfo` |
| 十进制计算 | `decimal` |
| 惰性迭代组合 | `itertools` |
| Top-K 和优先队列 | `heapq` |
| 有序列表边界 | `bisect` |
| 缓存和参数适配 | `functools` |
| 临时文件和目录 | `tempfile` |

## 标准库使用注意事项

- 标准库提供通用能力，不会自动完成业务校验。
- 惰性迭代器通常只能消费一次。
- `sys.getsizeof()` 只给出浅层大小。
- `heapq` 的内部列表是堆，不是已排序列表。
- `bisect` 只适用于按同一规则排序的数据。
- 无界缓存和无界队列会造成内存持续增长。
- 优先检查标准库和项目已有实现，需求超出边界时再比较第三方包。
