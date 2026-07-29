"""列表、字典、集合、队列和缓存类面试题。"""

from __future__ import annotations

# 本文件与标准库 collections 同名。直接运行时先移除脚本目录，
# 避免下面的导入再次加载当前文件。
import sys

if __package__ in (None, "") and sys.path:
    sys.path.pop(0)

from collections import Counter, OrderedDict, deque
from collections.abc import Hashable, Iterable
from typing import Generic, TypeVar

T = TypeVar("T", bound=Hashable)
K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


def unique_in_order(items: Iterable[T]) -> list[T]:
    """题目：去重，同时保持元素第一次出现的顺序。

    元素必须可哈希。不能直接 ``list(set(items))``，因为集合不表达业务顺序。

    时间复杂度：平均 O(n)
    空间复杂度：O(n)
    """

    seen: set[T] = set()
    result: list[T] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """题目：合并所有重叠或首尾相接的闭区间。

    例如 ``[(1, 3), (2, 6), (8, 10)]`` 变为
    ``[(1, 6), (8, 10)]``。

    时间复杂度：O(n log n)，主要成本是排序
    空间复杂度：O(n)，用于排序副本和结果
    """

    for start, end in intervals:
        if start > end:
            raise ValueError(f"非法区间：({start}, {end})")

    ordered = sorted(intervals)
    merged: list[tuple[int, int]] = []

    for start, end in ordered:
        if not merged or start > merged[-1][1]:
            merged.append((start, end))
            continue

        previous_start, previous_end = merged[-1]
        merged[-1] = (previous_start, max(previous_end, end))

    return merged


def top_k_frequent(items: list[T], k: int) -> list[T]:
    """题目：返回出现次数最多的 k 个元素。

    次数相同时，先出现在输入中的元素优先，使返回值完全确定。

    时间复杂度：O(n + u log u)，u 是不同元素的数量
    空间复杂度：O(u)
    """

    if k <= 0:
        return []

    frequencies = Counter(items)
    first_position: dict[T, int] = {}
    for index, item in enumerate(items):
        first_position.setdefault(item, index)

    ordered = sorted(
        frequencies,
        key=lambda item: (-frequencies[item], first_position[item]),
    )
    return ordered[:k]


def flatten_integers(nested: list[object]) -> list[int]:
    """题目：把任意深度的整数列表展开成一维列表。

    使用显式栈避免深层输入消耗 Python 递归调用栈。遇到非整数叶子时抛错。

    时间复杂度：O(n)
    空间复杂度：O(n)
    """

    result: list[int] = []
    stack = list(reversed(nested))

    while stack:
        item = stack.pop()
        if isinstance(item, list):
            stack.extend(reversed(item))
        elif isinstance(item, int) and not isinstance(item, bool):
            result.append(item)
        else:
            raise TypeError(f"只支持整数或列表，收到 {type(item).__name__}")

    return result


def invert_mapping(mapping: dict[K, V]) -> dict[V, list[K]]:
    """题目：反转字典，并正确处理多个键拥有相同值的情况。

    原字典的值必须可哈希。列表顺序遵循原字典迭代顺序。

    时间复杂度：平均 O(n)
    空间复杂度：O(n)
    """

    result: dict[V, list[K]] = {}
    for key, value in mapping.items():
        result.setdefault(value, []).append(key)
    return result


def moving_average(values: Iterable[float], window_size: int) -> list[float]:
    """题目：计算固定窗口的移动平均值。

    使用 deque 和当前总和，避免为每个窗口重新求和。

    时间复杂度：O(n)
    空间复杂度：O(window_size)
    """

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


class LRUCache(Generic[K, V]):
    """题目：实现固定容量的最近最少使用（LRU）缓存。

    ``OrderedDict`` 的尾部表示最近使用，头部表示最久未使用。
    ``get`` 和 ``put`` 的平均时间复杂度均为 O(1)，空间为 O(capacity)。
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("缓存容量必须为正整数")
        self.capacity = capacity
        self._data: OrderedDict[K, V] = OrderedDict()

    def get(self, key: K) -> V | None:
        """取得值并把该键标记为最近使用；不存在时返回 None。"""

        if key not in self._data:
            return None
        self._data.move_to_end(key)
        return self._data[key]

    def put(self, key: K, value: V) -> None:
        """插入或更新值，容量超限时淘汰最久未使用项。"""

        if key in self._data:
            self._data.move_to_end(key)
        self._data[key] = value

        if len(self._data) > self.capacity:
            self._data.popitem(last=False)

    def keys_from_oldest(self) -> list[K]:
        """返回从最久未使用到最近使用的键，仅用于学习和测试。"""

        return list(self._data)

    def __len__(self) -> int:
        return len(self._data)


def run_tests() -> None:
    assert unique_in_order([3, 1, 3, 2, 1]) == [3, 1, 2]
    assert unique_in_order("banana") == ["b", "a", "n"]
    assert unique_in_order([]) == []

    assert merge_intervals([(8, 10), (1, 3), (2, 6), (10, 12)]) == [
        (1, 6),
        (8, 12),
    ]
    assert merge_intervals([]) == []
    assert merge_intervals([(1, 1)]) == [(1, 1)]

    try:
        merge_intervals([(4, 2)])
    except ValueError:
        pass
    else:
        raise AssertionError("反向区间应该抛出 ValueError")

    assert top_k_frequent(["a", "b", "b", "a", "c"], 2) == ["a", "b"]
    assert top_k_frequent([1, 1, 2, 3, 3, 3], 10) == [3, 1, 2]
    assert top_k_frequent([1, 2], 0) == []

    assert flatten_integers([1, [2, [3, 4], []], 5]) == [1, 2, 3, 4, 5]
    assert flatten_integers([]) == []
    try:
        flatten_integers([1, "2"])
    except TypeError:
        pass
    else:
        raise AssertionError("非整数叶子应该抛出 TypeError")

    assert invert_mapping({"alice": "研发", "bob": "销售", "cathy": "研发"}) == {
        "研发": ["alice", "cathy"],
        "销售": ["bob"],
    }

    assert moving_average([1, 2, 3, 4, 5], 3) == [2.0, 3.0, 4.0]
    assert moving_average([1, 2], 3) == []

    cache: LRUCache[str, int] = LRUCache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1
    assert cache.keys_from_oldest() == ["b", "a"]
    cache.put("c", 3)
    assert cache.get("b") is None
    assert cache.keys_from_oldest() == ["a", "c"]
    cache.put("a", 10)
    assert cache.get("a") == 10
    assert len(cache) == 2


def main() -> None:
    run_tests()
    print("区间合并:", merge_intervals([(5, 7), (1, 4), (3, 6)]))
    print("频率最高:", top_k_frequent(list("mississippi"), 3))
    print("移动平均:", moving_average(range(1, 7), 3))
    print("collections.py：全部测试通过")


if __name__ == "__main__":
    main()
