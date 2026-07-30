# Python itertools、heapq 与 bisect

`itertools` 组合惰性迭代步骤，`heapq` 维护最小堆和 Top-K，`bisect` 在有序列表中查找边界。三者都能
减少手写循环，但需要理解惰性、顺序和复杂度。

<p class="source-note">对应源码：<code>python/python_interview_practice/12_standard_library_patterns.py</code></p>

## islice 与无限迭代器

`count()` 产生无限序列，必须限制消费数量：

```python
from itertools import count, islice

sequence = islice(count(start=10, step=3), 5)
print(list(sequence))
```

运行结果：

```text
[10, 13, 16, 19, 22]
```

不要直接对无限迭代器调用 `list()`。

## chain、accumulate 与 pairwise

```python
from itertools import accumulate, chain, pairwise

pages = [["A", "B"], ["C"], ["D", "E"]]

print(list(chain.from_iterable(pages)))
print(list(accumulate([3, 1, 4, 2])))
print(list(pairwise([10, 20, 35, 50])))
```

运行结果：

```text
['A', 'B', 'C', 'D', 'E']
[3, 4, 8, 10]
[(10, 20), (20, 35), (35, 50)]
```

- `chain.from_iterable()` 顺序连接多个可迭代对象；
- `accumulate()` 产生逐步累计结果；
- `pairwise()` 产生相邻元素对。

这些函数返回迭代器，结果通常只能消费一次。

## combinations 与 product

```python
from itertools import combinations, product

print(list(combinations(["A", "B", "C"], 2)))
print(list(product(["红", "蓝"], ["S", "M"])))
```

运行结果：

```text
[('A', 'B'), ('A', 'C'), ('B', 'C')]
[('红', 'S'), ('红', 'M'), ('蓝', 'S'), ('蓝', 'M')]
```

组合数量可能增长很快。函数虽然惰性产生结果，但调用 `list()` 会把所有组合放入内存。

## groupby 只合并连续分组

```python
from itertools import groupby
from operator import itemgetter

records = [
    {"team": "A", "score": 80},
    {"team": "B", "score": 75},
    {"team": "A", "score": 90},
    {"team": "B", "score": 85},
]

ordered = sorted(records, key=itemgetter("team"))

for team, rows in groupby(ordered, key=itemgetter("team")):
    print(team, [row["score"] for row in rows])
```

运行结果：

```text
A [80, 90]
B [75, 85]
```

`groupby()` 遇到 key 改变就结束当前组。要把相同 key 的所有记录放在一起，通常先按相同 key 排序。
每组的 `rows` 也是一次性迭代器，应在进入下一组前消费。

## heapq 最小堆

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

## bisect 查找有序边界

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

## 选择工具

| 需求 | 工具 |
| --- | --- |
| 截取迭代器的一段 | `islice()` |
| 连接多个迭代器 | `chain()` |
| 累计值、相邻值 | `accumulate()`、`pairwise()` |
| 组合和笛卡尔积 | `combinations()`、`product()` |
| 连续相同 key 分组 | `groupby()` |
| 动态维护最小值 | `heapq` |
| 少量最大值或最小值 | `nlargest()`、`nsmallest()` |
| 有序列表边界 | `bisect_left()`、`bisect_right()` |
