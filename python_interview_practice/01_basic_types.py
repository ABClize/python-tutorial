"""基础类型：建议逐行打断点并观察变量变化。"""


def string_examples():
    text = "  python interview  "
    print("原字符串:", repr(text))
    print("去空格并大写:", text.strip().upper())
    print("切片 [2:8]:", text[2:8])
    print("倒序:", text[::-1])
    print("单词列表:", text.split())
    print("替换:", text.replace("interview", "practice"))
    print("f-string:", f"{text.strip()!r} 长度为 {len(text.strip())}")


def list_tuple_examples():
    numbers = [3, 1, 4, 1, 5]
    numbers.append(9)
    numbers.extend([2, 6])
    print("列表:", numbers)
    print("排序后的新列表:", sorted(numbers))
    print("原列表不变:", numbers)

    point = (10, 20)  # 元组不可修改，适合表示固定结构的数据
    x, y = point  # 解包
    first, *middle, last = numbers
    print("元组解包:", x, y)
    print("星号解包:", first, middle, last)


def dict_set_examples():
    scores = {"alice": 90, "bob": 82}
    scores["carol"] = 95
    print("字典 keys:", list(scores.keys()))
    print("安全取值:", scores.get("david", 0))
    print("字典推导式:", {name: score + 5 for name, score in scores.items()})

    left = {1, 2, 3, 4}
    right = {3, 4, 5, 6}
    print("集合去重:", set([1, 1, 2, 2, 3]))
    print("交集/并集/差集:", left & right, left | right, left - right)


def identity_and_truthiness():
    first = [1, 2]
    second = [1, 2]
    alias = first
    print("== 比较值:", first == second)
    print("is 比较是否同一个对象:", first is second, first is alias)

    values = [0, 1, "", "hello", [], [1], None, False, True]
    for value in values:
        print(f"bool({value!r}) = {bool(value)}")


def main():
    print("\n--- 字符串 ---")
    string_examples()
    print("\n--- 列表与元组 ---")
    list_tuple_examples()
    print("\n--- 字典与集合 ---")
    dict_set_examples()
    print("\n--- 比较和真值 ---")
    identity_and_truthiness()


if __name__ == "__main__":
    main()
