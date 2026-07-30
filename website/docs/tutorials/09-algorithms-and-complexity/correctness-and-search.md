# 正确性与查找

几个示例运行正确，不代表算法对所有输入都正确。检查循环时，可以找出一个“每轮结束后都成立”的
条件。这个条件叫作循环不变量。

<p class="source-note">对应源码：<code>python/python_interview_practice/08_algorithms.py</code></p>

## 两数之和：保存已经见过的信息

给定整数列表和目标值，找出两个数，使它们的和等于目标值，并返回这两个数的下标。下面用字典保存已经
遍历过的数字：

```python
def two_sum(numbers: list[int], target: int) -> list[int]:
    seen: dict[int, int] = {}

    for index, number in enumerate(numbers):
        complement = target - number
        if complement in seen:
            return [seen[complement], index]
        seen[number] = index

    return []


print(two_sum([2, 7, 11, 15], 9))
```

运行结果：

```text
[0, 1]
```

处理到当前元素 `number` 时，需要寻找的是 `target - number`。字典 `seen` 保存“前面出现过的值
及其下标”。

每轮循环结束后，都满足下面的条件：

> 每次循环开始时，`seen` 恰好包含当前下标之前已经处理过的数。

必须先查找补数，再把当前数放入字典。这样同一个元素不会和自己配对。例如输入 `[3]`、目标值为
`6` 时，函数应该返回空列表，而不是 `[0, 0]`。

每个元素只处理一次，字典查询和写入平均为 O(1)，因此平均时间复杂度为 O(n)，额外空间为 O(n)。
函数遇到第一组答案就返回；如果题目要求找出全部组合，返回值和去重规则都需要重新定义。

## 回文判断：先统一比较规则

下面的规则把大小写和非字母数字字符忽略：

```python
def is_palindrome(text: str) -> bool:
    chars = [char.lower() for char in text if char.isalnum()]
    return chars == chars[::-1]


print(is_palindrome("A man, a plan, a canal: Panama"))
print(is_palindrome("Python"))
```

运行结果：

```text
True
False
```

代码分两步：

1. 用 `isalnum()` 保留字母和数字，用 `lower()` 统一大小写；
2. 比较处理后的列表和它的反转副本。

构造 `chars` 需要 O(n) 时间和 O(n) 空间，切片 `chars[::-1]` 又创建一份列表，所以整体仍是
O(n) 时间、O(n) 额外空间。

如果希望减少额外空间，可以使用左右指针。指针跳过不参与比较的字符，直到相遇：

```python
def is_palindrome_in_place(text: str) -> bool:
    left = 0
    right = len(text) - 1

    while left < right:
        while left < right and not text[left].isalnum():
            left += 1
        while left < right and not text[right].isalnum():
            right -= 1

        if text[left].lower() != text[right].lower():
            return False

        left += 1
        right -= 1

    return True
```

两个指针都只向中间移动，总时间仍为 O(n)，额外空间降为 O(1)。这并不是因为代码有嵌套
`while` 就变成 O(n²)：每个字符最多被指针跳过一次。

## 二分查找：维护候选区间

二分查找适用于已经按升序排列的数据：

```python
def binary_search(numbers: list[int], target: int) -> int:
    left = 0
    right = len(numbers) - 1

    while left <= right:
        middle = (left + right) // 2

        if numbers[middle] == target:
            return middle
        if numbers[middle] < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


print(binary_search([1, 3, 5, 7, 9, 11], 7))
print(binary_search([1, 3, 5, 7, 9, 11], 8))
```

运行结果：

```text
3
-1
```

这里使用闭区间 `[left, right]`，左右端点都属于候选范围。循环条件因此是 `left <= right`。

每轮循环结束后，都满足下面的条件：

> 如果目标存在，它一定还在闭区间 `[left, right]` 中。

当中间值小于目标时，`middle` 以及它左侧的位置不可能是答案，所以新的左边界是
`middle + 1`。大于目标时同理，新的右边界是 `middle - 1`。

每轮候选范围减半，最坏时间复杂度是 O(log n)，额外空间是 O(1)。

### 为什么边界容易写错

二分查找有两种常见区间写法：

| 区间 | 初始右边界 | 循环条件 | 排除右侧时 |
| --- | --- | --- | --- |
| 闭区间 `[left, right]` | `len(numbers) - 1` | `left <= right` | `right = middle - 1` |
| 左闭右开 `[left, right)` | `len(numbers)` | `left < right` | `right = middle` |

两套规则都能正确实现，但不能混用。比如初始化成 `len(numbers) - 1`，却使用左闭右开的更新规则，
就可能漏查末尾元素或陷入死循环。

## 重复值会改变“找到”的含义

普通二分查找只保证返回某个匹配位置：

```python
numbers = [1, 2, 2, 2, 3]
```

查找 `2` 时，返回 1、2 或 3 都符合原来的函数说明。如果要求“返回第一个 2”，找到目标后不能立即返回，
而要继续向左收缩范围：

```python
def binary_search_first(numbers: list[int], target: int) -> int:
    left = 0
    right = len(numbers) - 1
    answer = -1

    while left <= right:
        middle = (left + right) // 2
        if numbers[middle] >= target:
            if numbers[middle] == target:
                answer = middle
            right = middle - 1
        else:
            left = middle + 1

    return answer


print(binary_search_first([1, 2, 2, 2, 3], 2))
```

运行结果：

```text
1
```

算法是否正确取决于题目要求。先写清“找到任意一个”还是“找到第一个”，再选择对应写法。
