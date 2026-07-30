"""Python 常用标准库示例。

覆盖：
- argparse：位置参数、可选参数和类型转换
- csv：按字段读写表格文本
- logging：级别、参数化消息和局部日志配置
- decimal、math、random、statistics：精确小数、数学函数、伪随机数和统计量
- functools：缓存、偏函数、归约与单分派
- itertools：惰性迭代、组合、分组和累计
- collections：计数、分组、双端队列、作用域链
- pathlib：跨平台路径处理和文件遍历
- heapq：堆、Top-K 和优先队列
- bisect：在有序序列中二分查找与插入

这些工具通常比手写循环更明确，但仍应理解它们的时间复杂度和边界行为。
"""

from __future__ import annotations

import argparse
import csv
import heapq
import logging
import math
import random
import statistics
from bisect import bisect, bisect_left, bisect_right, insort
from collections import ChainMap, Counter, defaultdict, deque, namedtuple
from decimal import ROUND_HALF_UP, Decimal
from functools import cache, partial, reduce, singledispatch
from io import StringIO
from itertools import (
    accumulate,
    chain,
    combinations,
    count,
    groupby,
    islice,
    pairwise,
    product,
)
from operator import itemgetter, mul
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from typing import Any


def title(text: str) -> None:
    print(f"\n--- {text} ---")


def argparse_demo() -> None:
    """使用固定参数演示 argparse，不读取当前进程的真实命令行。"""
    title("argparse")

    parser = argparse.ArgumentParser(
        prog="study-report",
        description="生成学习记录",
    )
    parser.add_argument("topic", help="学习主题")
    parser.add_argument(
        "-n",
        "--hours",
        type=int,
        default=1,
        help="学习小时数",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="显示详细信息",
    )

    arguments = parser.parse_args(
        ["Python", "--hours", "3", "--verbose"]
    )
    print(
        "解析后的参数:",
        arguments.topic,
        arguments.hours,
        arguments.verbose,
    )


def csv_demo() -> None:
    """在临时目录中确定性地写入和读取 CSV。"""
    title("csv")

    records = [
        {"topic": "Python", "hours": 3},
        {"topic": "SQL", "hours": 2},
    ]

    with TemporaryDirectory() as directory:
        csv_path = Path(directory) / "study.csv"

        with csv_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["topic", "hours"],
            )
            writer.writeheader()
            writer.writerows(records)

        with csv_path.open(
            newline="",
            encoding="utf-8",
        ) as file:
            loaded_rows = list(csv.DictReader(file))

    print("CSV 读取结果:", loaded_rows)
    converted_rows = [
        {
            "topic": row["topic"],
            "hours": int(row["hours"]),
        }
        for row in loaded_rows
    ]
    print("转换 hours 后:", converted_rows)


def logging_demo() -> None:
    """把日志写入内存并恢复 logger 状态，不修改根 logger。"""
    title("logging")

    output = StringIO()
    handler = logging.StreamHandler(output)
    handler.setFormatter(
        logging.Formatter("%(levelname)s:%(message)s")
    )

    logger = logging.getLogger(f"{__name__}.logging_demo")
    previous_level = logger.level
    previous_propagate = logger.propagate
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    try:
        logger.debug("这条 DEBUG 日志不会输出")
        logger.info("已处理 %d 条记录", 2)
        logger.warning("剩余容量为 %d%%", 20)
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous_level)
        logger.propagate = previous_propagate
        handler.close()

    print("日志输出:", output.getvalue().splitlines())


