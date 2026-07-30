# Python 常用标准库

Python 安装完成后会同时提供一组标准库。路径处理、JSON 编解码、计数、队列、日期时间、精确小数、
迭代器组合和缓存等常见需求，通常不需要另外安装第三方包。

标准库模块很多，不必逐个背诵。更实用的方法是把常见问题与模块对应起来，并理解工具的输入、输出和
边界。

<p class="source-note">对应源码：<code>python/python_interview_practice/12_standard_library_patterns.py</code></p>

## 本章内容

- [模块、包与 import](./08-standard-library-patterns/modules-and-imports)：
  组织 Python 代码，理解模块执行时机、包结构和导入路径。
- [路径与 JSON 文件读写](./08-standard-library-patterns/paths-and-json)：
  使用 pathlib 处理路径，并用 JSON 保存和读取基础数据。
- [collections 常用容器工具](./08-standard-library-patterns/collections-tools)：
  使用 Counter、defaultdict、deque、ChainMap 和 namedtuple 处理常见容器模式。
- [日期时间与时区](./08-standard-library-patterns/datetime)：
  正确表示时间点、时区和时长。
- [Decimal 精确十进制计算](./08-standard-library-patterns/decimal)：
  避免二进制浮点误差并明确舍入规则。
- [itertools 惰性迭代工具](./08-standard-library-patterns/itertools)：
  截取、连接、累计、组合和分组迭代器。
- [heapq 与 bisect](./08-standard-library-patterns/heapq-and-bisect)：
  维护优先级、查找 Top-K 和有序列表边界。
- [functools 函数工具](./08-standard-library-patterns/functools)：
  缓存函数、固定参数、归约和按类型分派。
- [tempfile 与工具选择](./08-standard-library-patterns/tempfile-and-guide)：
  安全创建临时文件，并按常见需求选择标准库模块。
