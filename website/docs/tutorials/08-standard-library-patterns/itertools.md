# Python itertools 惰性迭代工具

`itertools` 用来组合惰性迭代步骤，可以减少手写循环。使用这些工具时，需要理解结果何时产生、是否
只能消费一次，以及组合数量会怎样增长。

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

## 选择工具

| 需求 | 工具 |
| --- | --- |
| 截取迭代器的一段 | `islice()` |
| 连接多个迭代器 | `chain()` |
| 累计值、相邻值 | `accumulate()`、`pairwise()` |
| 组合和笛卡尔积 | `combinations()`、`product()` |
| 连续相同 key 分组 | `groupby()` |
