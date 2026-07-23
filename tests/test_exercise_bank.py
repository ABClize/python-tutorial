"""Pytest-style examples for the larger interview exercise bank."""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from interview_exercises.algorithms import (
    binary_search_first,
    kth_largest,
    longest_increasing_subsequence_length,
    maximum_subarray,
    minimum_coin_count,
    shortest_path,
)
from interview_exercises.collections import LRUCache, merge_intervals, moving_average
from interview_exercises.concurrency import async_map_ordered
from interview_exercises.oop import Rectangle, TransactionalList
from interview_exercises.strings import (
    longest_unique_substring,
    run_length_decode,
    run_length_encode,
)


@pytest.mark.parametrize(
    ("numbers", "target", "expected"),
    [
        ([1, 2, 2, 2, 4], 2, 1),
        ([1, 3, 5], 4, -1),
        ([], 1, -1),
    ],
)
def test_binary_search_returns_first_match(
    numbers: list[int],
    target: int,
    expected: int,
) -> None:
    assert binary_search_first(numbers, target) == expected


def test_maximum_subarray_returns_sum_and_slice() -> None:
    numbers = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
    best_sum, (start, end) = maximum_subarray(numbers)
    assert best_sum == 6
    assert numbers[start:end] == [4, -1, 2, 1]


@pytest.mark.parametrize(
    ("coins", "amount", "expected"),
    [
        ([1, 2, 5], 11, 3),
        ([2], 3, -1),
        ([], 0, 0),
    ],
)
def test_minimum_coin_count(coins: list[int], amount: int, expected: int) -> None:
    assert minimum_coin_count(coins, amount) == expected


def test_shortest_path_uses_breadth_first_search() -> None:
    graph = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["E"],
        "D": ["F"],
        "E": ["F"],
    }
    path = shortest_path(graph, "A", "F")
    assert path is not None
    assert path[0] == "A"
    assert path[-1] == "F"
    assert len(path) == 4


def test_heap_and_lis_examples() -> None:
    assert kth_largest([3, 2, 1, 5, 6, 4], 2) == 5
    assert longest_increasing_subsequence_length([10, 9, 2, 5, 3, 7, 101, 18]) == 4


def test_lru_cache_updates_recency_and_evicts_oldest() -> None:
    cache: LRUCache[str, int] = LRUCache(capacity=2)
    cache.put("first", 1)
    cache.put("second", 2)
    assert cache.get("first") == 1
    cache.put("third", 3)
    assert cache.get("second") is None
    assert cache.keys_from_oldest() == ["first", "third"]


def test_interval_merge_and_moving_average() -> None:
    assert merge_intervals([(8, 10), (1, 3), (2, 6), (10, 12)]) == [
        (1, 6),
        (8, 12),
    ]
    assert moving_average([1, 2, 3, 4], 2) == [1.5, 2.5, 3.5]


@pytest.mark.asyncio
async def test_async_map_is_concurrent_but_preserves_order() -> None:
    assert await async_map_ordered([3, 1, 2]) == [6, 2, 4]


def test_descriptor_validates_rectangle_dimensions() -> None:
    rectangle = Rectangle(3, 4)
    assert rectangle.area == 12
    with pytest.raises(ValueError, match="必须大于"):
        rectangle.width = 0


def test_transaction_context_commits_or_rolls_back() -> None:
    values = TransactionalList([1, 2])
    with values as transaction:
        transaction.append(3)
    assert values.values == [1, 2, 3]

    with pytest.raises(RuntimeError), values as transaction:
        transaction.append(4)
        raise RuntimeError("触发回滚")
    assert values.values == [1, 2, 3]


@given(st.text())
def test_run_length_encoding_round_trip(text: str) -> None:
    assert run_length_decode(run_length_encode(text)) == text


@given(st.text())
def test_longest_unique_substring_has_no_duplicates(text: str) -> None:
    result = longest_unique_substring(text)
    assert result in text
    assert len(result) == len(set(result))
