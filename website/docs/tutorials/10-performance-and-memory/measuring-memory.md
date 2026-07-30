# 测量 Python 内存

测量 Python 内存时，要先说明测量范围。`sys.getsizeof()` 只看对象本身，`tracemalloc` 跟踪
Python 分配，RSS 则查看整个进程。三种结果不能直接当成同一个数字。

<!-- 对应源码：python/python_interview_practice/15_performance_and_memory.py -->

## tracemalloc 跟踪 Python 分配

`tracemalloc` 能记录 Python 在哪些代码行分配了内存。下面在创建一万条记录前后各拍一次快照：

```python
import tracemalloc

tracemalloc.start()
before = tracemalloc.take_snapshot()

records = [
    {"id": number, "name": f"user-{number}"}
    for number in range(10_000)
]

after = tracemalloc.take_snapshot()
differences = after.compare_to(before, "lineno")

print(len(records))
print(len(differences) > 0)

tracemalloc.stop()
```

运行结果：

```text
10000
True
```

`compare_to(before, "lineno")` 按源码行比较。查看增长最大的几项：

```python
for stat in differences[:5]:
    print(stat)
```

输出会包含文件、行号、大小变化和对象块数量。具体数字依赖 Python 版本和当前环境，不应写成固定
答案。

## 当前值、峰值和快照各看什么

追踪开始后，可以读取：

```python
current, peak = tracemalloc.get_traced_memory()
```

- `current`：当前仍被追踪的内存；
- `peak`：从 `tracemalloc.start()` 以来出现过的最高值；
- 两次快照之差：哪些源码位置增加或减少了分配。

如果任务处理中临时创建大量对象，结束后又释放，`current` 可能较低而 `peak` 很高。如果内存随每次
请求持续累积，连续快照更容易显示增长来源。

启动追踪之前已经存在的分配不会完整出现在结果中。为了比较某段操作，应该先启动追踪并取得基线
快照，再执行操作。

## 确保被测对象仍然存活

下面的函数返回记录列表，调用者持有返回值直到第二次快照完成：

```python
def allocate_records(count: int) -> list[dict[str, object]]:
    return [
        {
            "id": index,
            "name": f"user-{index}",
            "scores": [index, index + 1, index + 2],
        }
        for index in range(count)
    ]
```

如果对象在第二次快照前已经失去全部引用，它们可能已被回收，快照差异就无法反映预期增长。测量代码
本身也必须符合对象的真实生命周期。

## getsizeof 只看浅层大小

`sys.getsizeof()` 返回对象本身的浅层大小。下面比较列表和列表中第一个整数的大小：

```python
import sys

values = [1, 2, 3]

print(sys.getsizeof(values) > 0)
print(sys.getsizeof(values[0]) > 0)
```

运行结果：

```text
True
True
```

列表内部保存的是元素引用。`getsizeof(values)` 通常只包含列表对象及其引用数组，不会递归加上三个
整数对象，也不会判断这些整数是否还被其他容器共享。

因此下面两句话含义不同：

- “列表容器本身的浅层大小”可以用 `getsizeof()` 估算；
- “这批数据让进程增加了多少内存”需要结合快照、对象共享情况和进程指标。

简单地递归相加所有 `getsizeof()` 也可能重复计算共享对象，并遗漏 C 扩展中的原生分配。

## __slots__ 减少实例属性字典

普通类的实例通常使用 `__dict__` 保存动态属性：

```python
class RegularPoint:
    def __init__(self, x: int, y: int, label: str) -> None:
        self.x = x
        self.y = y
        self.label = label
```

`__slots__` 预先声明允许的属性，普通情况下不再为每个实例创建 `__dict__`：

```python
class SlottedPoint:
    __slots__ = ("x", "y", "label")

    def __init__(self, x: int, y: int, label: str) -> None:
        self.x = x
        self.y = y
        self.label = label


regular = RegularPoint(1, 2, "A")
slotted = SlottedPoint(1, 2, "A")

print(hasattr(regular, "__dict__"))
print(hasattr(slotted, "__dict__"))
```

运行结果：

```text
True
False
```

Python 3.10 及以上版本的 dataclass 可以直接启用 slots：

```python
from dataclasses import dataclass


@dataclass(slots=True)
class Point:
    x: int
    y: int
    label: str
```

slots 适合以下情况：

- 会创建大量结构相同的小对象；
- 测量确认实例字典占用显著；
- 不需要运行时动态添加属性；
- 继承、序列化和框架兼容性已经验证。

它会限制动态属性，并可能影响多重继承、弱引用、序列化和依赖 `__dict__` 的工具。只创建少量实例
时，节省的内存通常不值得增加这些约束。

## tracemalloc 看不到全部进程内存

`tracemalloc` 主要跟踪 Python 分配器管理的内存。NumPy、图像库、数据库驱动等 C 扩展可能在 Python
堆之外申请内存，线程栈、共享库和内存映射也属于进程 RSS 的一部分。

因此排查内存时常常需要同时观察：

- `tracemalloc` 当前值、峰值和快照；
- 进程 RSS；
- 业务对象、任务、队列和连接数量；
- 缓存条目数；
- 原生库自己的内存指标。

工具的可见范围不同，结果不一致并不一定表示某个工具出错。
