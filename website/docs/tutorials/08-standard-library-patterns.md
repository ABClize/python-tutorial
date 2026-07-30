# Python 常用标准库

Python 安装完成后会同时提供一组标准库。路径处理、JSON 编解码、计数、队列、日期时间、精确小数、
迭代器组合和缓存等常见需求，通常不需要另外安装第三方包。

标准库模块很多，不必逐个背诵。更实用的方法是把常见问题与模块对应起来，并理解工具的输入、输出和
边界。

<p class="source-note">对应源码：<code>python/python_interview_practice/12_standard_library_patterns.py</code></p>

## 本章内容

- [模块、路径与 JSON](./08-standard-library-patterns/modules-paths-and-json)：
  组织和导入 Python 模块，跨平台处理路径，并在程序之间交换基础数据。
- [collections 常用容器工具](./08-standard-library-patterns/collections-tools)：
  使用 Counter、defaultdict、deque、ChainMap 和 namedtuple 处理常见容器模式。
- [日期时间与 Decimal](./08-standard-library-patterns/datetime-and-decimal)：
  正确表示时间点、时区、时长和需要明确十进制舍入的数值。
- [itertools、heapq 与 bisect](./08-standard-library-patterns/itertools-heap-and-bisect)：
  惰性组合迭代器、查找 Top-K，并维护有序序列。
- [functools、tempfile 与工具选择](./08-standard-library-patterns/functools-tempfile-and-guide)：
  缓存函数、固定参数、按类型分派，并安全创建临时文件。
