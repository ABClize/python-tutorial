# Python 性能分析与内存管理

性能优化是让程序在保持正确结果的前提下运行得更快或占用更少内存。开始修改前，先测出慢在哪里、输入
有多大；修改后，再用相同条件测一次。只看代码长短，不能判断性能是否变好。

本章依次介绍 `timeit`、`cProfile`、`tracemalloc`、生成器、垃圾回收、RSS、缓存和内存增长问题。

<!-- 对应源码：python/python_interview_practice/15_performance_and_memory.py -->

## 本章内容

- [测量方法与 timeit](./10-performance-and-memory/measurement-and-timeit)：确定指标、控制测量范围并比较小段代码。
- [使用 cProfile 定位热点](./10-performance-and-memory/profiling-with-cprofile)：读懂调用次数、自身耗时和累计耗时。
- [测量 Python 内存](./10-performance-and-memory/measuring-memory)：使用 `tracemalloc`、`getsizeof()` 和 `__slots__`。
- [迭代器、垃圾回收与 RSS](./10-performance-and-memory/iterators-gc-and-rss)：理解惰性计算、引用计数、循环引用和进程内存。
- [泄漏、缓存与优化顺序](./10-performance-and-memory/leaks-caches-and-optimization)：排查持续增长并决定先优化哪里。
