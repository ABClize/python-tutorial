# Python tempfile、logging 与标准库工具选择

`tempfile` 用于安全创建临时文件和临时目录。系统会生成不重复的名称，退出上下文管理器时还能自动
清理。`logging` 用于按级别记录程序运行信息，比直接到处写 `print()` 更容易统一控制和保存。

<!-- 对应源码：python/python_interview_practice/12_standard_library_patterns.py -->

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

## logging 日志级别

日志级别表示消息的重要程度：

| 级别 | 常见用途 |
| --- | --- |
| `DEBUG` | 调试时查看变量、分支和执行细节 |
| `INFO` | 记录程序正常启动、完成和关键步骤 |
| `WARNING` | 程序还能继续，但出现了需要注意的情况 |
| `ERROR` | 当前操作失败 |
| `CRITICAL` | 严重错误，程序或服务可能无法继续 |

设置为 `INFO` 时，会输出 `INFO` 及以上级别，`DEBUG` 会被过滤。默认没有额外配置时，根 logger 通常
只处理 `WARNING` 及以上级别。

## getLogger 与 basicConfig

每个模块通常在顶部创建自己的 logger：

```python
import logging

logger = logging.getLogger(__name__)
```

`__name__` 会生成类似 `shop.report` 的 logger 名称。模块层级会反映在 logger 名称中，便于按模块查找
日志。

应用入口再统一配置日志：

```python
import logging

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s:%(name)s:%(message)s",
    )

    logger.debug("读取调试配置")
    logger.info("已处理 %d 条记录", 2)
    logger.warning("剩余容量为 %d%%", 20)


if __name__ == "__main__":
    main()
```

运行结果包含：

```text
INFO:__main__:已处理 2 条记录
WARNING:__main__:剩余容量为 20%
```

`DEBUG` 低于当前 `INFO` 级别，所以没有输出。`basicConfig()` 配置根 logger，通常只在程序入口调用
一次。可复用模块只创建 logger 并记录消息，不应自行决定整个应用的输出格式和目标。进程中已经存在
handler 时，再调用 `basicConfig()` 通常不会重复配置。

本项目源码中的 `logging_demo()` 没有调用 `basicConfig()`。它把 handler 临时挂到专用 logger，
写入内存后立即移除，并恢复原来的级别和传播设置，因此不会修改整个进程的日志配置。

## 参数化日志消息

日志方法支持把格式字符串和参数分开传入：

```python
logger.info(
    "已处理 %d 条记录，文件=%s",
    row_count,
    file_name,
)
```

这里使用 logging 的 `%` 占位符，但不要自己先写 `message % values`。参数分开传递时，消息通过级别
过滤后才需要格式化。`%s` 适合普通文本，`%d` 适合整数，`%r` 适合需要看清引号和转义的调试值。

## 使用 logger.exception 记录异常

`logger.exception()` 应在 `except` 代码块中使用。它会按 `ERROR` 级别记录消息，并自动附加当前异常
和 traceback：

```python
value = "three"

try:
    hours = int(value)
except ValueError:
    logger.exception(
        "无法转换小时数：value=%r",
        value,
    )
```

日志会先出现“无法转换小时数”，后面再显示 `ValueError` 的 traceback。这样既能看到业务上下文，也
能找到抛出异常的代码位置。只想记录错误消息、不需要 traceback 时，使用 `logger.error()`。

## 日志不要记录敏感信息

不要把密码、访问令牌、Cookie、Authorization 请求头、完整身份证号或支付数据写入日志。错误排查需要
关联请求时，可以记录随机请求 id、业务编号或经过脱敏的字段。

日志消息还应说明发生了什么，不要只写“失败”。例如，“读取配置失败：path=%s”比“发生错误”更容易
定位问题。

## 常见需求对应的标准库

| 问题 | 优先考虑 |
| --- | --- |
| 命令行参数 | `argparse` |
| 路径拼接和文件状态 | `pathlib` |
| JSON 数据交换 | `json` |
| CSV 表格文本 | `csv` |
| 分级日志 | `logging` |
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
- 应用入口负责日志配置，可复用模块只使用自己的 logger。
- 日志中不要记录密码、令牌和完整个人敏感信息。
- 先检查标准库和项目已有实现；功能确实不够时，再比较第三方包。
