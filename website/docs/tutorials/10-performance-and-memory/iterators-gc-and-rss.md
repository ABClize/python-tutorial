# 迭代器、垃圾回收与 RSS

生成器按需产生数据，不必一次保存全部结果。垃圾回收器负责处理已经无法访问的对象。RSS 表示操作系统
看到的进程驻留内存。三个概念都与内存有关，但数值不能直接互相替代。

<!-- 对应源码：python/python_interview_practice/15_performance_and_memory.py -->

## 列表会立即保存全部结果

列表推导会立即计算每一项，并把所有结果保存在列表中。下面一次生成一百万个平方数：

```python
squares = [number * number for number in range(1_000_000)]

print(squares[0])
print(squares[-1])
```

列表支持按下标访问和重复遍历，代价是创建时就要计算并保存全部结果。

## 生成器按需产生元素

生成器表达式先创建一个生成器对象，调用 `next()` 时才计算下一项：

```python
squares = (number * number for number in range(1_000_000))

print(next(squares))
print(next(squares))
```

运行结果：

```text
0
1
```

每次调用 `next()`，生成器才继续执行到下一个结果。生成器函数使用 `yield`：

```python
from collections.abc import Iterator


def square_generator(limit: int) -> Iterator[int]:
    for number in range(limit):
        yield number * number


generator = square_generator(5)
print(list(generator))
```

运行结果：

```text
[0, 1, 4, 9, 16]
```

调用 `square_generator(5)` 时，函数体还没有完整执行，只创建了保存执行状态的生成器对象。
`list(generator)` 不断调用 `next()`，直到生成器结束。

<ClientOnly>
  <MemoryGrowthChart />
</ClientOnly>

图中比较的是列表容器引用数组和生成器对象本身的浅层估算：

- 列表需要为每一项保存引用，容器大小随元素数量近似线性增长；
- 生成器保存代码执行位置和局部状态，不预先建立完整结果表；
- 图中没有递归计算列表元素对象的全部内存；
- 具体字节数取决于 Python 版本、位数和实现。

## 生成器不是无条件替代列表

生成器也有一些限制：

- 通常只能向前消费一次；
- 不支持按下标随机访问；
- 再次遍历需要重新创建；
- 惰性执行会把异常推迟到迭代时；
- 如果最终调用 `list()`、完整排序或全部缓存，仍会物化所有结果；
- 逐项暂停和恢复也有运行成本。

```python
generator = square_generator(3)

print(list(generator))
print(list(generator))
```

运行结果：

```text
[0, 1, 4]
[]
```

第二次得到空列表，是因为同一个生成器已经耗尽。需要重新遍历时，应再次调用
`square_generator(3)`。

生成器适合流水式处理：数据一项一项到达，每项处理完即可释放，并且不需要随机访问全部结果。

## CPython 主要使用引用计数

变量保存的是对象引用。CPython 中，对象引用数降为零时，通常会立即释放：

```python
records = [{"id": 1}]
alias = records

del records
print(alias)
```

运行结果：

```text
[{'id': 1}]
```

`del records` 删除的是变量绑定。`alias` 仍然引用同一个列表，因此列表不会被回收。类似地，全局
容器、缓存、未完成任务和回调都可能继续持有对象。

## 循环引用需要垃圾回收器

两个容器可以互相引用：

```python
left: dict[str, object] = {}
right: dict[str, object] = {"left": left}
left["right"] = right
```

即使删除外部变量，环内对象的引用计数也不会直接降为零。CPython 的循环垃圾回收器会寻找已经无法
从程序入口到达的引用环。

```python
import gc

collected = gc.collect()
print(collected >= 0)
```

运行结果：

```text
True
```

手动调用 `gc.collect()` 只能回收已经不可达的对象。只要某个全局缓存、队列或事件监听器仍然引用
它们，这些对象就是可达的，垃圾回收器不会把它们当作垃圾。

频繁手动收集也可能带来停顿。通常应先修正意外的长期引用，而不是把 `gc.collect()` 放进每次请求。

## 对象释放后 RSS 可能不下降

RSS 是操作系统看到的进程驻留物理内存。Python 对象释放后，内存分配器可能保留内存块，供进程后续
创建相似对象时复用，而不是立即交还操作系统。

因此可能同时出现：

- `tracemalloc` 显示 Python 对象分配已经减少；
- 业务对象数量已经回落；
- 进程 RSS 没有立即下降；
- 后续相似分配可以复用保留的内存。

这不一定是内存泄漏。真正的持续增长通常表现为：在相似负载周期后，对象、缓存、队列或 Python
分配的基线不断抬高，而且没有回落。

## 从三个方面检查内存问题

检查内存问题时，可以分别看下面三类数据：

| 层次 | 观察内容 | 常见工具或指标 |
| --- | --- | --- |
| Python 分配 | 哪些代码行增加了 Python 对象 | `tracemalloc` |
| 对象生命周期 | 哪类对象、任务、队列还在增长 | 业务计数、对象检查 |
| 进程内存 | 操作系统看到的驻留内存 | RSS、容器监控 |

如果 `tracemalloc` 与 RSS 一起增长，优先从 Python 分配快照定位。如果 RSS 增长而 Python 分配稳定，
还要检查 C 扩展、线程栈、内存映射和分配器保留。只看单个数字很难判断根因。
