# 常用标准库模式

标准库题的重点不是背函数名，而是识别已有抽象：计数、分组、惰性流水线、Top-K、二分边界和路径
操作都有成熟工具。正确使用它们通常比手写循环更短，也更容易表达复杂度。

<p class="source-note">对应源码：<code>python/python_interview_practice/12_standard_library_patterns.py</code></p>

## 先理解模块、包与 import

一个 `.py` 文件就是模块；包含多个模块的目录通常作为包。`import` 会查找模块、执行其顶层代码，
并把模块对象绑定到当前名字。

```python
import math
from pathlib import Path

radius = 2
area = math.pi * radius**2
project_file = Path("pyproject.toml")
```

`import math` 保留了来源，阅读 `math.pi` 时能立刻知道名字来自哪里。`from module import name`
适合少量、明确且不冲突的名字；不要在业务代码中使用 `from module import *`。

模块中的这段判断可区分“直接运行”和“被导入”：

```python
def main() -> None:
    print("执行命令行入口")


if __name__ == "__main__":
    main()
```

直接运行文件时 `__name__` 是 `"__main__"`；被其他模块导入时则是模块名。把演示和命令行入口
放进 `main()`，可避免导入时意外执行网络请求、读写文件或启动服务。

## 用 pathlib 完成最小文件读写

文本文件应显式指定编码，路径拼接交给 `Path`：

```python
from pathlib import Path

output_dir = Path("output")
output_dir.mkdir(parents=True, exist_ok=True)

report = output_dir / "summary.txt"
report.write_text("通过：12\n未通过：3\n", encoding="utf-8")

content = report.read_text(encoding="utf-8")
print(content)
```

`read_text()` 会把整个文件读入内存，适合小文件。大文件应使用 `with path.open(...) as file`
逐行处理；JSON、CSV 等结构化格式则优先使用对应标准库，不要手写字符串拆分规则。

## 按问题选择工具

| 问题 | 首选工具 | 关键提醒 |
| --- | --- | --- |
| 频次统计 | `collections.Counter` | `most_common()` 直接取高频项 |
| 双端队列 | `collections.deque` | 两端增删 O(1) |
| 自动分组 | `defaultdict(list)` | 避免重复初始化 |
| 惰性组合 | `itertools` | 无限迭代器必须限制消费 |
| 缓存纯函数 | `functools.cache` | 参数必须可哈希，注意生命周期 |
| Top-K | `heapq.nlargest` | 不必完整排序 |
| 有序边界 | `bisect_left/right` | 查找 O(log n)，列表插入仍 O(n) |
| 路径处理 | `pathlib.Path` | 不手写路径分隔符 |

## itertools 组合惰性流水线

```python
from itertools import chain, islice

pages = [["A", "B"], ["C"], ["D", "E"]]
flattened = chain.from_iterable(pages)
first_three = list(islice(flattened, 3))
```

迭代器只在消费时产生元素，适合大数据流。`count()`、`cycle()`、`repeat()` 可能无限，必须用
`islice()`、条件或外部协议限制，否则 `list(iterator)` 永远不会结束。

### groupby 只合并连续相同 key

```python
from itertools import groupby
from operator import itemgetter

ordered = sorted(records, key=itemgetter("team"))
groups = {
    team: list(rows)
    for team, rows in groupby(ordered, key=itemgetter("team"))
}
```

它不是 SQL 的全局 `GROUP BY`。若相同 key 在输入中不连续，必须先按同一 key 排序，或改用
`defaultdict`。

## Counter、deque 与 ChainMap

`Counter` 是频次字典，支持集合式加减交并；`deque` 适合队列和滑动窗口；`ChainMap` 以只读视角
组合多层配置。

```python
from collections import ChainMap

config = ChainMap(command_line, environment, defaults)
timeout = config["timeout"]  # 从左到右查找
```

