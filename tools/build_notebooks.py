"""Build deterministic tutorial notebooks with nbformat.

Run this script after editing notebook content, then execute the generated
notebooks with ``python -m jupyter nbconvert --execute --to notebook --inplace``.
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"


def markdown(source: str):
    return new_markdown_cell(dedent(source).strip())


def code(source: str):
    return new_code_cell(dedent(source).strip())


def notebook(cells):
    return new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.11",
            },
        },
    )


def mutability_notebook():
    return notebook(
        [
            markdown(
                """
                # Python 可变对象、引用与拷贝

                ## Goal

                通过可以逐格执行的实验理解赋值、浅拷贝、深拷贝、函数参数和可变默认参数。
                每个实验都遵循“先预测，再运行，最后用 `assert` 验证”的方式。
                """
            ),
            markdown(
                """
                ## Setup

                本教程只使用 Python 标准库，没有外部数据，也不依赖前面运行过的隐藏状态。
                """
            ),
            code(
                """
                import copy


                def inspect_value(name, value):
                    print(
                        f"{name:<10} value={value!r:<24} "
                        f"type={type(value).__name__:<8} id={id(value)}"
                    )
                """
            ),
            markdown(
                """
                ## Steps

                ### 1. 赋值不是复制

                `alias = original` 只增加一个名字，两个名字仍指向同一个列表。
                """
            ),
            code(
                """
                original = [[1, 2], [3, 4]]
                alias = original

                inspect_value("original", original)
                inspect_value("alias", alias)
                print("同一个对象:", original is alias)
                """
            ),
            markdown(
                """
                ### 2. 对比浅拷贝和深拷贝

                浅拷贝创建新的外层列表，但继续共享内层列表；深拷贝递归复制嵌套对象。
                """
            ),
            code(
                """
                original = [[1, 2], [3, 4]]
                shallow = original.copy()
                deep = copy.deepcopy(original)

                original[0].append(99)

                print("original:", original)
                print("shallow :", shallow)
                print("deep    :", deep)
                print("外层共享:", original is shallow)
                print("浅拷贝内层共享:", original[0] is shallow[0])
                print("深拷贝内层共享:", original[0] is deep[0])
                """
            ),
            markdown(
                """
                ### 3. 函数收到的是对象引用

                重新绑定局部变量不会改变调用者的名字，但修改可变对象本身会被调用者观察到。
                """
            ),
            code(
                """
                def rebind(items):
                    items = ["函数中的新列表"]
                    return items


                def mutate(items):
                    items.append("函数添加")


                values = ["原值"]
                rebound = rebind(values)
                print("重新绑定后:", values, rebound)

                mutate(values)
                print("原地修改后:", values)
                """
            ),
            markdown(
                """
                ### 4. 可变默认参数陷阱

                默认参数在函数定义时创建一次，而不是每次调用时创建。
                """
            ),
            code(
                """
                def append_bad(value, items=[]):  # noqa: B006 - 故意演示反例
                    items.append(value)
                    return items


                def append_good(value, items=None):
                    if items is None:
                        items = []
                    items.append(value)
                    return items


                print("错误:", append_bad("A"), append_bad("B"))
                print("正确:", append_good("A"), append_good("B"))
                """
            ),
            markdown("## Checks"),
            code(
                """
                source = [[1], [2]]
                shallow = source.copy()
                deep = copy.deepcopy(source)

                assert source is not shallow
                assert source[0] is shallow[0]
                assert source[0] is not deep[0]

                source[0].append(3)
                assert shallow == [[1, 3], [2]]
                assert deep == [[1], [2]]
                print("所有引用和拷贝检查通过。")
                """
            ),
            markdown(
                """
                ## Next Steps

                1. 把内层列表换成不可变元组，观察浅拷贝是否仍有风险。
                2. 给列表中加入自定义类实例，再比较三种复制方式。
                3. 在 VS Code 变量面板中观察外层和内层对象的 `id()`。
                """
            ),
        ]
    )


def functions_notebook():
    return notebook(
        [
            markdown(
                """
                # 闭包、装饰器、迭代器与生成器

                ## Goal

                理解函数是一等对象、闭包如何保存状态、装饰器如何包装函数，以及生成器为何是惰性计算。
                """
            ),
            markdown("## Setup"),
            code(
                """
                from functools import wraps
                from itertools import islice
                """
            ),
            markdown(
                """
                ## Steps

                ### 1. 函数是一等对象

                函数可以赋给变量、作为参数传入，也可以作为返回值。
                """
            ),
            code(
                """
                def add(left, right):
                    return left + right


                operation = add
                print("函数对象:", operation.__name__)
                print("调用结果:", operation(2, 3))
                """
            ),
            markdown("### 2. 闭包保存外层状态"),
            code(
                """
                def counter_factory(start=0):
                    count = start

                    def increment(step=1):
                        nonlocal count
                        count += step
                        return count

                    return increment


                counter_a = counter_factory()
                counter_b = counter_factory(100)
                print("A:", counter_a(), counter_a(5))
                print("B:", counter_b(), counter_b())
                """
            ),
            markdown("### 3. 装饰器增加横切功能"),
            code(
                """
                def trace(func):
                    @wraps(func)
                    def wrapper(*args, **kwargs):
                        print(f"调用 {func.__name__}{args}")
                        result = func(*args, **kwargs)
                        print(f"返回 {result!r}")
                        return result

                    return wrapper


                @trace
                def multiply(left, right):
                    return left * right


                product = multiply(6, 7)
                print("函数名仍被保留:", multiply.__name__)
                """
            ),
            markdown(
                """
                ### 4. 生成器按需计算

                调用生成器函数时，函数体尚未执行；每次 `next()` 才推进到下一个 `yield`。
                """
            ),
            code(
                """
                def fibonacci():
                    left, right = 0, 1
                    while True:
                        yield left
                        left, right = right, left + right


                sequence = fibonacci()
                print("生成器对象:", sequence)
                print("前 8 项:", list(islice(sequence, 8)))
                """
            ),
            markdown("### 5. 自定义迭代器协议"),
            code(
                """
                class Countdown:
                    def __init__(self, start):
                        self.current = start

                    def __iter__(self):
                        return self

                    def __next__(self):
                        if self.current == 0:
                            raise StopIteration
                        value = self.current
                        self.current -= 1
                        return value


                print("倒计时:", list(Countdown(5)))
                """
            ),
            markdown("## Checks"),
            code(
                """
                assert product == 42
                assert counter_a() == 7
                assert list(Countdown(3)) == [3, 2, 1]
                assert list(islice(fibonacci(), 7)) == [0, 1, 1, 2, 3, 5, 8]
                print("所有函数与迭代协议检查通过。")
                """
            ),
            markdown(
                """
                ## Next Steps

                1. 给 `trace` 增加耗时统计。
                2. 写一个可以重复迭代的 `CountdownIterable`，让 `__iter__` 返回新的迭代器。
                3. 比较列表推导式和生成器表达式的内存占用。
                """
            ),
        ]
    )


def algorithms_notebook():
    return notebook(
        [
            markdown(
                """
                # 算法正确性、测试与复杂度

                ## Goal

                以“两数之和”为例，对比暴力搜索与哈希表方案，并用参数化样例验证边界条件。
                """
            ),
            markdown(
                """
                ## Setup

                使用固定输入和标准库 `timeit`。耗时只用于观察数量级，不能作为严格性能承诺。
                """
            ),
            code(
                """
                from timeit import repeat
                """
            ),
            markdown(
                """
                ## Steps

                ### 1. 暴力方案

                枚举所有数对，时间复杂度为 $O(n^2)$，额外空间为 $O(1)$。
                """
            ),
            code(
                """
                def two_sum_brute(numbers, target):
                    for left in range(len(numbers)):
                        for right in range(left + 1, len(numbers)):
                            if numbers[left] + numbers[right] == target:
                                return [left, right]
                    return []
                """
            ),
            markdown(
                """
                ### 2. 哈希表方案

                扫描时记录已经见过的数字，平均时间复杂度为 $O(n)$，额外空间为 $O(n)$。
                """
            ),
            code(
                """
                def two_sum_hash(numbers, target):
                    seen = {}
                    for index, number in enumerate(numbers):
                        complement = target - number
                        if complement in seen:
                            return [seen[complement], index]
                        seen[number] = index
                    return []
                """
            ),
            markdown("### 3. 先验证正确性"),
            code(
                """
                cases = [
                    ([2, 7, 11, 15], 9, [0, 1]),
                    ([3, 2, 4], 6, [1, 2]),
                    ([3, 3], 6, [0, 1]),
                    ([], 1, []),
                    ([1, 2, 3], 100, []),
                ]

                for numbers, target, expected in cases:
                    brute = two_sum_brute(numbers, target)
                    hashed = two_sum_hash(numbers, target)
                    print(numbers, target, "=>", brute, hashed)
                    assert brute == expected
                    assert hashed == expected
                """
            ),
            markdown("### 4. 再观察性能趋势"),
            code(
                """
                sample = list(range(500))
                impossible_target = -1

                brute_times = repeat(
                    lambda: two_sum_brute(sample, impossible_target),
                    number=10,
                    repeat=3,
                )
                hash_times = repeat(
                    lambda: two_sum_hash(sample, impossible_target),
                    number=10,
                    repeat=3,
                )

                print(f"暴力方案最佳耗时: {min(brute_times):.6f} 秒")
                print(f"哈希方案最佳耗时: {min(hash_times):.6f} 秒")
                print(f"本次实验速度比约为: {min(brute_times) / min(hash_times):.1f}x")
                """
            ),
            markdown("## Checks"),
            code(
                """
                for size in [0, 1, 2, 10, 50]:
                    numbers = list(range(size))
                    target = size * 3 + 1
                    assert two_sum_brute(numbers, target) == two_sum_hash(numbers, target)

                print("边界与一致性检查通过。")
                """
            ),
            markdown(
                """
                ## Next Steps

                1. 给函数增加类型标注。
                2. 解释为什么哈希表查询是“平均” $O(1)$。
                3. 尝试返回所有满足条件的下标对。
                4. 用 pytest 的 `@pytest.mark.parametrize` 改写样例表。
                """
            ),
        ]
    )


NOTEBOOKS = {
    "01_mutability_and_copy.ipynb": mutability_notebook,
    "02_functions_and_generators.ipynb": functions_notebook,
    "03_algorithms_and_complexity.ipynb": algorithms_notebook,
}


def main() -> None:
    NOTEBOOK_DIR.mkdir(exist_ok=True)
    for filename, factory in NOTEBOOKS.items():
        path = NOTEBOOK_DIR / filename
        nbformat.write(factory(), path)
        print(f"created {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
