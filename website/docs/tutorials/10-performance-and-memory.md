# 性能分析与内存模型

性能优化不是猜哪种写法“更 Pythonic”，而是一个证据循环：明确目标、建立基准、定位热点、修改，
再用同一基准验证。时间复杂度解释增长趋势，profiler 和内存快照解释真实程序把资源花在哪里。

<p class="source-note">对应源码：<code>python/python_interview_practice/15_performance_and_memory.py</code></p>

## 先区分四类问题

<div class="concept-map">
  <div class="concept-step"><small>是否随 n 恶化</small><strong>复杂度分析</strong></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>一次操作多快</small><strong>timeit</strong></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>时间花在哪里</small><strong>cProfile</strong></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>内存从哪增长</small><strong>tracemalloc</strong></div>
</div>

一个工具不能回答所有问题。微基准发现两种实现的局部差距，却无法模拟网络、数据库和并发负载；
复杂度很好也不保证常数、缓存命中和数据布局适合真实场景。

## timeit 避免手写计时陷阱

```python
from timeit import Timer


def best_time(function, *, repeat=5, number=1000):
    timer = Timer(function)
    return min(timer.repeat(repeat=repeat, number=number)) / number
```

多轮最小值常用于减少偶发调度噪声，但报告时应说明选择标准。比较双方必须完成相同工作，并把数据
构造、预热或 I/O 是否计入说清楚。

## cProfile 先找累计热点

`cProfile` 记录函数调用次数、函数自身时间和包含子调用的累计时间。常见阅读顺序：

1. 按 cumulative time 排序，找到真正消耗总时间的调用链；
2. 检查调用次数是否异常；
3. 再进入具体函数看算法、I/O 或对象分配；
4. 优化后用相同输入复测。

不要只优化“单次最慢函数”。一个很快但调用几百万次的函数，也可能是主要热点。

## tracemalloc 比较快照

```python
import tracemalloc

tracemalloc.start()
before = tracemalloc.take_snapshot()

records = allocate_records(10_000)

after = tracemalloc.take_snapshot()
for stat in after.compare_to(before, "lineno")[:10]:
    print(stat)
```

快照差异能把增长定位到源码行。它关注 Python 管理的分配，并不等于进程 RSS；原生扩展、内存池和
操作系统页面还需其他工具。

## 引用计数与循环垃圾回收

CPython 主要通过引用计数管理对象：引用数降到零时通常立即释放。循环引用的对象不会自然降到零，
因此还有分代垃圾回收器检测不可达环。

```python
left = {}
right = {"left": left}
left["right"] = right
```

离开作用域后，这两个 dict 仍互相引用，但循环 GC 可以回收它们。`del name` 只删除一个名字绑定，
不保证对象立即销毁；只要还有其他引用，对象就继续存活。

资源释放不能依赖 `__del__` 或垃圾回收时机。文件、连接和锁应使用上下文管理器，缓存和全局容器则
要主动管理生命周期。

## 常见“内存泄漏”来源

Python 中的泄漏往往不是无法回收，而是仍然可达：

- 无界 dict、list 或 `lru_cache(maxsize=None)`；
- 事件监听器和回调长期保存对象；
- 闭包捕获大对象；
- Task、Future 或异常 traceback 保留局部变量；
- 日志队列和生产消费速度失衡；
- C 扩展在 Python 追踪范围之外分配。

排查时同时观察对象数量、tracemalloc 快照和进程 RSS。对象已释放但 RSS 不立刻下降，可能是 Python
内存分配器保留 arena 供后续复用，不等于对象仍可访问。

## 列表与生成器的增长方式

列表先保存所有元素引用；生成器只保存执行状态并按需产生值。拖动规模观察容器本身的增长趋势：

<ClientOnly>
  <MemoryGrowthChart />
</ClientOnly>

生成器节省峰值内存，但通常只能顺序消费一次，也无法随机访问。若后续需要多次遍历或全部排序，
最终仍可能把结果物化为容器。

## 缓存是时间、空间和一致性的交换

缓存能减少重复计算或 I/O，但必须回答：

- key 是否完整表达输入；
- 值何时过期、如何失效；
- 最大容量是多少；
- 并发未命中是否会击穿下游；
- 失败或空值是否缓存；
- 多进程之间是否共享。

函数缓存适合纯函数；外部数据缓存需要 TTL、版本或主动失效策略。命中率很低且对象很大的缓存，
可能只是在浪费内存。

## `__slots__` 何时有价值

普通实例通常有独立 `__dict__`。大量结构相同的小对象可以通过 `__slots__` 或
`@dataclass(slots=True)` 省去这部分开销。

它的代价包括限制动态属性、影响某些继承和序列化用法。只有对象数量足够大且测量确认实例字典是
显著成本时，才值得引入。

## 先优化算法，再优化语句

把 list 成员查询替换为 set，可能把重复 O(n) 搜索降为平均 O(1)；这通常比把一个循环改成更短的
语法收益大。常见顺序：

1. 去掉不必要工作和重复 I/O；
2. 选择合适算法和数据结构；
3. 批量化或缓存稳定结果；
4. 最后才考虑局部实现细节。

## CPU、I/O 与并行策略

profiler 显示 CPU 热点后，选择可能包括更好算法、批处理、向量化、原生扩展或多进程；I/O 热点则
可能通过连接复用、并发、批量查询和缓存改善。把 CPU 密集函数放进更多线程，通常不会解决
CPython 字节码受 GIL 限制的问题。

优化还要关注尾延迟而不只是平均值。服务的 p95/p99 可能由 GC、锁竞争、慢查询或外部依赖长尾决定，
单次本地微基准无法覆盖这些因素。

## 常见误区

### `sys.getsizeof()` 是对象完整内存

它通常只返回浅层大小，不递归包含对象引用到的子对象。共享对象还会让简单递归重复计数。

### 生成器总是更快

它主要降低峰值内存，逐项暂停恢复也有成本。小数据、重复读取和随机访问可能更适合 list。

### 一次基准可以代表生产环境

CPU 频率、解释器版本、缓存、输入分布和系统负载都会影响结果。可复现输入和多轮测量比单个数字
更重要。

## 面试时怎么表述

> 我会先定义性能目标和输入规模，用复杂度判断增长风险；再用 timeit 测局部实现、cProfile 找累计
> 热点、tracemalloc 比较内存快照。优化后必须用同一基准复测。生成器和 slots 都是有取舍的内存
> 工具，不应在没有测量时默认使用。
