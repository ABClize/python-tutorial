# 动态规划与序列处理

有些问题会反复计算相同的子问题。动态规划把已经得到的结果保存下来，避免重复工作。序列处理中的
双指针、计数表和规范化键，也都是把问题中可复用的信息显式保存起来。

<p class="source-note">对应源码：<code>python/python_interview_practice/08_algorithms.py</code>、<code>python/python_interview_practice/09_practice_questions.py</code></p>

## 从斐波那契数理解重复子问题

斐波那契数列满足：

```text
F(0) = 0
F(1) = 1
F(n) = F(n - 1) + F(n - 2)
```

直接按照定义递归：

```python
def fibonacci_recursive(number: int) -> int:
    if number < 2:
        return number
    return fibonacci_recursive(number - 1) + fibonacci_recursive(number - 2)
```

`fibonacci_recursive(5)` 会多次计算 `fibonacci_recursive(3)`、`fibonacci_recursive(2)` 等
相同结果。调用树随 `number` 快速膨胀，时间复杂度接近 O(2ⁿ)。

从较小结果逐步计算，可以避免重复：

```python
def fibonacci_dynamic(number: int) -> int:
    if number < 2:
        return number

    previous, current = 0, 1
    for _ in range(2, number + 1):
        previous, current = current, previous + current

    return current


print(fibonacci_dynamic(10))
```

运行结果：

```text
55
```

这里的状态是“当前位置前面的两个斐波那契数”。每轮只依赖 `previous` 和 `current`，不需要保存
完整列表，所以时间复杂度为 O(n)，额外空间为 O(1)。

动态规划通常包含三部分：

1. 状态表示什么；
2. 当前状态怎样由较小状态得到；
3. 最小问题的初始值是什么。

并不是出现循环就叫动态规划。关键在于问题能否拆成重叠子问题，以及已保存的状态能否用来构造更大
问题的答案。

## 合并两个有序列表

两个输入已经排序时，不必把它们拼接后重新排序。用两个下标分别指向尚未处理的最小值：

```python
def merge_sorted(left: list[int], right: list[int]) -> list[int]:
    result: list[int] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index] <= right[right_index]:
            result.append(left[left_index])
            left_index += 1
        else:
            result.append(right[right_index])
            right_index += 1

    result.extend(left[left_index:])
    result.extend(right[right_index:])
    return result


print(merge_sorted([1, 4, 7], [2, 3, 8]))
```

运行结果：

```text
[1, 2, 3, 4, 7, 8]
```

每次比较后，较小元素已经不可能被后续元素超越，可以安全地放入结果。一个列表耗尽后，另一个列表
剩余部分本身已有序，直接 `extend()` 即可。

两个指针总共移动 `m + n` 次，时间复杂度是 O(m + n)。返回的新列表保存全部元素，额外空间为
O(m + n)。

## 翻转单词时利用 split 的规则

`str.split()` 不传分隔符时，会按任意连续空白切分，并自动忽略首尾空白：

```python
def reverse_words(sentence: str) -> str:
    return " ".join(reversed(sentence.split()))


print(reverse_words("  Python   makes coding fun  "))
```

运行结果：

```text
fun coding makes Python
```

这个函数不仅翻转单词顺序，还把任意连续空白规范成一个普通空格。如果需求要求保留原始空格，当前
实现就不符合契约，需要换成能保留分隔符的处理方式。

## 找到第一个只出现一次的字符

只扫描一次无法同时知道“当前位置是不是第一次出现”和“以后还会不会再出现”。可以分两遍处理：

```python
def first_non_repeating_char(text: str) -> str | None:
    counts: dict[str, int] = {}

    for char in text:
        counts[char] = counts.get(char, 0) + 1

    for char in text:
        if counts[char] == 1:
            return char

    return None


print(first_non_repeating_char("aabbcdde"))
print(first_non_repeating_char("aabb"))
```

运行结果：

```text
c
None
```

第一遍统计次数，第二遍仍按原字符串顺序查找，所以返回的是第一个唯一字符。两遍都是线性扫描，总
时间为 O(n)，字典最多保存不同字符的数量，最坏额外空间为 O(n)。

## 展平一层嵌套列表

二维列表可以用两层推导式展平一层：

```python
def flatten_once(items: list[list[int]]) -> list[int]:
    return [value for group in items for value in group]


print(flatten_once([[1, 2], [3], [], [4, 5]]))
```

运行结果：

```text
[1, 2, 3, 4, 5]
```

推导式中的执行顺序等价于：

```python
result: list[int] = []
for group in items:
    for value in group:
        result.append(value)
```

这个函数只展平一层。输入 `[[1, [2]]]` 时，内层列表 `[2]` 仍会保留。递归展平属于另一种契约，
还要规定字符串、元组等对象是否也应被展开。

## 用规范化键分组

字母异位词包含相同字母，只是顺序不同。把每个单词的字符排序后，可得到同组单词共有的键：

```python
def group_anagrams(words: list[str]) -> list[list[str]]:
    groups: dict[str, list[str]] = {}

    for word in words:
        key = "".join(sorted(word))
        groups.setdefault(key, []).append(word)

    return list(groups.values())


print(group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))
```

运行结果：

```text
[['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
```

如果共有 `n` 个单词、单词平均长度为 `k`，每个单词排序约为 O(k log k)，总时间约为
O(nk log k)。字典的键把“字母组成相同”转换成了普通的相等比较。

当前实现区分大小写，并把标点也算作字符。是否要把 `"Eat"` 和 `"tea"` 分到同组，取决于需求；
需要忽略大小写时，可以在生成键前调用 `casefold()`。
