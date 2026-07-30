# 复杂度基础

算法解决的是一类问题，而不是某一组固定数据。下面两个函数都能判断列表里是否有重复值，但随着列表
变长，它们需要做的工作并不一样。复杂度就是描述这种增长趋势的方法。

<p class="source-note">对应源码：<code>python/python_interview_practice/08_algorithms.py</code></p>

## 从输入、输出和约束开始

一个算法至少要说明三件事：

1. 接收什么输入；
2. 返回什么结果；
3. 输入需要满足什么条件。

例如，二分查找的函数签名可以写成：

```python
def binary_search(numbers: list[int], target: int) -> int:
    ...
```

仅有签名还不够。它还依赖下面的约定：

- `numbers` 必须按升序排列；
- 找到目标时返回一个有效下标；
- 找不到时返回 `-1`；
- 如果目标重复出现，不保证返回第一个还是最后一个位置。

“列表已经排序”是二分查找成立的前提。如果调用者传入 `[5, 1, 3]`，函数即使偶尔返回正确结果，
也不能说明算法正确。

## 输入规模 n 表示什么

复杂度中的 `n` 表示输入规模。它不是固定指某种对象，需要根据问题解释：

| 问题 | 输入规模 |
| --- | --- |
| 在列表中查找元素 | 列表长度 `n` |
| 扫描字符串 | 字符数量 `n` |
| 合并两个列表 | 两个列表长度 `m` 和 `n` |
| 遍历图 | 顶点数 `V` 和边数 `E` |
| 处理矩阵 | 行数 `m` 和列数 `n` |

只有先说明规模，`O(n)` 才有明确含义。合并两个长度不同的列表时，写成 `O(m + n)` 通常比笼统写
`O(n)` 更准确。

## 大 O 描述增长速度

大 O 关注输入增大时，主要操作次数如何增长。常见量级从慢到快排列如下：

```text
O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ) < O(n!)
```

| 复杂度 | 常见操作 |
| --- | --- |
| O(1) | 按列表下标读取；字典的平均查询 |
| O(log n) | 二分查找；每轮把范围减半 |
| O(n) | 扫描一次列表；构造集合 |
| O(n log n) | 通用比较排序 |
| O(n²) | 比较所有元素对 |
| O(2ⁿ) | 枚举一个集合的所有子集 |
| O(n!) | 枚举所有排列 |

如果操作次数是 `3n² + 20n + 8`，当 `n` 足够大时，`n²` 的增长远快于其余部分。因此忽略常数
和低阶项，记为 O(n²)。这不表示常数永远不重要：数据量很小时，解释器开销、函数调用和缓存命中仍
会影响实际用时。

## 比较 O(n²) 与 O(n)

最直接的查重方法是比较每一对元素：

```python
def has_duplicate_slow(values: list[int]) -> bool:
    for left in range(len(values)):
        for right in range(left + 1, len(values)):
            if values[left] == values[right]:
                return True
    return False


print(has_duplicate_slow([3, 1, 4, 1]))
print(has_duplicate_slow([3, 1, 4, 2]))
```

运行结果：

```text
True
False
```

列表长度为 `n` 时，最坏情况下需要比较：

```text
(n - 1) + (n - 2) + ... + 1 = n(n - 1) / 2
```

主导项是 `n²`，所以时间复杂度为 O(n²)。这个版本只使用少量局部变量，额外空间是 O(1)。

如果用集合记录已经见过的值：

```python
def has_duplicate(values: list[int]) -> bool:
    seen: set[int] = set()

    for value in values:
        if value in seen:
            return True
        seen.add(value)

    return False


print(has_duplicate([3, 1, 4, 1]))
print(has_duplicate([3, 1, 4, 2]))
```

运行结果：

```text
True
False
```

每个元素最多处理一次，集合查询和插入的平均成本是 O(1)，所以平均时间复杂度是 O(n)。`seen`
最多保存 `n` 个元素，额外空间复杂度是 O(n)。这里用更多内存换取了更少的比较。

