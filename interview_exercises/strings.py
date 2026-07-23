"""字符串类面试题。

学习建议：先折叠每个函数的实现，只阅读文档字符串并自己完成。
"""

from __future__ import annotations

# 直接运行本文件时，脚本目录位于 sys.path 首位，其中的 collections.py
# 会遮蔽同名标准库。包导入时没有这个问题。
import sys

if __package__ in (None, "") and sys.path:
    sys.path.pop(0)

from collections import Counter, defaultdict


def normalize_for_anagram(text: str) -> str:
    """统一大小写，并忽略空白和标点。

    `casefold` 比 `lower` 更适合处理 Unicode 文本。
    """

    return "".join(character.casefold() for character in text if character.isalnum())


def are_anagrams(left: str, right: str) -> bool:
    """题目：判断两个字符串是否互为字母异位词。

    这里约定忽略大小写、空白和标点。例如 ``Dormitory`` 与
    ``Dirty room!!`` 被视为异位词。

    时间复杂度：O(n + m)
    空间复杂度：O(k)，k 是不同字符的数量
    """

    return Counter(normalize_for_anagram(left)) == Counter(normalize_for_anagram(right))


def longest_unique_substring(text: str) -> str:
    """题目：返回不含重复字符的最长连续子串。

    若有多个同样长的答案，返回最早出现的一个。

    解法：滑动窗口保存字符最后一次出现的位置。窗口左边界只向右移动。
    时间复杂度：O(n)
    空间复杂度：O(k)，k 是窗口中可能出现的不同字符数
    """

    last_seen: dict[str, int] = {}
    left = 0
    best_start = 0
    best_length = 0

    for right, character in enumerate(text):
        previous = last_seen.get(character)
        if previous is not None and previous >= left:
            left = previous + 1

        last_seen[character] = right
        current_length = right - left + 1
        if current_length > best_length:
            best_start = left
            best_length = current_length

    return text[best_start : best_start + best_length]


def group_anagrams(words: list[str]) -> list[list[str]]:
    """题目：把互为字母异位词的单词放进同一组。

    分组顺序和组内顺序都保持输入首次出现的顺序，便于稳定测试。
    本题只忽略大小写，不忽略单词内的其他字符。

    时间复杂度：O(n * k log k)，k 是单词平均长度
    空间复杂度：O(n * k)
    """

    groups: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for word in words:
        signature = tuple(sorted(word.casefold()))
        groups[signature].append(word)
    return list(groups.values())


def has_valid_brackets(text: str) -> bool:
    """题目：判断文本中的圆括号、方括号和花括号是否正确配对。

    非括号字符会被忽略。栈顶必须匹配当前右括号。

    时间复杂度：O(n)
    空间复杂度：O(n)，最坏情况下全部是左括号
    """

    matching_open = {")": "(", "]": "[", "}": "{"}
    opening = set(matching_open.values())
    stack: list[str] = []

    for character in text:
        if character in opening:
            stack.append(character)
        elif character in matching_open and (not stack or stack.pop() != matching_open[character]):
            return False

    return not stack


def run_length_encode(text: str) -> list[tuple[str, int]]:
    """题目：对字符串进行游程编码。

    返回 ``(字符, 连续次数)`` 列表而不是拼接字符串，因此数字字符和任意
    Unicode 字符都不会产生歧义。

    时间复杂度：O(n)
    空间复杂度：O(n)，当相邻字符都不相同时达到最坏情况
    """

    if not text:
        return []

    encoded: list[tuple[str, int]] = []
    current = text[0]
    count = 1

    for character in text[1:]:
        if character == current:
            count += 1
        else:
            encoded.append((current, count))
            current = character
            count = 1

    encoded.append((current, count))
    return encoded


def run_length_decode(encoded: list[tuple[str, int]]) -> str:
    """题目：还原游程编码，并拒绝不合法的次数。

    时间复杂度：O(n + r)，r 是还原后字符串的长度
    空间复杂度：O(r)
    """

    pieces: list[str] = []
    for character, count in encoded:
        if len(character) != 1:
            raise ValueError("每个编码项必须包含一个字符")
        if count <= 0:
            raise ValueError("连续次数必须为正整数")
        pieces.append(character * count)
    return "".join(pieces)


def minimum_window_substring(text: str, target: str) -> str:
    """题目：找出包含 target 中全部字符（含重复次数）的最短子串。

    例如 ``ADOBECODEBANC`` 和 ``ABC`` 的答案是 ``BANC``。
    这是滑动窗口进阶题：右边界负责满足条件，左边界负责缩短答案。

    时间复杂度：O(n + m)
    空间复杂度：O(k)
    """

    if not text or not target:
        return ""

    needed = Counter(target)
    missing = len(target)
    left = 0
    best_start = 0
    best_length = len(text) + 1

    for right, character in enumerate(text):
        if needed[character] > 0:
            missing -= 1
        needed[character] -= 1

        while missing == 0:
            window_length = right - left + 1
            if window_length < best_length:
                best_start = left
                best_length = window_length

            left_character = text[left]
            needed[left_character] += 1
            if needed[left_character] > 0:
                missing += 1
            left += 1

    if best_length > len(text):
        return ""
    return text[best_start : best_start + best_length]


def run_tests() -> None:
    """覆盖正常输入、空输入、重复字符和非法输入。"""

    assert are_anagrams("Dormitory", "Dirty room!!")
    assert are_anagrams("", "")
    assert not are_anagrams("python", "typhoon!")

    assert longest_unique_substring("abcabcbb") == "abc"
    assert longest_unique_substring("abba") == "ab"
    assert longest_unique_substring("bbbbb") == "b"
    assert longest_unique_substring("") == ""

    assert group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]) == [
        ["eat", "tea", "ate"],
        ["tan", "nat"],
        ["bat"],
    ]
    assert group_anagrams([]) == []

    assert has_valid_brackets("function(a[0], {x: 1})")
    assert not has_valid_brackets("([)]")
    assert not has_valid_brackets("(()")
    assert has_valid_brackets("没有括号")

    samples = ["", "aaabbc", "111122", "你你好吗"]
    for sample in samples:
        assert run_length_decode(run_length_encode(sample)) == sample

    try:
        run_length_decode([("ab", 2)])
    except ValueError:
        pass
    else:
        raise AssertionError("非法编码应该抛出 ValueError")

    assert minimum_window_substring("ADOBECODEBANC", "ABC") == "BANC"
    assert minimum_window_substring("a", "aa") == ""
    assert minimum_window_substring("aa", "aa") == "aa"
    assert minimum_window_substring("anything", "") == ""


def main() -> None:
    run_tests()
    print("最长无重复子串:", longest_unique_substring("pwwkew"))
    print("异位词分组:", group_anagrams(["listen", "silent", "cat", "act"]))
    print("最小覆盖子串:", minimum_window_substring("ADOBECODEBANC", "ABC"))
    print("strings.py：全部测试通过")


if __name__ == "__main__":
    main()
