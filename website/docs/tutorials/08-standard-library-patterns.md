# Python 常用标准库

Python 标准库是安装 Python 时自带的一组模块。处理命令行参数、路径、CSV、JSON、日志、计数、队列、
日期时间、精确小数、迭代器和缓存时，通常不需要再安装第三方包。

标准库模块很多，不必逐个背诵。先记住常见需求对应哪个模块，再通过短例子掌握基本用法和注意事项。

<!-- 对应源码：python/python_interview_practice/12_standard_library_patterns.py -->

## 本章内容

- [模块、命令行参数与 uv](./08-standard-library-patterns/modules-and-imports)：
  运行脚本和模块，使用 `argparse`，并通过 uv 管理项目环境。
- [路径、JSON 与 CSV 文件读写](./08-standard-library-patterns/paths-and-json)：
  使用 `pathlib` 处理路径，并用 JSON 和 CSV 保存、读取基础数据。
- [collections 常用容器工具](./08-standard-library-patterns/collections-tools)：
  使用 `Counter`、`defaultdict`、`deque`、`ChainMap` 和 `namedtuple`。
- [日期时间与时区](./08-standard-library-patterns/datetime)：
  正确表示时间点、时区和时长。
- [Decimal、math、random 与 statistics](./08-standard-library-patterns/decimal)：
  处理精确小数、数学函数、可重复伪随机数和常用统计量。
- [itertools 惰性迭代工具](./08-standard-library-patterns/itertools)：
  截取、连接、累计、组合和分组迭代器。
- [heapq 与 bisect](./08-standard-library-patterns/heapq-and-bisect)：
  维护优先队列、查找 Top-K，并在有序列表中查找插入位置。
- [functools 函数工具](./08-standard-library-patterns/functools)：
  缓存函数、固定参数、逐步合并一组值和按类型分派。
- [tempfile、logging 与标准库工具选择](./08-standard-library-patterns/tempfile-and-guide)：
  安全创建临时文件，记录分级日志，并按常见需求选择标准库模块。
