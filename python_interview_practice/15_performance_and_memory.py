"""Python 性能与内存面试示例。

本文件覆盖：
- timeit：重复执行小段代码，避免手写计时器的常见误差
- cProfile：先定位耗时函数，再决定优化哪里
- tracemalloc：比较两次内存快照，定位 Python 内存分配
- __slots__：省去每个普通实例的 __dict__，降低大量实例的开销
- generator：按需生成数据，避免一次性保存全部元素

性能数字受 Python 版本、操作系统和当前负载影响，所以本文件不对具体时间或字节数
做脆弱断言。可以稳定验证的是：结果正确、调用次数正确，以及示例采用的计算模型。
优化的一般顺序是：明确目标 -> 基准测试 -> profile -> 修改 -> 再次基准测试。
"""

from __future__ import annotations

import cProfile
import gc
import sys
import timeit
import tracemalloc
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from typing import Any


def title(text: str) -> None:
    print(f"\n--- {text} ---")


def best_time(
    function: Callable[[], Any],
    *,
    repeat: int = 5,
    number: int = 1_000,
) -> float:
    """返回多轮计时的最小值，减少偶发系统调度噪声的影响。"""
    timer = timeit.Timer(function)
    return min(timer.repeat(repeat=repeat, number=number)) / number


def timeit_demo() -> None:
    """比较列表和集合的成员查询；不要把一次测量当成普遍定律。"""
    title("timeit 微基准")

    numbers_list = list(range(5_000))
    numbers_set = set(numbers_list)
    missing = -1

    list_seconds = best_time(lambda: missing in numbers_list)
    set_seconds = best_time(lambda: missing in numbers_set)

    print(f"列表成员查询（最佳平均）: {list_seconds * 1_000_000:.2f} μs")
    print(f"集合成员查询（最佳平均）: {set_seconds * 1_000_000:.2f} μs")
    print("复杂度模型: list 查询 O(n)，set 平均查询 O(1)")

    # timeit 也能计时语句字符串，但可调用对象通常更容易重构和复用。
    comprehension_seconds = timeit.timeit(
        "[number * number for number in range(100)]",
        number=2_000,
    )
    loop_seconds = timeit.timeit(
        "result = []\nfor number in range(100):\n    result.append(number * number)",
        number=2_000,
    )
    print(
        "列表推导 / 普通循环（总秒数）:",
        f"{comprehension_seconds:.4f}",
        f"{loop_seconds:.4f}",
    )
    print("提示: 微基准应预热、重复，并确保比较双方完成同样的工作")


def normalize_words(lines: Iterable[str]) -> list[str]:
    """将文本拆词并标准化；故意写成 profile 中可识别的独立函数。"""
    return [
        word.strip(".,!?").casefold()
        for line in lines
        for word in line.split()
        if word.strip(".,!?")
    ]


