"""小练习与参考实现。先遮住函数体自己写，再对照答案。"""


def reverse_words(sentence):
    """题：翻转句子中单词的顺序，并忽略多余空格。"""
    return " ".join(reversed(sentence.split()))


def first_non_repeating_char(text: str) -> str | None:
    """题：返回第一个只出现一次的字符；不存在则返回 None。"""
    counts: dict[str, int] = {}
    for char in text:
        counts[char] = counts.get(char, 0) + 1
    for char in text:
        if counts[char] == 1:
            return char
    return None


def flatten_once(items):
    """题：将二维列表展平一层。"""
    return [value for group in items for value in group]


def merge_sorted(left, right):
    """题：合并两个有序列表，不使用 sorted。"""
    result = []
    left_index = right_index = 0
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


def group_anagrams(words: list[str]) -> list[list[str]]:
    """题：把由相同字母组成的单词分为一组。"""
    groups: dict[str, list[str]] = {}
    for word in words:
        key = "".join(sorted(word))
        groups.setdefault(key, []).append(word)
    return list(groups.values())


def run_checks():
    """用 assert 做最简单的自动校验；失败时会抛出 AssertionError。"""
    assert reverse_words("  I  love Python ") == "Python love I"
    assert first_non_repeating_char("aabbcdde") == "c"
    assert first_non_repeating_char("aabb") is None
    assert flatten_once([[1, 2], [3], [], [4, 5]]) == [1, 2, 3, 4, 5]
    assert merge_sorted([1, 4, 7], [2, 3, 8]) == [1, 2, 3, 4, 7, 8]
    assert group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]) == [
        ["eat", "tea", "ate"],
        ["tan", "nat"],
        ["bat"],
    ]


def main():
    run_checks()
    print("全部 assert 校验通过。")
    print("翻转单词:", reverse_words("  Python makes coding fun  "))
    print("首个唯一字符:", first_non_repeating_char("swiss"))
    print("展平:", flatten_once([[1, 2], [3, 4]]))
    print("合并有序列表:", merge_sorted([1, 5], [2, 3, 6]))
    print("字母异位词分组:", group_anagrams(["listen", "silent", "enlist", "rat", "tar"]))


if __name__ == "__main__":
    main()
