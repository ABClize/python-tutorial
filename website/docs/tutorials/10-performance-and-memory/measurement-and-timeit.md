# 测量方法与 timeit

`timeit` 用于重复测量一小段 Python 代码。“程序很慢”还不够具体。先判断是单次请求慢、批处理完成
得少、输入变大后耗时上升，还是外部接口偶尔超时，再选择测量方法。

<p class="source-note">对应源码：<code>python/python_interview_practice/15_performance_and_memory.py</code></p>

## 先确定要测什么

| 现象 | 适合观察的指标或工具 |
| --- | --- |
| 两种局部实现谁更快 | `timeit` |
| 不知道整个程序慢在哪里 | `cProfile` |
| Python 对象持续增加 | `tracemalloc`、对象数量 |
| 进程占用的物理内存持续增加 | RSS、队列与缓存指标 |
| Web 请求偶尔很慢 | p95、p99、链路追踪 |
| 单位时间完成的工作太少 | 吞吐量 |
| 输入扩大后耗时增长过快 | 算法复杂度、分规模基准 |

这些指标不能互相替代：

- 平均延迟正常，不代表 p99 正常；
- 一段表达式的微基准很快，不代表整个服务吞吐量高；
- `tracemalloc` 中的 Python 堆稳定，不代表进程 RSS 或 C 扩展内存稳定；
- CPU 使用率低，也可能是程序正在等待网络、磁盘、连接池或锁。

## 让两次测量可以比较

性能数据依赖运行环境。一份可解释的记录至少要包含：

- Python 和主要依赖版本；
- 操作系统与硬件；
- 输入规模、内容分布和构造方式；
- 是否包含文件、网络、数据库和序列化；
- 是否预热、重复多少次、采用什么统计值；
- 修改前后的代码版本；
- 两种实现是否产生相同结果和副作用。

如果一边计入数据构造，另一边只测核心查询，数字即使精确也不能比较。

常见工作顺序是：

```text
定义指标 → 建立基准 → 定位热点 → 修改一个因素 → 复测 → 记录结果
```

## timeit 适合测量小段代码

`timeit` 会重复执行被测代码，适合小范围比较。它比只调用一次 `time.perf_counter()` 更能减少偶发
系统调度带来的影响。

```python
from timeit import Timer

numbers_list = list(range(5_000))
numbers_set = set(numbers_list)
missing = -1

list_timer = Timer(lambda: missing in numbers_list)
set_timer = Timer(lambda: missing in numbers_set)

list_times = list_timer.repeat(repeat=5, number=1_000)
set_times = set_timer.repeat(repeat=5, number=1_000)

print(len(list_times))
print(len(set_times))
print(min(list_times) >= 0)
print(min(set_times) >= 0)
```

运行结果：

```text
5
5
True
True
```

具体耗时会随机器变化，不应写成固定答案。这里可以提前分析复杂度：

- list 成员查询最坏是 O(n)；
- set 成员查询平均是 O(1)；
- set 需要额外内存，构造 set 本身是 O(n)。

上面的基准只测“容器已经准备好之后的查询”。如果真实流程只查询一次，而且每次都要先执行
`set(numbers_list)`，就应该把构造成本也计入。

## 把每次调用的最佳时间算出来

项目源码使用下面的辅助函数：

```python
import timeit
from collections.abc import Callable
from typing import Any


def best_time(
    function: Callable[[], Any],
    *,
    repeat: int = 5,
    number: int = 1_000,
) -> float:
    timer = timeit.Timer(function)
    total_seconds = min(timer.repeat(repeat=repeat, number=number))
    return total_seconds / number
```

`repeat=5` 表示进行 5 轮，`number=1_000` 表示每轮调用 1,000 次。`repeat()` 返回每轮的总用时，
除以 `number` 后得到单次调用时间。

取最小值可以减少其他进程临时抢占 CPU 造成的偶发变慢，接近当前环境下这段代码能够达到的速度。
但服务端延迟更关心真实分布，通常还要记录中位数、p95 和 p99，不能只保存最快一次。

## 字符串语句与可调用对象

`timeit` 也能执行字符串：

```python
from timeit import timeit

elapsed = timeit(
    "sum(values)",
    setup="values = list(range(100))",
    number=10_000,
)

print(elapsed >= 0)
```

运行结果：

```text
True
```

`setup` 只负责准备环境，不计入被测语句的时间。字符串适合命令行中的小实验，可调用对象则更容易
传入真实数据、复用已有函数并在计时前检查结果。

## 比较保序去重

使用列表保存已经见过的值：

```python
def unique_with_list(values: list[int]) -> list[int]:
    result: list[int] = []

    for value in values:
        if value not in result:
            result.append(value)

    return result
```

使用 set 加速查询，同时用列表保留原顺序：

```python
def unique_with_set(values: list[int]) -> list[int]:
    seen: set[int] = set()
    result: list[int] = []

    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)

    return result
```

计时前先检查两者完成的工作是否相同：

```python
data = [3, 1, 3, 2, 1]

print(unique_with_list(data))
print(unique_with_set(data))
print(unique_with_list(data) == unique_with_set(data))
```

运行结果：

```text
[3, 1, 2]
[3, 1, 2]
True
```

列表版本中的 `value not in result` 会随着 `result` 变长而变慢，最坏时间复杂度是 O(n²)。set
版本的平均时间复杂度是 O(n)，额外空间是 O(n)。这种算法级差异通常比改变循环写法更重要。

## 微基准容易犯的错误

- 只运行一次，把系统抖动当成代码差异；
- 输入太小，测到的主要是计时器和函数调用开销；
- 两种实现返回的结果不同；
- 一边包含初始化，另一边不包含；
- 测量常量输入，却把结论推广到所有输入规模；
- 为了基准删掉真实流程中的必要校验和 I/O；
- 把微秒级差异当成整个程序的主要瓶颈。

`timeit` 回答的是“在这组条件下，这小段代码运行多久”。它不能告诉我们整个程序最值得优化的是哪
个函数，定位全局热点要使用 profiler。
