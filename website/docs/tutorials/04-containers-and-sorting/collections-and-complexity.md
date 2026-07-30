# Python collections 工具与容器复杂度

标准库 `collections` 提供了一些专用容器。`Counter` 用于计数，`defaultdict` 用于自动创建默认值，
`deque` 用于在两端快速添加或删除元素。

<p class="source-note">对应源码：<code>python/python_interview_practice/03_collections_copy.py</code>、<code>python/interview_exercises/collections.py</code></p>

## `Counter`

`collections.Counter` 是用于计数的 dict 子类。下面统计六个单词出现的次数：

```python
from collections import Counter


words = ["python", "java", "python", "go", "python", "go"]
counts = Counter(words)

print(counts["python"])
print(counts["rust"])
print(counts.most_common(2))
```

运行结果：

```text
3
0
[('python', 3), ('go', 2)]
```

`"python"` 出现三次，未出现的 `"rust"` 返回 `0`。`most_common(2)` 返回出现次数最多的两项。
普通 dict 读取缺失 key 会报错，而 `Counter` 对缺失元素返回计数 `0`。

## `defaultdict`

`defaultdict` 在访问缺失 key 时调用工厂函数创建默认值。下面按单词长度分组：

```python
from collections import defaultdict


groups: defaultdict[int, list[str]] = defaultdict(list)

for word in ["go", "python", "java", "sql"]:
    groups[len(word)].append(word)

print(dict(groups))
```

运行结果：

```text
{2: ['go'], 6: ['python'], 4: ['java'], 3: ['sql']}
```

`defaultdict(list)` 会为每个新长度创建空列表，然后把单词加入对应列表。它适合分组和累计。

与 `dict.get()` 不同，读取缺失 key 会把新 key 真正写入 `defaultdict`，因此不要用无意的读取来
探测 key 是否存在。

## `deque`

list 在末尾 `append()` 和 `pop()` 很快，但从头部插入或删除需要移动后续元素。双端队列
`collections.deque` 支持两端高效操作。下面从队列左侧取出第一个任务：

```python
from collections import deque


queue = deque(["任务 1", "任务 2"])
queue.append("任务 3")

print(queue.popleft())
print(list(queue))
```

运行结果：

```text
任务 1
['任务 2', '任务 3']
```

`popleft()` 返回“任务 1”，队列中还剩后两个任务。

固定长度的 deque 还可保存最近 n 项：

```python
from collections import deque


recent = deque(maxlen=3)
recent.extend([1, 2, 3, 4, 5])

print(list(recent))
```

运行结果：

```text
[3, 4, 5]
```

## 滑动窗口

deque 配合当前总和可以计算移动平均值。下面用长度为 `3` 的窗口处理五个数字：

```python
from collections import deque
from collections.abc import Iterable


def moving_average(
    values: Iterable[float],
    window_size: int,
) -> list[float]:
    if window_size <= 0:
        raise ValueError("窗口大小必须为正整数")

    window: deque[float] = deque()
    current_sum = 0.0
    averages: list[float] = []

    for value in values:
        window.append(value)
        current_sum += value

        if len(window) > window_size:
            current_sum -= window.popleft()

        if len(window) == window_size:
            averages.append(current_sum / window_size)

    return averages


print(moving_average([1, 2, 3, 4, 5], 3))
```

运行结果：

```text
[2.0, 3.0, 4.0]
```

三个窗口分别是 `[1, 2, 3]`、`[2, 3, 4]` 和 `[3, 4, 5]`，平均值为 `2.0`、`3.0`
和 `4.0`。每个元素最多入队和出队一次，时间复杂度为 O(n)，额外空间为 O(window_size)。

## 常见操作的复杂度

下面列出常见操作的平均或摊销复杂度：

| 操作 | 复杂度 |
| --- | --- |
| list 按索引读取 | O(1) |
| list 末尾追加、弹出 | 摊销 O(1) |
| list 头部插入、删除 | O(n) |
| list 按值查找 | O(n) |
| dict 按 key 查询 | 平均 O(1) |
| set 成员判断 | 平均 O(1) |
| 排序 | O(n log n) |

哈希容器通常用更多内存换取快速查询。O(1) 是平均复杂度，不表示每次操作耗时完全相同。数据量较小时，
优先选择含义准确、代码清楚的容器。

## 容器使用注意事项

- 不要在遍历 list 或 dict 时无计划地修改其长度。
- list 的原地修改方法通常返回 `None`。
- tuple 中仍可引用可变对象。
- dict key 和 set 元素必须可哈希。
- 不要依赖 set 的显示和遍历顺序。
- 需要保序去重时，应明确采用 dict 或 `seen` 算法。
- 排序复杂对象时，应通过 `key` 写清主要和次要规则。
- 大量从队列头部删除元素时，使用 deque 而不是 list。
