"""Property-based tests: verify rules across many generated inputs."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

from hypothesis import given
from hypothesis import strategies as st

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str) -> ModuleType:
    """Load a teaching module whose filename starts with a number."""
    module_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"无法加载模块: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


algorithms = load_module(
    "property_algorithms",
    "python_interview_practice/08_algorithms.py",
)
practice = load_module(
    "property_practice",
    "python_interview_practice/09_practice_questions.py",
)


@given(st.lists(st.integers(), max_size=100), st.lists(st.integers(), max_size=100))
def test_merge_sorted_matches_builtin_sort(left: list[int], right: list[int]) -> None:
    """For any integer lists, merging sorted inputs equals sorting all values."""
    sorted_left = sorted(left)
    sorted_right = sorted(right)
    assert practice.merge_sorted(sorted_left, sorted_right) == sorted(left + right)


@given(st.lists(st.lists(st.integers(), max_size=20), max_size=20))
def test_flatten_once_preserves_order(groups: list[list[int]]) -> None:
    expected = []
    for group in groups:
        expected.extend(group)
    assert practice.flatten_once(groups) == expected


@given(st.lists(st.text(min_size=1), max_size=30))
def test_reverse_words_is_an_involution(words: list[str]) -> None:
    """Reversing twice returns the whitespace-normalized sentence."""
    sentence = " ".join(words)
    reversed_twice = practice.reverse_words(practice.reverse_words(sentence))
    assert reversed_twice == " ".join(sentence.split())


@given(st.lists(st.integers(), unique=True, max_size=100), st.integers())
def test_binary_search_agrees_with_membership(numbers: list[int], target: int) -> None:
    ordered = sorted(numbers)
    index = algorithms.binary_search(ordered, target)
    if target in ordered:
        assert index >= 0
        assert ordered[index] == target
    else:
        assert index == -1


@given(st.text(alphabet="([{", max_size=50))
def test_mirrored_brackets_are_valid(opening: str) -> None:
    closing = opening.translate(str.maketrans({"(": ")", "[": "]", "{": "}"}))[::-1]
    assert algorithms.valid_brackets(opening + closing)


@given(st.text())
def test_palindrome_accepts_text_mirrored_around_center(text: str) -> None:
    mirrored = text + text[::-1]
    assert algorithms.is_palindrome(mirrored)
