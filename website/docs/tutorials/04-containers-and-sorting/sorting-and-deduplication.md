# Python 排序与保序去重

排序不仅要知道升序和降序，还要分清 sorted() 返回新列表与 list.sort() 原地修改的差别。对于复杂记录，可以用 key 指定排序依据；需要去重时，还要明确是否保留原顺序。

<p class="source-note">对应源码：<code>python/python_interview_practice/03_collections_copy.py</code>、<code>python/interview_exercises/collections.py</code></p>

## `sorted()` 和 `list.sort()`

`sorted()` 接收任意可迭代对象，返回新的 list，不修改原数据：

```python
scores = [82, 55, 91]
ordered = sorted(scores, reverse=True)

print(ordered)
print(scores)
```

运行结果：

```text
[91, 82, 55]
[82, 55, 91]
```

`list.sort()` 只用于 list，原地排序并返回 `None`：

```python
scores = [82, 55, 91]
result = scores.sort()

print(scores)
print(result)
```

运行结果：

```text
[55, 82, 91]
None
```

需要保留原顺序时使用 `sorted()`；不再需要原顺序且希望避免新列表时使用 `sort()`。

## 使用 `key` 指定排序依据

复杂数据需要明确“按什么排序”：

```python
students = [
    {"name": "小林", "score": 88},
    {"name": "小周", "score": 95},
    {"name": "小陈", "score": 88},
]

ordered = sorted(
    students,
    key=lambda student: (-student["score"], student["name"]),
)

for student in ordered:
    print(student["name"], student["score"])
```

运行结果：

```text
小周 95
小林 88
小陈 88
```

`key` 函数对每个元素计算一次排序键。tuple 会逐项比较，因此 `(-score, name)` 表示：

1. 先按分数降序，负号把较高分数变成较小的排序键；
2. 分数相同时按姓名升序。

`operator.itemgetter()` 和 `operator.attrgetter()` 也可用于简单字段排序：

```python
from operator import itemgetter


records = [("小林", 82), ("小周", 91)]
print(sorted(records, key=itemgetter(1), reverse=True))
```

运行结果：

```text
[('小周', 91), ('小林', 82)]
```

## 稳定排序

Python 的排序是稳定的：两个元素的排序键相同时，保留它们在原输入中的相对顺序。

```python
records = [
    ("小林", "A"),
    ("小周", "B"),
    ("小陈", "A"),
]

print(sorted(records, key=lambda record: record[1]))
```

运行结果：

```text
[('小林', 'A'), ('小陈', 'A'), ('小周', 'B')]
```

稳定性允许分步骤排序。若先按次要条件排序，再按主要条件稳定排序，次要顺序会在主要 key 相同时保留。
多数情况使用 tuple key 更直接。

## 保序去重

元素可哈希时，可以借助 dict 保留第一次出现的顺序：

```python
items = [3, 1, 3, 2, 1]
unique_items = list(dict.fromkeys(items))

print(unique_items)
```

运行结果：

```text
[3, 1, 2]
```

显式 `seen` 集合便于加入更多处理：

```python
def unique_in_order(items):
    seen = set()
    result = []

    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)

    return result


print(unique_in_order([3, 1, 3, 2, 1]))
```

运行结果：

```text
[3, 1, 2]
```

直接写 `list(set(items))` 不能表达保序要求。元素不可哈希时，需要选择一个可哈希字段作为去重 key。
