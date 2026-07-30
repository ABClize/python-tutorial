# Python heapq 与 bisect

`heapq` 用于最小堆、Top-K 和优先队列。`bisect` 用于在有序列表中查找插入位置。两者都处理有序
数据，但用途不同。

<!-- 对应源码：python/python_interview_practice/12_standard_library_patterns.py -->

## heapq 最小堆

下面把普通列表原地转换成最小堆，再依次弹出三个最小值：

```python
import heapq

numbers = [9, 1, 7, 3, 8, 2]
heapq.heapify(numbers)

print(numbers[0])
print([heapq.heappop(numbers) for _ in range(3)])
```

运行结果：

```text
1
[1, 2, 3]
```

堆只保证最小元素位于索引 `0`，内部列表不是完整排序结果。`heapify()` 线性时间建堆，
`heappush()` 和 `heappop()` 是 O(log n)。

## Top-K

下面从四位候选人中找出分数最高的两位：

```python
import heapq
from operator import itemgetter

candidates = [
    {"name": "Ada", "score": 92},
    {"name": "Linus", "score": 88},
    {"name": "Grace", "score": 99},
    {"name": "Guido", "score": 95},
]

top_two = heapq.nlargest(
    2,
    candidates,
    key=itemgetter("score"),
)
print([(item["name"], item["score"]) for item in top_two])
```

运行结果：

```text
[('Grace', 99), ('Guido', 95)]
```

只需要少量最大或最小元素时，Top-K 不必完整排序所有数据。`k` 接近总元素数时，直接排序可能更合适。

## 稳定优先队列

相同优先级时，加入递增序号避免比较任务对象：

```python
import heapq
from itertools import count

queue: list[tuple[int, int, str]] = []
order = count()

heapq.heappush(queue, (2, next(order), "写文档"))
heapq.heappush(queue, (1, next(order), "修复问题"))
heapq.heappush(queue, (2, next(order), "补测试"))

while queue:
    _, _, task = heapq.heappop(queue)
    print(task)
```

运行结果：

```text
修复问题
写文档
补测试
```

优先级 `1` 先执行。两个优先级为 `2` 的任务再按照加入队列的先后顺序执行。

## bisect 查找插入位置

下面分别查找 `80` 左侧和右侧的插入位置：

```python
from bisect import bisect_left, bisect_right

scores = [60, 70, 80, 80, 90]

print(bisect_left(scores, 80))
print(bisect_right(scores, 80))
```

运行结果：

```text
2
4
```

`bisect_left()` 返回相同元素之前的位置，`bisect_right()` 返回相同元素之后的位置。

`insort()` 查找位置后插入：

```python
from bisect import insort

scores = [60, 70, 80, 90]
insort(scores, 85)

print(scores)
```

运行结果：

```text
[60, 70, 80, 85, 90]
```

二分查找位置是 O(log n)，但 list 中间插入要移动元素，整个 `insort()` 仍是 O(n)。输入必须始终按
同一规则排序。

## 怎样选择工具

| 需求 | 工具 |
| --- | --- |
| 动态维护最小值 | `heapq` |
| 少量最大值或最小值 | `nlargest()`、`nsmallest()` |
| 有序列表边界 | `bisect_left()`、`bisect_right()` |
