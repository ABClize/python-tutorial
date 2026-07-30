# Python collections 常用容器工具

标准库 `collections` 提供几种专用容器。`Counter` 用于计数，`defaultdict` 自动创建默认值，
`deque` 适合从两端添加和删除元素，`ChainMap` 按顺序查找多个映射。

<!-- 对应源码：python/python_interview_practice/12_standard_library_patterns.py -->

## Counter 统计次数

下面的示例统计列表中每个主题出现了多少次：

```python
from collections import Counter

topics = ["Python", "SQL", "Python", "Git", "Python", "SQL"]
counts = Counter(topics)

print(counts)
print(counts["Python"])
print(counts["Go"])
print(counts.most_common(2))
```

运行结果：

```text
Counter({'Python': 3, 'SQL': 2, 'Git': 1})
3
0
[('Python', 3), ('SQL', 2)]
```

Counter 是 dict 子类，缺少元素时返回 `0`，不会抛出 `KeyError`。

## Counter 运算

两个 `Counter` 可以相加，也可以按 key 取较小或较大的计数：

```python
from collections import Counter

left = Counter(a=3, b=1)
right = Counter(a=2, b=4)

print(left + right)
print(left & right)
print(left | right)
```

运行结果：

```text
Counter({'a': 5, 'b': 5})
Counter({'a': 2, 'b': 1})
Counter({'b': 4, 'a': 3})
```

- `+` 合并计数；
- `&` 取每个元素的较小计数；
- `|` 取每个元素的较大计数。

Counter 保留首次遇到元素的顺序；计数相同时，显示顺序也会受这个顺序影响。

## defaultdict 自动创建默认值

下面按姓名收集多个分数。第一次遇到姓名时，`defaultdict(list)` 会自动创建空列表：

```python
from collections import defaultdict

scores: defaultdict[str, list[int]] = defaultdict(list)

for name, score in [("A", 90), ("B", 80), ("A", 95)]:
    scores[name].append(score)

print(dict(scores))
```

运行结果：

```text
{'A': [90, 95], 'B': [80]}
```

第一次访问缺失 key 时，`defaultdict` 调用 `list` 创建空列表，并把 key 写入字典。

`dict.get()` 只返回默认值，不会插入 key；`defaultdict` 的缺失读取会改变字典。只查询时使用 `get()`
更合适。

## deque 双端队列

list 从头部 `pop(0)` 需要移动后续元素。先进先出队列使用 deque：

```python
from collections import deque

tasks = deque(["读取配置", "处理订单"])
tasks.append("写入日志")

while tasks:
    print(tasks.popleft())
```

运行结果：

```text
读取配置
处理订单
写入日志
```

常用操作：

| 方法 | 作用 |
| --- | --- |
| `append(value)` | 右端加入 |
| `appendleft(value)` | 左端加入 |
| `pop()` | 右端移除 |
| `popleft()` | 左端移除 |
| `extend(values)` | 右端加入多个元素 |
| `rotate(n)` | 循环移动元素 |

设置 `maxlen` 可以保存固定数量的最近记录：

```python
from collections import deque

recent = deque(["任务1", "任务2", "任务3"], maxlen=3)
recent.append("任务4")

print(list(recent))
```

运行结果：

```text
['任务2', '任务3', '任务4']
```

超过最大长度时，另一端最旧的元素自动移除。

## ChainMap 按顺序查找多个映射

下面按照“命令行、环境变量、默认值”的顺序查找配置：

```python
from collections import ChainMap

defaults = {"theme": "light", "timeout": 30}
environment = {"timeout": 10}
command_line = {"debug": True}

config = ChainMap(command_line, environment, defaults)

print(config["debug"])
print(config["timeout"])
print(config["theme"])
```

运行结果：

```text
True
10
light
```

查找从左到右进行。ChainMap 不会复制并合并字典；修改 `config[key]` 默认只写入第一个映射。

## namedtuple 轻量记录

下面定义一个有 `x`、`y` 两个字段的不可变记录：

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
point = Point(3, 4)

print(point)
print(point.x)
print(point[1])
```

运行结果：

```text
Point(x=3, y=4)
3
4
```

`namedtuple` 保留 tuple 的索引和解包能力，同时增加字段名。新代码需要类型标注、默认值和方法时，也可以
使用 `typing.NamedTuple` 或 `@dataclass(frozen=True)`。

## 怎样选择容器工具

| 需求 | 工具 |
| --- | --- |
| 统计频次 | `Counter` |
| 按 key 收集多个值 | `defaultdict(list)` |
| 先进先出或两端操作 | `deque` |
| 固定长度最近记录 | `deque(maxlen=...)` |
| 多层配置查找 | `ChainMap` |
| 轻量不可变记录 | `namedtuple` |

这些工具能减少重复代码，但仍要注意 key 不存在时的行为、元素顺序和容器容量。
