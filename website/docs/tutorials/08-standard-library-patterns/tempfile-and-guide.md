# Python tempfile 与标准库工具选择

`tempfile` 用于安全创建临时文件和临时目录。系统会生成不重复的名称，退出上下文管理器时还能自动
清理。页面后半部分列出常见需求对应的标准库模块。

<p class="source-note">对应源码：<code>python/python_interview_practice/12_standard_library_patterns.py</code></p>

## tempfile 临时目录

测试和中间处理不要手工使用固定临时文件名。下面创建一个临时目录，在其中写入并读取文件：

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as directory:
    root = Path(directory)
    path = root / "result.txt"
    path.write_text("完成", encoding="utf-8")
    print(path.read_text(encoding="utf-8"))
```

运行结果：

```text
完成
```

离开 `with` 后临时目录及其内容被清理。需要保留结果时，应在退出前复制到长期目录。

## 常见需求对应的标准库

| 问题 | 优先考虑 |
| --- | --- |
| 路径拼接和文件状态 | `pathlib` |
| JSON 数据交换 | `json` |
| 频次统计 | `collections.Counter` |
| 按 key 收集值 | `collections.defaultdict` |
| 队列和最近记录 | `collections.deque` |
| 多层配置查找 | `collections.ChainMap` |
| 时间点、时区和时长 | `datetime`、`zoneinfo` |
| 十进制计算 | `decimal` |
| 惰性迭代组合 | `itertools` |
| Top-K 和优先队列 | `heapq` |
| 有序列表边界 | `bisect` |
| 缓存和参数适配 | `functools` |
| 临时文件和目录 | `tempfile` |

## 标准库使用注意事项

- 标准库提供通用能力，不会自动完成业务校验。
- 惰性迭代器通常只能消费一次。
- `sys.getsizeof()` 只给出浅层大小。
- `heapq` 的内部列表是堆，不是已排序列表。
- `bisect` 只适用于按同一规则排序的数据。
- 无界缓存和无界队列会造成内存持续增长。
- 先检查标准库和项目已有实现；功能确实不够时，再比较第三方包。
