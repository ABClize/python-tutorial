"""Tests for ``python_interview_practice/09_practice_questions.py``."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "python_interview_practice" / "09_practice_questions.py"
)
SPEC = importlib.util.spec_from_file_location(
    "interview_practice_questions",
    MODULE_PATH,
)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"无法从路径加载模块: {MODULE_PATH}")
practice = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(practice)


class ReverseWordsTests(unittest.TestCase):
    """Tests for reversing whitespace-delimited words."""

    def test_reverses_words(self) -> None:
        self.assertEqual(
            practice.reverse_words("Python makes coding fun"),
            "fun coding makes Python",
        )

    def test_collapses_leading_trailing_and_repeated_whitespace(self) -> None:
        self.assertEqual(
            practice.reverse_words("  I  love Python "),
            "Python love I",
        )

    def test_treats_tabs_and_newlines_as_whitespace(self) -> None:
        self.assertEqual(
            practice.reverse_words("one\ttwo\nthree"),
            "three two one",
        )

    def test_empty_or_whitespace_only_input_returns_empty_string(self) -> None:
        for sentence in ("", " ", "\t\n"):
            with self.subTest(sentence=sentence):
                self.assertEqual(practice.reverse_words(sentence), "")

    def test_none_has_no_split_method(self) -> None:
        with self.assertRaises(AttributeError):
            practice.reverse_words(None)


class FirstNonRepeatingCharacterTests(unittest.TestCase):
    """Tests for finding the first character with frequency one."""

    def test_returns_first_unique_character(self) -> None:
        self.assertEqual(practice.first_non_repeating_char("swiss"), "w")
        self.assertEqual(practice.first_non_repeating_char("aabbcdde"), "c")

    def test_can_return_first_or_last_character(self) -> None:
        self.assertEqual(practice.first_non_repeating_char("abcab"), "c")
        self.assertEqual(practice.first_non_repeating_char("aabbc"), "c")

    def test_returns_none_when_no_unique_character_exists(self) -> None:
        for text in ("", "aabb", "zzzz"):
            with self.subTest(text=text):
                self.assertIsNone(practice.first_non_repeating_char(text))

    def test_is_case_sensitive(self) -> None:
        self.assertEqual(practice.first_non_repeating_char("aAabb"), "A")

    def test_supports_unicode_characters(self) -> None:
        self.assertEqual(practice.first_non_repeating_char("你好吗你好"), "吗")

    def test_none_is_not_iterable(self) -> None:
        with self.assertRaises(TypeError):
            practice.first_non_repeating_char(None)


class FlattenOnceTests(unittest.TestCase):
    """Tests for flattening one level of nested iterables."""

    def test_flattens_nested_lists_one_level(self) -> None:
        self.assertEqual(
            practice.flatten_once([[1, 2], [3], [], [4, 5]]),
            [1, 2, 3, 4, 5],
        )

    def test_handles_empty_outer_or_inner_lists(self) -> None:
        self.assertEqual(practice.flatten_once([]), [])
        self.assertEqual(practice.flatten_once([[], [], []]), [])

    def test_accepts_other_inner_iterables(self) -> None:
        self.assertEqual(
            practice.flatten_once([(1, 2), range(3, 5), "ab"]),
            [1, 2, 3, 4, "a", "b"],
        )

    def test_flattens_exactly_one_level(self) -> None:
        nested = [[[1], [2]], [[3]]]
        self.assertEqual(practice.flatten_once(nested), [[1], [2], [3]])

    def test_does_not_modify_input(self) -> None:
        items = [[1, 2], [3]]
        original = [group.copy() for group in items]
        practice.flatten_once(items)
        self.assertEqual(items, original)

    def test_non_iterable_inner_item_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            practice.flatten_once([[1, 2], 3])


class MergeSortedTests(unittest.TestCase):
    """Tests for merging two ascending indexable sequences."""

    def test_merges_interleaved_sorted_lists(self) -> None:
        self.assertEqual(
            practice.merge_sorted([1, 4, 7], [2, 3, 8]),
            [1, 2, 3, 4, 7, 8],
        )

    def test_handles_empty_inputs(self) -> None:
        self.assertEqual(practice.merge_sorted([], []), [])
        self.assertEqual(practice.merge_sorted([1, 2], []), [1, 2])
        self.assertEqual(practice.merge_sorted([], [3, 4]), [3, 4])

    def test_preserves_duplicates(self) -> None:
        self.assertEqual(
            practice.merge_sorted([1, 2, 2, 5], [2, 2, 3]),
            [1, 2, 2, 2, 2, 3, 5],
        )

    def test_handles_negative_numbers(self) -> None:
        self.assertEqual(
            practice.merge_sorted([-5, -1, 4], [-3, 0, 2]),
            [-5, -3, -1, 0, 2, 4],
        )

    def test_accepts_tuples(self) -> None:
        self.assertEqual(
            practice.merge_sorted((1, 5), (2, 3, 6)),
            [1, 2, 3, 5, 6],
        )

    def test_does_not_modify_inputs(self) -> None:
        left = [1, 4]
        right = [2, 3]
        left_original = left.copy()
        right_original = right.copy()
        practice.merge_sorted(left, right)
        self.assertEqual(left, left_original)
        self.assertEqual(right, right_original)

    def test_incomparable_values_raise_type_error(self) -> None:
        with self.assertRaises(TypeError):
            practice.merge_sorted([1], ["2"])


class GroupAnagramsTests(unittest.TestCase):
    """Tests for grouping words by their sorted-character signature."""

    def test_groups_typical_anagrams(self) -> None:
        self.assertEqual(
            practice.group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]),
            [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]],
        )

    def test_handles_empty_input(self) -> None:
        self.assertEqual(practice.group_anagrams([]), [])

    def test_groups_empty_strings_and_duplicate_words(self) -> None:
        self.assertEqual(
            practice.group_anagrams(["", "", "a", "a"]),
            [["", ""], ["a", "a"]],
        )

    def test_grouping_is_case_sensitive(self) -> None:
        self.assertEqual(
            practice.group_anagrams(["Tea", "Eat", "tea", "ate"]),
            [["Tea"], ["Eat"], ["tea", "ate"]],
        )

    def test_keeps_first_seen_group_and_word_order(self) -> None:
        words = ["rat", "listen", "tar", "silent", "art", "enlist"]
        self.assertEqual(
            practice.group_anagrams(words),
            [
                ["rat", "tar", "art"],
                ["listen", "silent", "enlist"],
            ],
        )

    def test_does_not_modify_input(self) -> None:
        words = ["eat", "tea", "bat"]
        original = words.copy()
        practice.group_anagrams(words)
        self.assertEqual(words, original)

    def test_non_iterable_word_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            practice.group_anagrams(["abc", 123])


class BuiltInChecksTests(unittest.TestCase):
    """Keep the source file's own assert-based examples as a regression test."""

    def test_run_checks_completes_without_assertion(self) -> None:
        self.assertIsNone(practice.run_checks())


if __name__ == "__main__":
    unittest.main()
