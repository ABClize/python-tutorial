# 测试与实际测量

复杂度分析说明数据增大时耗时怎样增长。测试检查函数结果是否符合要求。实际测量告诉我们代码在当前
机器上运行了多久。三种方法用途不同，不能互相替代。

<p class="source-note">对应源码：<code>python/python_interview_practice/09_practice_questions.py</code></p>

## 根据输入和结果写测试

测试不需要知道函数内部用了字典还是循环，只需要给出输入并检查结果：

```text
from python_interview_practice import (
    09_practice_questions,  # 这个写法是错误示例
)
```

Python 模块名不能在标识符位置以数字开头，因此编号课程通常作为脚本运行，而不是直接使用普通
`import` 语句导入。项目源码在同一个模块中用 `assert` 做了最小校验：

```python
def run_checks() -> None:
    assert reverse_words("  I  love Python ") == "Python love I"
    assert first_non_repeating_char("aabbcdde") == "c"
    assert first_non_repeating_char("aabb") is None
    assert flatten_once([[1, 2], [3], [], [4, 5]]) == [1, 2, 3, 4, 5]
    assert merge_sorted([1, 4, 7], [2, 3, 8]) == [1, 2, 3, 4, 7, 8]
```

`assert` 条件为假时抛出 `AssertionError`。它适合课程中的快速检查，但正式测试更适合放入
`tests/`，由 pytest 收集、隔离并报告失败位置。

::: warning 不要把 assert 当作业务校验
使用 `python -O` 运行时，普通 `assert` 语句会被移除。用户输入、权限和数据完整性校验应该显式
抛出异常，不能依赖 `assert`。
:::

## 根据函数要求列出边界用例

以 `merge_sorted(left, right)` 为例，“两个输入都已升序排列”是前置条件。测试至少应覆盖：

| 情况 | 示例 | 预期 |
| --- | --- | --- |
| 两边都有数据 | `[1, 4]` 与 `[2, 3]` | `[1, 2, 3, 4]` |
| 左边为空 | `[]` 与 `[2, 3]` | `[2, 3]` |
| 右边为空 | `[1, 4]` 与 `[]` | `[1, 4]` |
| 两边都为空 | `[]` 与 `[]` | `[]` |
| 包含重复值 | `[1, 2]` 与 `[2, 3]` | `[1, 2, 2, 3]` |
| 包含负数 | `[-3, 1]` 与 `[-2, 4]` | `[-3, -2, 1, 4]` |

pytest 测试可以写成：

```python
def test_merge_sorted_keeps_all_values_in_order() -> None:
    assert merge_sorted([1, 2], [2, 3]) == [1, 2, 2, 3]


def test_merge_sorted_accepts_empty_inputs() -> None:
    assert merge_sorted([], []) == []
    assert merge_sorted([], [2, 3]) == [2, 3]
```

如果函数只接收已排序列表，测试就不应该假定它会自动排序。可以信任调用者，也可以在函数中检查并抛出
异常，但必须在函数说明中写清楚。

## 属性测试检查普遍规律

示例测试只覆盖写出来的几组数据。属性测试生成许多输入，检查始终应该成立的规律。合并有序列表应
满足：

- 结果仍然升序；
- 结果长度等于两个输入长度之和；
- 每个值出现的总次数没有改变。

使用 Hypothesis 可以表达这些性质：

```python
from collections import Counter

from hypothesis import given
from hypothesis import strategies as st


@given(
    st.lists(st.integers()).map(sorted),
    st.lists(st.integers()).map(sorted),
)
def test_merge_sorted_properties(
    left: list[int],
    right: list[int],
) -> None:
    result = merge_sorted(left, right)

    assert result == sorted(result)
    assert len(result) == len(left) + len(right)
    assert Counter(result) == Counter(left) + Counter(right)
```

属性测试不是“随机跑几次”这么简单。失败后，Hypothesis 会尝试缩小输入，找出仍能触发问题的更小
示例，便于定位边界错误。

## 用 timeit 比较具体实现

复杂度相同的两种实现，实际速度可能因常数、对象分配和底层 C 实现而不同。`timeit` 会重复执行
代码，减少单次测量抖动：

```python
from timeit import Timer


values = list(range(10_000))
list_timer = Timer("9_999 in values", globals={"values": values})
set_values = set(values)
set_timer = Timer("9_999 in values", globals={"values": set_values})

list_best = min(list_timer.repeat(repeat=5, number=1_000))
set_best = min(set_timer.repeat(repeat=5, number=1_000))

print(list_best > set_best)
```

运行结果通常为：

```text
True
```

这里比较的是“容器已经构造完成后的成员查询”。如果真实任务每次查询前都要临时执行
`set(values)`，就必须把构造成本也纳入测量。测量范围不同，结论也会不同。

实际计时会受到硬件、Python 版本和系统负载影响，因此教程不写死具体秒数。可靠报告应记录环境、
输入规模、预热方式、重复次数和统计值。

## 分析、测试和测量怎样配合

可以按下面的顺序检查一个算法：

1. 写清输入、输出和输入要求；
2. 说明每一步为什么不会丢失正确答案；
3. 计算主要操作数量和额外空间的增长；
4. 用正常、边界和失败用例验证函数要求；
5. 只有性能确实重要时，再用代表性数据测量。

在项目的 `python/` 目录可以运行：

```bash
uv run python python_interview_practice/08_algorithms.py
uv run python python_interview_practice/09_practice_questions.py
uv run pytest -v
```

复杂度较优不保证实现正确，测试通过也不保证在大数据量下足够快。把正确性和性能分开验证，结论才
更清楚。
