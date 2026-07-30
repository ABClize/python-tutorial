"""基础类型：建议逐行打断点并观察变量变化。"""

import re


def string_examples():
    text = "  python interview  "
    print("原字符串:", repr(text))
    print("去空格并大写:", text.strip().upper())
    print("切片 [2:8]:", text[2:8])
    print("倒序:", text[::-1])
    print("单词列表:", text.split())
    print("替换:", text.replace("interview", "practice"))
    print("f-string:", f"{text.strip()!r} 长度为 {len(text.strip())}")


def square(number: int) -> int:
    return number * number


def is_even(number: int) -> bool:
    return number % 2 == 0


def builtin_function_examples() -> None:
    numbers = [-3, 7, 2]
    print("长度/总和:", len(numbers), sum(numbers))
    print("最小/最大:", min(numbers), max(numbers))
    print("绝对值/舍入:", abs(numbers[0]), round(3.14159, 2))
    print(
        "any/all:",
        any(number > 5 for number in numbers),
        all(number > 0 for number in numbers),
    )
    print("map:", list(map(square, numbers)))
    print("filter:", list(filter(is_even, numbers)))


def control_flow_examples() -> None:
    for status in ["ready", "skip"]:
        if status == "skip":
            pass
        print("pass 不跳过后续代码:", status)

    for number in [2, 4, 6]:
        if number % 2 != 0:
            print("找到奇数:", number)
            break
    else:
        print("循环 else: 没有找到奇数")

    status_code = 404
    match status_code:
        case 200:
            message = "成功"
        case 400 | 404:
            message = "请求错误"
        case _:
            message = "其他状态"
    print("字面量与 OR 模式:", message)

    command: list[object] = ["move", 3, 5]
    match command:
        case ["move", int(x), int(y)] if x >= 0 and y >= 0:
            result = f"移动到 ({x}, {y})"
        case ["move", _, _]:
            result = "坐标格式错误"
        case ["quit"]:
            result = "退出"
        case _:
            result = "未知命令"
    print("序列模式与 guard:", result)

    value = "failed"
    match value:
        case captured:
            print("裸名字捕获:", captured)


def text_bytes_regex_examples() -> None:
    price = 12.5
    ratio = 0.376
    count = 7
    print(
        "f-string 格式:",
        f"{price:.2f}",
        f"{ratio:.1%}",
        f"{count:04d}",
        f"{price:>8.2f}",
    )

    print("2026", "07", "30", sep="-")
    print("加载", end="...")
    print("完成")

    text = "Python你好"
    data = text.encode("utf-8")
    print("UTF-8 编码:", data)
    print("UTF-8 解码:", data.decode("utf-8"))

    try:
        data.decode("ascii")
    except UnicodeDecodeError as error:
        print("编码不匹配:", type(error).__name__)

    order_text = "订单 A-102 和 B-205 已创建"
    pattern = r"[A-Z]-\d+"
    first = re.search(pattern, order_text)
    print("search:", first.group() if first else None)
    print("findall:", re.findall(pattern, order_text))
    print("sub:", re.sub(pattern, "编号", order_text))


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
    print("\n--- 常用内置函数 ---")
    builtin_function_examples()
    print("\n--- 条件、循环与模式匹配 ---")
    control_flow_examples()
    print("\n--- 文本、字节与正则 ---")
    text_bytes_regex_examples()
    print("\n--- 列表与元组 ---")
    list_tuple_examples()
    print("\n--- 字典与集合 ---")
    dict_set_examples()
    print("\n--- 比较和真值 ---")
    identity_and_truthiness()


if __name__ == "__main__":
    main()
