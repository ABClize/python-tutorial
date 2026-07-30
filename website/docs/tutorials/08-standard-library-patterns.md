# Python 常用标准库

Python 标准库是安装 Python 时自带的一组模块。处理路径、JSON、计数、队列、日期时间、精确小数、
迭代器和缓存时，通常不需要再安装第三方包。

标准库模块很多，不必逐个背诵。先记住常见需求对应哪个模块，再通过短例子掌握基本用法和注意事项。

<p class="source-note">对应源码：<code>python/python_interview_practice/12_standard_library_patterns.py</code></p>

## 本章内容

- [模块、包与 import](./08-standard-library-patterns/modules-and-imports)：
  组织 Python 代码，理解模块执行时机、包结构和导入路径。
- [路径与 JSON 文件读写](./08-standard-library-patterns/paths-and-json)：
  使用 pathlib 处理路径，并用 JSON 保存和读取基础数据。
- [collections 常用容器工具](./08-standard-library-patterns/collections-tools)：
  使用 `Counter`、`defaultdict`、`deque`、`ChainMap` 和 `namedtuple`。
- [日期时间与时区](./08-standard-library-patterns/datetime)：
  正确表示时间点、时区和时长。
- [Decimal 精确十进制计算](./08-standard-library-patterns/decimal)：
  避免二进制浮点误差并明确舍入规则。
- [itertools 惰性迭代工具](./08-standard-library-patterns/itertools)：
  截取、连接、累计、组合和分组迭代器。
- [heapq 与 bisect](./08-standard-library-patterns/heapq-and-bisect)：
  维护优先队列、查找 Top-K，并在有序列表中查找插入位置。
- [functools 函数工具](./08-standard-library-patterns/functools)：
  缓存函数、固定参数、归约和按类型分派。
- [tempfile 与工具选择](./08-standard-library-patterns/tempfile-and-guide)：
  安全创建临时文件，并按常见需求选择标准库模块。
