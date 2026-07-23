"""常见算法面试题：查找、动态规划、图和堆。"""

from __future__ import annotations

import sys

if __package__ in (None, "") and sys.path:
    # 防止同目录的 collections.py 遮蔽标准库。
    sys.path.pop(0)

import heapq
from collections import deque


def binary_search_first(numbers: list[int], target: int) -> int:
    """题目：在升序数组中查找 target 第一次出现的位置。

    不直接在找到时返回，而是继续收缩右边界。

    时间复杂度：O(log n)
    空间复杂度：O(1)
    """

    left = 0
    right = len(numbers) - 1
    answer = -1

    while left <= right:
        middle = left + (right - left) // 2
        if numbers[middle] >= target:
            if numbers[middle] == target:
                answer = middle
            right = middle - 1
        else:
            left = middle + 1

    return answer


def two_sum(numbers: list[int], target: int) -> tuple[int, int] | None:
    """题目：找出和为 target 的两个元素下标。

    扫描时只记录已经见过的数字，保证不能重复使用同一元素。

    时间复杂度：平均 O(n)
    空间复杂度：O(n)
    """

    index_by_value: dict[int, int] = {}
    for index, number in enumerate(numbers):
        complement = target - number
        if complement in index_by_value:
            return index_by_value[complement], index
        index_by_value.setdefault(number, index)
    return None


def maximum_subarray(numbers: list[int]) -> tuple[int, tuple[int, int]]:
    """题目：返回最大连续子数组的和，以及左闭右开下标区间。

    Kadane 算法的不变量：current_sum 是以当前位置结尾的最佳子数组和。

    时间复杂度：O(n)
    空间复杂度：O(1)
    """

    if not numbers:
        raise ValueError("输入不能为空")

    best_sum = current_sum = numbers[0]
    best_start = current_start = 0
    best_end = 1

    for index in range(1, len(numbers)):
        number = numbers[index]
        if current_sum + number < number:
            current_sum = number
            current_start = index
        else:
            current_sum += number

        if current_sum > best_sum:
            best_sum = current_sum
            best_start = current_start
            best_end = index + 1

    return best_sum, (best_start, best_end)


def kth_largest(numbers: list[int], k: int) -> int:
    """题目：返回数组中第 k 大的元素，重复值分别计数。

    维护大小不超过 k 的最小堆，堆顶就是当前第 k 大。

    时间复杂度：O(n log k)
    空间复杂度：O(k)
    """

    if not 1 <= k <= len(numbers):
        raise ValueError("k 必须位于 1 和数组长度之间")

    heap: list[int] = []
    for number in numbers:
        if len(heap) < k:
            heapq.heappush(heap, number)
        elif number > heap[0]:
            heapq.heapreplace(heap, number)
    return heap[0]


def minimum_coin_count(coins: list[int], amount: int) -> int:
    """题目：用给定面额凑出 amount，返回最少硬币数，无法凑出则返回 -1。

    ``dp[value]`` 表示凑出 value 的最少硬币数。

    时间复杂度：O(amount * len(coins))
    空间复杂度：O(amount)
    """

    if amount < 0:
        raise ValueError("金额不能为负数")
    if any(coin <= 0 for coin in coins):
        raise ValueError("硬币面额必须为正整数")

    unreachable = amount + 1
    dp = [0] + [unreachable] * amount

    for value in range(1, amount + 1):
        for coin in coins:
            if coin <= value:
                dp[value] = min(dp[value], dp[value - coin] + 1)

    return -1 if dp[amount] == unreachable else dp[amount]


def shortest_path(
    graph: dict[str, list[str]],
    start: str,
    destination: str,
) -> list[str] | None:
    """题目：在无权图中返回从 start 到 destination 的最短路径。

    广度优先搜索第一次到达某节点时，走过的边数一定最少。

    时间复杂度：O(V + E)
    空间复杂度：O(V)
    """

    if start == destination:
        return [start]

    queue: deque[str] = deque([start])
    parent: dict[str, str | None] = {start: None}

    while queue:
        node = queue.popleft()
        for neighbor in graph.get(node, []):
            if neighbor in parent:
                continue

            parent[neighbor] = node
            if neighbor == destination:
                path = [destination]
                current: str | None = destination
                while current != start:
                    if current is None:  # 防御性分支，正常 BFS 不会进入
                        return None
                    current = parent[current]
                    if current is not None:
                        path.append(current)
                path.reverse()
                return path

            queue.append(neighbor)

    return None


def longest_increasing_subsequence_length(numbers: list[int]) -> int:
    """题目：返回严格递增子序列的最大长度。

    ``tails[i]`` 保存长度为 i + 1 的递增子序列中，最小的结尾数字。
    用手写 lower_bound 找到第一个大于等于当前数字的位置。

    时间复杂度：O(n log n)
    空间复杂度：O(n)
    """

    tails: list[int] = []

    for number in numbers:
        left = 0
        right = len(tails)
        while left < right:
            middle = (left + right) // 2
            if tails[middle] < number:
                left = middle + 1
            else:
                right = middle

        if left == len(tails):
            tails.append(number)
        else:
            tails[left] = number

    return len(tails)


def run_tests() -> None:
    assert binary_search_first([1, 2, 2, 2, 4], 2) == 1
    assert binary_search_first([1, 3, 5], 4) == -1
    assert binary_search_first([], 1) == -1

    assert two_sum([2, 7, 11, 15], 9) == (0, 1)
    assert two_sum([3, 3], 6) == (0, 1)
    assert two_sum([1, 2, 3], 100) is None

    numbers = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
    best_sum, (start, end) = maximum_subarray(numbers)
    assert best_sum == 6
    assert numbers[start:end] == [4, -1, 2, 1]
    assert maximum_subarray([-5, -2, -8]) == (-2, (1, 2))

    assert kth_largest([3, 2, 1, 5, 6, 4], 2) == 5
    assert kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4

    assert minimum_coin_count([1, 2, 5], 11) == 3
    assert minimum_coin_count([2], 3) == -1
    assert minimum_coin_count([], 0) == 0

    graph = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["D", "E"],
        "D": ["F"],
        "E": ["F"],
        "F": [],
    }
    assert shortest_path(graph, "A", "F") == ["A", "B", "D", "F"]
    assert shortest_path(graph, "A", "A") == ["A"]
    assert shortest_path(graph, "F", "A") is None

    assert longest_increasing_subsequence_length([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    assert longest_increasing_subsequence_length([7, 7, 7]) == 1
    assert longest_increasing_subsequence_length([]) == 0


def main() -> None:
    run_tests()
    print("两数之和:", two_sum([8, 3, 12, 7], 10))
    print("第 3 大:", kth_largest([9, 1, 8, 2, 7, 3], 3))
    print("最长递增子序列长度:", longest_increasing_subsequence_length([4, 1, 5, 2, 6, 3]))
    print("algorithms.py：全部测试通过")


if __name__ == "__main__":
    main()
