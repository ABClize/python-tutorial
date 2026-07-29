"""Tests for ``python_interview_practice/08_algorithms.py``."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "python_interview_practice" / "08_algorithms.py"
SPEC = importlib.util.spec_from_file_location("interview_algorithms", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"无法从路径加载模块: {MODULE_PATH}")
algorithms = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(algorithms)


class TwoSumTests(unittest.TestCase):
    """Tests for the hash-table two-sum implementation."""

    def test_finds_pair_in_typical_input(self) -> None:
        self.assertEqual(algorithms.two_sum([2, 7, 11, 15], 9), [0, 1])

    def test_handles_duplicate_values(self) -> None:
        self.assertEqual(algorithms.two_sum([3, 3], 6), [0, 1])

    def test_handles_negative_values(self) -> None:
        self.assertEqual(algorithms.two_sum([3, -1, 5, 2], 4), [1, 2])

    def test_returns_first_pair_found_while_scanning(self) -> None:
        self.assertEqual(algorithms.two_sum([1, 2, 3, 4], 5), [1, 2])

    def test_returns_empty_list_when_no_pair_exists(self) -> None:
        for numbers, target in [([], 1), ([1], 2), ([1, 2, 3], 100)]:
            with self.subTest(numbers=numbers, target=target):
                self.assertEqual(algorithms.two_sum(numbers, target), [])

    def test_does_not_modify_input(self) -> None:
        numbers = [4, 1, 8, 2]
        original = numbers.copy()
        algorithms.two_sum(numbers, 10)
        self.assertEqual(numbers, original)

    def test_rejects_non_iterable_input(self) -> None:
        with self.assertRaises(TypeError):
            algorithms.two_sum(None, 10)


class PalindromeTests(unittest.TestCase):
    """Tests for normalized palindrome detection."""

    def test_ignores_spaces_punctuation_and_case(self) -> None:
        self.assertTrue(algorithms.is_palindrome("A man, a plan, a canal: Panama"))
        self.assertTrue(algorithms.is_palindrome("No 'x' in Nixon"))

    def test_supports_digits_and_unicode_alphanumeric_characters(self) -> None:
        self.assertTrue(algorithms.is_palindrome("A1b2b1a"))
        self.assertTrue(algorithms.is_palindrome("上海自来水来自海上"))

    def test_rejects_non_palindrome(self) -> None:
        self.assertFalse(algorithms.is_palindrome("Python"))
        self.assertFalse(algorithms.is_palindrome("almost, but not"))

    def test_empty_or_punctuation_only_text_is_palindrome(self) -> None:
        for text in ("", "   ", ".,!?---"):
            with self.subTest(text=text):
                self.assertTrue(algorithms.is_palindrome(text))

    def test_none_is_not_valid_text(self) -> None:
        with self.assertRaises(TypeError):
            algorithms.is_palindrome(None)


class BinarySearchTests(unittest.TestCase):
    """Tests for binary search on ascending sequences."""

    def test_finds_values_at_start_middle_and_end(self) -> None:
        numbers = [1, 3, 5, 7, 9, 11, 13]
        for target, expected_index in [(1, 0), (7, 3), (13, 6)]:
            with self.subTest(target=target):
                self.assertEqual(
                    algorithms.binary_search(numbers, target),
                    expected_index,
                )

    def test_returns_minus_one_for_missing_values(self) -> None:
        numbers = [1, 3, 5, 7]
        for target in (-1, 2, 10):
            with self.subTest(target=target):
                self.assertEqual(algorithms.binary_search(numbers, target), -1)

    def test_empty_sequence_returns_minus_one(self) -> None:
        self.assertEqual(algorithms.binary_search([], 42), -1)

    def test_accepts_tuple_as_sequence(self) -> None:
        self.assertEqual(algorithms.binary_search((2, 4, 6, 8), 6), 2)

    def test_duplicate_target_returns_a_valid_matching_index(self) -> None:
        numbers = [1, 2, 2, 2, 3]
        index = algorithms.binary_search(numbers, 2)
        self.assertIn(index, (1, 2, 3))
        self.assertEqual(numbers[index], 2)

    def test_does_not_modify_input(self) -> None:
        numbers = [1, 3, 5, 7]
        original = numbers.copy()
        algorithms.binary_search(numbers, 5)
        self.assertEqual(numbers, original)

    def test_rejects_value_without_sequence_protocol(self) -> None:
        with self.assertRaises(TypeError):
            algorithms.binary_search(None, 1)


class ValidBracketsTests(unittest.TestCase):
    """Tests for stack-based bracket validation."""

    def test_accepts_nested_and_adjacent_pairs(self) -> None:
        for text in ("()", "()[]{}", "{[()]()}", "(((())))"):
            with self.subTest(text=text):
                self.assertTrue(algorithms.valid_brackets(text))

    def test_rejects_mismatched_or_unclosed_brackets(self) -> None:
        for text in ("(", "([)]", "(]", "(()", "{[}"):
            with self.subTest(text=text):
                self.assertFalse(algorithms.valid_brackets(text))

    def test_rejects_closing_bracket_without_opening_bracket(self) -> None:
        for text in (")", "hello]", "}{}"):
            with self.subTest(text=text):
                self.assertFalse(algorithms.valid_brackets(text))

    def test_ignores_non_bracket_characters(self) -> None:
        self.assertTrue(algorithms.valid_brackets("if (a[0] == value) { ok(); }"))
        self.assertTrue(algorithms.valid_brackets("plain text"))

    def test_empty_string_is_valid(self) -> None:
        self.assertTrue(algorithms.valid_brackets(""))

    def test_none_is_not_iterable(self) -> None:
        with self.assertRaises(TypeError):
            algorithms.valid_brackets(None)


class FibonacciDynamicTests(unittest.TestCase):
    """Tests for the iterative Fibonacci implementation."""

    def test_base_cases_and_known_sequence_values(self) -> None:
        expected = {
            0: 0,
            1: 1,
            2: 1,
            3: 2,
            5: 5,
            10: 55,
            20: 6765,
        }
        for number, result in expected.items():
            with self.subTest(number=number):
                self.assertEqual(algorithms.fibonacci_dynamic(number), result)

    def test_handles_larger_value_without_recursion(self) -> None:
        self.assertEqual(
            algorithms.fibonacci_dynamic(50),
            12_586_269_025,
        )

    def test_rejects_non_numeric_input(self) -> None:
        with self.assertRaises(TypeError):
            algorithms.fibonacci_dynamic("10")

    def test_non_integral_loop_bound_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            algorithms.fibonacci_dynamic(2.5)


if __name__ == "__main__":
    unittest.main()