def numeric_tools_demo() -> None:
    """演示精确小数、数学函数、局部伪随机数和基础统计量。"""
    title("decimal / math / random / statistics")

    price = Decimal("19.90")
    print("Decimal 精确计算:", price * 3)
    print("Decimal 小数相加:", Decimal("0.1") + Decimal("0.2"))

    amount = Decimal("10.005")
    rounded = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    print("Decimal 四舍五入:", rounded)

    print("平方根:", math.sqrt(81))
    print("向上取整:", math.ceil(3.2))
    print("向下取整:", math.floor(3.8))
    print("浮点数是否接近:", math.isclose(0.1 + 0.2, 0.3))

    generator = random.Random(2026)
    print("固定种子的骰子:", generator.randint(1, 6))
    print("固定种子的选择:", generator.choice(["红", "蓝", "绿"]))
    print("固定种子的抽样:", generator.sample(range(1, 11), k=3))

    scores = [60, 70, 80, 90, 100]
    print("平均数:", statistics.mean(scores))
    print("中位数:", statistics.median(scores))

    empty_scores: list[int] = []
    try:
        statistics.mean(empty_scores)
    except statistics.StatisticsError:
        print("空数据: StatisticsError")


fibonacci_calls = 0


@cache
def fibonacci(number: int) -> int:
    """缓存递归结果，把指数级重复计算降为线性数量的子问题。"""
    global fibonacci_calls
    fibonacci_calls += 1
    if number < 2:
        return number
    return fibonacci(number - 1) + fibonacci(number - 2)


def power(base: int, exponent: int) -> int | float:
    result = base**exponent
    return float(result) if exponent < 0 else int(result)


@singledispatch
def normalize(value: Any) -> str:
    """默认实现；singledispatch 根据第一个参数的运行时类型分派。"""
    return str(value)


@normalize.register
def _(value: int) -> str:
    return f"整数:{value}"


@normalize.register
def _(value: list) -> str:
    return f"列表:{','.join(map(str, value))}"


def functools_demo() -> None:
    title("functools")

    global fibonacci_calls
    fibonacci.cache_clear()
    fibonacci_calls = 0
    print("带缓存的斐波那契:", fibonacci(10))
    print("真正计算的子问题数:", fibonacci_calls)
    info = fibonacci.cache_info()
    print("缓存命中/未命中:", info.hits, info.misses)

    square = partial(power, exponent=2)
    cube = partial(power, exponent=3)
    print("partial 固定部分参数:", square(5), cube(3))

    values = [1, 2, 3, 4]
    print("reduce 累乘:", reduce(mul, values, 1))
    print("单分派:", normalize(7), normalize(["A", "B"]), normalize(2.5))


def itertools_demo() -> None:
    title("itertools")

    pages = [["A", "B"], ["C"], ["D", "E"]]
    print("chain 展平一层:", list(chain.from_iterable(pages)))

    # count 是无限迭代器，必须用 islice 等方式限制消费数量。
    sequence = islice(count(start=10, step=3), 5)
    print("惰性无限序列的前 5 项:", list(sequence))

    print("累计和:", list(accumulate([3, 1, 4, 2])))
    print("相邻两项:", list(pairwise([10, 20, 35, 50])))
    print("两两组合:", list(combinations(["A", "B", "C"], 2)))
    print("笛卡尔积:", list(product(["红", "蓝"], ["S", "M"])))

    records = [
        {"team": "A", "score": 80},
        {"team": "B", "score": 75},
        {"team": "A", "score": 90},
        {"team": "B", "score": 85},
    ]
    # groupby 只合并连续的相同键，所以分组前通常必须按相同 key 排序。
    ordered = sorted(records, key=itemgetter("team"))
    grouped = {
        team: [record["score"] for record in rows]
        for team, rows in groupby(ordered, key=itemgetter("team"))
    }
    print("排序后 groupby:", grouped)