def count_words(words: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return counts


def profiling_workload(rounds: int = 200) -> int:
    lines = [
        "Python code should be clear.",
        "Clear code is easier to test.",
        "Profile code before optimizing.",
    ]
    total_unique_words = 0
    for _ in range(rounds):
        words = normalize_words(lines)
        total_unique_words += len(count_words(words))
    return total_unique_words


def cprofile_demo() -> None:
    """cProfile 是确定性 profiler：记录每个函数的调用次数和累计耗时。"""
    title("cProfile 定位热点")

    profiler = cProfile.Profile()
    result = profiler.runcall(profiling_workload, 200)

    # getstats 返回结构化数据。这里只展示调用次数，避免把随机器变化的耗时
    # 当作固定答案；真实排查时可使用 `python -m cProfile -s cumulative script.py`。
    interesting_names = {"profiling_workload", "normalize_words", "count_words"}
    call_counts: dict[str, int] = {}
    for entry in profiler.getstats():
        code = entry.code
        name = code.co_name if hasattr(code, "co_name") else str(code)
        if name in interesting_names:
            call_counts[name] = entry.callcount

    print("工作负载结果:", result)
    print("关键函数调用次数:", dict(sorted(call_counts.items())))
    print("实战中重点查看 cumulative time，而不只是单次函数耗时")
    assert result == 2_400
    assert call_counts == {
        "count_words": 200,
        "normalize_words": 200,
        "profiling_workload": 1,
    }


def allocate_records(count: int) -> list[dict[str, object]]:
    """创建可被 tracemalloc 追踪的纯 Python 对象。"""
    return [
        {
            "id": index,
            "name": f"user-{index}",
            "scores": [index, index + 1, index + 2],
        }
        for index in range(count)
    ]


def tracemalloc_demo() -> None:
    """快照差异比单看某个时刻的总内存更容易定位增长来源。"""
    title("tracemalloc 内存快照")

    gc.collect()
    tracemalloc.start()
    before = tracemalloc.take_snapshot()

    records = allocate_records(1_000)
    after = tracemalloc.take_snapshot()
    current, peak = tracemalloc.get_traced_memory()

    differences = after.compare_to(before, "lineno")
    positive_bytes = sum(stat.size_diff for stat in differences if stat.size_diff > 0)

    print("记录数量:", len(records))
    print("快照间新增内存:", f"{positive_bytes / 1024:.1f} KiB")
    print(
        "当前 / 峰值追踪内存:",
        f"{current / 1024:.1f} KiB",
        f"{peak / 1024:.1f} KiB",
    )

    # 保持 records 存活到读取快照之后，否则对象可能提前回收，使结果难以解释。
    assert records[999]["name"] == "user-999"
    tracemalloc.stop()


class RegularPoint:
    """普通实例通常把动态属性存放在每个对象自己的 __dict__ 中。"""

    def __init__(self, x: int, y: int, label: str) -> None:
        self.x = x
        self.y = y
        self.label = label


class SlottedPoint:
    """slots 预先声明实例属性，因此默认没有 __dict__。"""

    __slots__ = ("x", "y", "label")

    def __init__(self, x: int, y: int, label: str) -> None:
        self.x = x
        self.y = y
        self.label = label


@dataclass(slots=True)
class SlottedDataPoint:
    """Python 3.10+ 的 dataclass(slots=True) 可减少手写样板代码。"""

    x: int
    y: int
    label: str


def total_shallow_size(objects: Iterable[object]) -> int:
    """估算实例及其 __dict__ 的浅层大小，不递归计算共享属性值。"""
    total = 0
    for obj in objects:
        total += sys.getsizeof(obj)
        attributes = getattr(obj, "__dict__", None)
        if attributes is not None:
            total += sys.getsizeof(attributes)
    return total


def slots_demo() -> None:
    title("__slots__ 与大量小对象")

    regular = [RegularPoint(index, index + 1, "P") for index in range(5_000)]
    slotted = [SlottedPoint(index, index + 1, "P") for index in range(5_000)]
    dataclass_slotted = [SlottedDataPoint(index, index + 1, "P") for index in range(5_000)]

    regular_size = total_shallow_size(regular)
    slotted_size = total_shallow_size(slotted)
    dataclass_size = total_shallow_size(dataclass_slotted)

    print("普通实例浅层总大小:", f"{regular_size / 1024:.1f} KiB")
    print("slots 实例浅层总大小:", f"{slotted_size / 1024:.1f} KiB")
    print("slots dataclass 浅层总大小:", f"{dataclass_size / 1024:.1f} KiB")
    print("普通实例有 __dict__:", hasattr(regular[0], "__dict__"))
    print("slots 实例有 __dict__:", hasattr(slotted[0], "__dict__"))

    try:
        slotted[0].color = "red"  # type: ignore[attr-defined]
    except AttributeError:
        print("未在 slots 中声明的属性不能动态添加")

    print("注意: getsizeof 是浅层估算，严谨结论应结合 tracemalloc 和真实数据")


def square_generator(limit: int) -> Iterator[int]:
    """调用函数时先得到生成器；每次 next 才运行到下一个 yield。"""
    for number in range(limit):
        yield number * number


def generator_memory_demo() -> None:
    title("generator 的惰性内存模型")

    limit = 20_000
    squares_list = [number * number for number in range(limit)]
    squares_generator = square_generator(limit)

    print("列表容器浅层大小:", f"{sys.getsizeof(squares_list) / 1024:.1f} KiB")
    print("生成器对象浅层大小:", f"{sys.getsizeof(squares_generator)} B")
    print("生成器前三项:", [next(squares_generator) for _ in range(3)])

    # 新建生成器再求和，因为上一个生成器已经消费了三项；生成器是一次性的。
    generator_total = sum(square_generator(limit))
    list_total = sum(squares_list)
    print("两种方式计算结果相同:", generator_total == list_total)
    print("列表可重复遍历；生成器节省内存，但消费后不能自动回到开头")
    assert generator_total == list_total


def main() -> None:
    timeit_demo()
    cprofile_demo()
    tracemalloc_demo()
    slots_demo()
    generator_memory_demo()


if __name__ == "__main__":
    main()
