# Python 性能分析与内存管理

性能优化需要可重复的证据。修改代码前，要明确慢在哪里、输入有多大、准备观察什么指标；修改后，再
用相同条件复测。只凭感觉缩短代码，通常无法证明程序真的更快或更省内存。

本章分别介绍局部计时、函数热点分析、Python 内存追踪、生成器与垃圾回收，以及常见的长期内存增长
问题。

<p class="source-note">对应源码：<code>python/python_interview_practice/15_performance_and_memory.py</code></p>

## 本章内容

- [测量方法与 timeit](./10-performance-and-memory/measurement-and-timeit)：确定指标、控制测量范围并比较小段代码。
- [使用 cProfile 定位热点](./10-performance-and-memory/profiling-with-cprofile)：读懂调用次数、自身耗时和累计耗时。
- [测量 Python 内存](./10-performance-and-memory/measuring-memory)：使用 `tracemalloc`、`getsizeof()` 和 `__slots__`。
- [迭代器、垃圾回收与 RSS](./10-performance-and-memory/iterators-gc-and-rss)：理解惰性计算、引用计数、循环引用和进程内存。
- [泄漏、缓存与优化顺序](./10-performance-and-memory/leaks-caches-and-optimization)：排查持续增长并决定先优化哪里。