def collections_demo() -> None:
    title("collections")

    words = ["python", "sql", "python", "git", "sql", "python"]
    counts = Counter(words)
    print("Counter 计数:", counts)
    print("最高频的两个:", counts.most_common(2))
    print("Counter 运算:", Counter(a=3, b=1) & Counter(a=2, b=4))

    grouped: defaultdict[str, list[int]] = defaultdict(list)
    for name, score in [("A", 90), ("B", 80), ("A", 95)]:
        grouped[name].append(score)
    print("defaultdict 分组:", dict(grouped))

    recent = deque(["任务1", "任务2", "任务3"], maxlen=3)
    recent.append("任务4")  # 超过 maxlen 时，最左侧旧元素自动移除。
    recent.appendleft("紧急任务")  # 此时最右侧元素被移除。
    print("有界 deque:", list(recent))
    recent.rotate(1)
    print("deque 旋转:", list(recent))

    defaults: dict[str, object] = {"theme": "light", "timeout": 30}
    environment: dict[str, object] = {"timeout": 10}
    command_line: dict[str, object] = {"debug": True}
    config: ChainMap[str, object] = ChainMap(command_line, environment, defaults)
    print("ChainMap 查找优先级:", config["debug"], config["timeout"], config["theme"])

    Point = namedtuple("Point", ["x", "y"])
    point = Point(3, 4)
    print("namedtuple:", point, point.x, point._asdict())


def pathlib_demo() -> None:
    title("pathlib")

    path = PurePosixPath("/srv/app/data/report.csv")
    print("纯路径拆分:", path.name, path.stem, path.suffix, path.parent)
    print("替换扩展名:", path.with_suffix(".json"))
    print("拼接路径:", path.parent / "archive" / path.name)

    # TemporaryDirectory 的真实路径随机，因此只打印相对路径和文件内容。
    with TemporaryDirectory() as directory:
        root = Path(directory)
        notes = root / "notes"
        notes.mkdir()
        (root / "README.txt").write_text("首页", encoding="utf-8")
        (notes / "python.txt").write_text("类型与协议", encoding="utf-8")
        (notes / "sql.txt").write_text("查询与索引", encoding="utf-8")

        relative_files = sorted(file.relative_to(root).as_posix() for file in root.rglob("*.txt"))
        print("递归查找文件:", relative_files)

        python_note = notes / "python.txt"
        print("安全读写文本:", python_note.name, python_note.read_text(encoding="utf-8"))
        print("路径状态:", notes.is_dir(), python_note.is_file())


def heapq_demo() -> None:
    title("heapq")

    numbers = [9, 1, 7, 3, 8, 2]
    heapq.heapify(numbers)  # 原地变成最小堆；内部列表不等于完整排序结果。
    smallest_three = [heapq.heappop(numbers) for _ in range(3)]
    print("依次弹出最小值:", smallest_three)

    candidates = [
        {"name": "Ada", "score": 92},
        {"name": "Linus", "score": 88},
        {"name": "Grace", "score": 99},
        {"name": "Guido", "score": 95},
    ]
    top_two = heapq.nlargest(2, candidates, key=itemgetter("score"))
    print("Top-K:", [(item["name"], item["score"]) for item in top_two])

    # 第二项序号用于稳定打破同优先级，避免 Python 比较任务对象本身。
    queue: list[tuple[int, int, str]] = []
    order = count()
    heapq.heappush(queue, (2, next(order), "写文档"))
    heapq.heappush(queue, (1, next(order), "修复线上问题"))
    heapq.heappush(queue, (2, next(order), "补测试"))
    execution_order = [heapq.heappop(queue)[2] for _ in range(len(queue))]
    print("稳定优先队列:", execution_order)


def bisect_demo() -> None:
    title("bisect")

    scores = [60, 70, 80, 80, 90]
    print("80 的左右边界:", bisect_left(scores, 80), bisect_right(scores, 80))

    insort(scores, 85)
    print("保持有序插入:", scores)

    breakpoints = [60, 70, 80, 90]
    grades = ["F", "D", "C", "B", "A"]
    examples = [59, 60, 79, 80, 100]
    classified = {score: grades[bisect(breakpoints, score)] for score in examples}
    print("二分区间映射:", classified)

    print("复杂度提示: 二分查找 O(log n)，列表中间插入仍是 O(n)")


def main() -> None:
    argparse_demo()
    csv_demo()
    logging_demo()
    numeric_tools_demo()
    functools_demo()
    itertools_demo()
    collections_demo()
    pathlib_demo()
    heapq_demo()
    bisect_demo()


if __name__ == "__main__":
    main()