写入默认落到第一个映射，因此它适合覆盖层查找，不等同于把多个字典深度合并。

## functools 复用函数行为

`cache` / `lru_cache` 通过记忆参数到结果，减少重复计算：

```python
from functools import cache


@cache
def fibonacci(number: int) -> int:
    if number < 2:
        return number
    return fibonacci(number - 1) + fibonacci(number - 2)
```

缓存要求参数可哈希，并会延长返回对象生命周期。对无界输入、依赖外部状态或需要过期的数据，
不能无脑使用永久 cache。

`partial()` 固定部分参数；`singledispatch` 根据第一个参数运行时类型选择实现。它们适合公开的
行为变化，不应替代清晰的领域对象设计。

## heapq 与 Top-K

堆只保证根节点最小，不保证底层列表完全有序。维护大小为 k 的堆，可以把 Top-K 从完整排序的
O(n log n) 降到 O(n log k)。

优先队列中若任务本身不可比较，可加入单调序号打破相同优先级：

```python
(priority, sequence_number, task)
```

## bisect 查找边界

`bisect_left(values, target)` 返回目标左边界，`bisect_right` 返回右边界。它们适合有序区间映射，
但在 list 中间插入仍需移动元素，所以 `insort()` 总体是 O(n)。

## pathlib 区分纯路径和真实文件

`PurePath` 只做路径运算，不访问文件系统；`Path` 可以读写、遍历和检查状态。使用 `/` 运算符拼接
路径，比手写 `"/"` 更跨平台、更清楚。

## datetime 与时区

时间处理应区分 naive datetime 与 aware datetime。跨系统时间戳通常使用 UTC 保存，在显示边界再
转换到用户时区：

```python
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

created_at = datetime.now(UTC)
shanghai = created_at.astimezone(ZoneInfo("Asia/Shanghai"))
```

不要手工给本地时间加 8 小时，也不要用固定 offset 代替具有夏令时规则的 IANA 时区。持续时间应
使用 monotonic clock 测量，避免系统时钟校准导致结果倒退。

## Decimal、Fraction 与精确计算

`decimal.Decimal` 适合十进制金额与可控舍入，`fractions.Fraction` 适合精确有理数。Decimal 应从
字符串构造：

```python
from decimal import Decimal, ROUND_HALF_UP

amount = Decimal("19.90")
tax = (amount * Decimal("0.06")).quantize(
    Decimal("0.01"),
    rounding=ROUND_HALF_UP,
)
```

具体舍入模式是业务规则，不能默认所有金额都使用同一种“四舍五入”。

## enum、dataclasses 与结构化值

Enum 为有限状态提供名字和身份，dataclass 减少值对象样板代码。需要 JSON 序列化时要明确传输的是
枚举名称还是值；需要跨版本兼容时，也要考虑未知新状态如何处理。

## json 与不可信输入

`json.loads()` 只把文本解析成 dict/list/数字等基础结构，不验证业务字段。解析之后仍需 Schema 或
显式校验。`pickle` 能恢复复杂 Python 对象，但反序列化不可信 pickle 可执行任意代码，不能用作
公开接口数据格式。

## 常见误区

### 标准库实现一定最适合

工具只解决特定抽象。数据已经在数据库中时，先在 SQL 聚合通常比全部拉到 Python 再 Counter 更好。

### 惰性迭代器可以随时重复读取

多数迭代器是一次性的。需要多次遍历时应重新创建、显式缓存，或使用可迭代容器。

### 堆列表就是排序结果

只有 `heap[0]` 的最小值保证成立。要按序取出必须逐个 `heappop()`，这会破坏原堆。

## 面试时怎么表述

> 我先识别问题模式再选标准库：Counter 做计数，deque 做两端队列，itertools 组合惰性流水线，
> heapq 做 Top-K，bisect 找有序边界。选择后仍会说明一次性迭代、缓存生命周期和真实复杂度，
> 不把标准库名称当成结论。