<ClientOnly>
  <ComplexityChart />
</ClientOnly>

图中的纵轴是主要操作量的估算，不是实际运行秒数。调大输入规模后，O(n²) 曲线比 O(n) 上升得
更快。输入扩大 5 倍时，线性方案的主要操作量约扩大 5 倍，平方方案则约扩大 25 倍。对数纵轴可以
把数量级差异很大的曲线放在同一张图上观察。

## 怎样从代码判断复杂度

### 固定次数操作：O(1)

```python
def first(values: list[int]) -> int:
    return values[0]
```

无论列表有 10 项还是 100 万项，函数都只读取一个位置。列表为空时会抛出 `IndexError`，这属于
输入约束，不会改变复杂度。

### 扫描一次：O(n)

```python
def contains(values: list[int], target: int) -> bool:
    for value in values:
        if value == target:
            return True
    return False
```

目标在第一项时只比较一次，目标不存在时要检查全部 `n` 项。因此最好情况是 O(1)，最坏情况是
O(n)。

### 连续循环相加

```python
for value in values:
    process(value)

for value in values:
    save(value)
```

两个循环依次执行，工作量是 `n + n = 2n`，忽略常数后仍为 O(n)，不是 O(n²)。

### 独立的嵌套循环相乘

```python
for left in left_values:
    for right in right_values:
        compare(left, right)
```

如果两个列表长度分别为 `m` 和 `n`，总比较次数是 `m × n`，复杂度为 O(mn)。只有两个范围都
由同一个 `n` 表示时，才简写成 O(n²)。

### 每轮减半：O(log n)

二分查找每轮排除一半候选范围：

```text
n → n/2 → n/4 → n/8 → ... → 1
```

一个数连续除以 2，约 `log₂n` 次后会降到 1，所以二分查找是 O(log n)。

### 排序后再扫描：O(n log n)

```python
ordered = sorted(values)
for value in ordered:
    process(value)
```

Python 的 `sorted()` 和 `list.sort()` 使用 Timsort。最坏时间复杂度为 O(n log n)，后面的线性
扫描为 O(n)，两者相加后由增长更快的一项主导：

```text
O(n log n) + O(n) = O(n log n)
```

缩进层数不是判断复杂度的唯一依据。双指针代码可能写成嵌套循环，但如果两个指针在整个函数中各自
最多向前移动 `n` 次，总工作量仍可能是 O(n)。

## 时间复杂度与空间复杂度

时间复杂度描述执行步骤的增长，空间复杂度描述算法额外占用的内存增长。通常不把输入本身算作额外
空间，但新建容器、递归调用栈和缓存都要计算。

| 查重方案 | 时间 | 额外空间 |
| --- | --- | --- |
| 两两比较 | 最坏 O(n²) | O(1) |
| 集合记录 | 平均 O(n) | O(n) |

“原地算法”通常表示只使用 O(1) 或很少的额外空间，但它不等于完全不分配 Python 对象，也不保证
运行得更快。讨论时要区分算法层面的额外空间与解释器内部的实际分配。

## 最好、平均、最坏和摊销

同一段代码在不同输入下可能执行不同次数：

- 线性查找在第一项找到目标，最好是 O(1)；
- 目标位于末尾或不存在，最坏是 O(n)；
- 哈希表查询通常说平均 O(1)，极端情况下可能退化。

列表的 `append()` 大多数时候只在末尾写入，偶尔需要扩容并复制已有引用。某一次扩容可能需要
O(n)，但连续追加 `n` 项的总成本仍为 O(n)，因此把单次 `append()` 记为摊销 O(1)。

复杂度结论最好带上条件，例如“集合查询平均 O(1)”或“二分查找最坏 O(log n)”，不要把平均情况
和最坏情况混在一起。
