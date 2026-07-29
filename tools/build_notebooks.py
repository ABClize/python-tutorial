"""使用 nbformat 构建可重现的中文交互式教程 Notebook。

修改教程内容后运行本脚本重新生成 Notebook。执行验证应把结果写入独立目录，
不要用执行输出覆盖 ``notebooks/`` 中的生成源产物。
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"


def markdown(source: str):
    """创建一个去除公共缩进的 Markdown 单元格。"""
    return new_markdown_cell(dedent(source).strip())


def code(source: str):
    """创建一个去除公共缩进的代码单元格。"""
    return new_code_cell(dedent(source).strip())


def notebook(cells):
    """创建使用项目 Python 内核的空输出 Notebook。"""
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


def matplotlib_setup():
    """创建 Matplotlib 与 ipywidgets 的公共初始化单元格。"""
    return code(
        """
        %matplotlib inline

        import ipywidgets as widgets
        import matplotlib.pyplot as plt
        from IPython.display import clear_output, display

        plt.rcParams["axes.unicode_minus"] = False
        """
    )


def plotly_setup():
    """创建 Plotly 与 ipywidgets 的公共初始化单元格。"""
    return code(
        """
        import ipywidgets as widgets
        import plotly.graph_objects as go
        from IPython.display import display

        PLOTLY_CONFIG = {
            "displayModeBar": False,
            "displaylogo": False,
            "responsive": True,
        }
        """
    )


def mutability_notebook():
    return notebook(
        [
            markdown(
                """
                # Python 可变对象、引用与拷贝

                ## 学习目标

                通过可操作的对象关系图理解赋值、浅拷贝、深拷贝、函数参数和可变默认参数。
                重点不是记住几个 API，而是建立一个心智模型：

                > Python 变量保存的是对象引用；复制操作决定新旧容器在哪一层继续共享对象。
                """
            ),
            markdown(
                """
                ## 准备

                本教程使用 `ipywidgets` 改变复制方式，使用 Matplotlib 画出变量、外层列表和
                内层列表之间的引用关系。图中的 A、B、C 只是为了区分对象，不代表变量名。
                """
            ),
            matplotlib_setup(),
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
                ## 先建立心智模型

                ### 1. 赋值不是复制

                `alias = original` 只增加一个变量名。两个名字仍指向同一个外层列表，因此修改任何一方
                都会被另一方观察到。
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
                ### 2. 直接操作引用关系图

                在下拉框中切换三种方式：

                - **直接赋值**：外层和内层都共享；
                - **浅拷贝**：外层分开，内层继续共享；
                - **深拷贝**：本例中的外层和内层都分开。

                先看箭头，再看图下方的两个 `is` 结论。真正决定修改是否互相影响的是“被修改的那一层
                是否仍然指向同一个对象”。
                """
            ),
            code(
                """
                def unique_objects(values):
                    unique = []
                    for value in values:
                        if not any(value is existing for existing in unique):
                            unique.append(value)
                    return unique


                def vertical_positions(count):
                    return [(count - index) / (count + 1) for index in range(count)]


                def draw_box(axis, x, y, text, color):
                    axis.text(
                        x,
                        y,
                        text,
                        ha="center",
                        va="center",
                        fontsize=10,
                        bbox={
                            "boxstyle": "round,pad=0.45",
                            "facecolor": color,
                            "edgecolor": "#334155",
                        },
                    )


                def draw_arrow(axis, start, end):
                    axis.annotate(
                        "",
                        xy=end,
                        xytext=start,
                        arrowprops={"arrowstyle": "->", "color": "#475569", "lw": 1.8},
                    )


                def build_copy_example(copy_mode):
                    source = [[1, 2], [3, 4]]
                    if copy_mode == "直接赋值":
                        copied = source
                    elif copy_mode == "浅拷贝":
                        copied = source.copy()
                    else:
                        copied = copy.deepcopy(source)
                    return source, copied


                def draw_copy_graph(copy_mode):
                    source, copied = build_copy_example(copy_mode)
                    mode_labels = {
                        "直接赋值": "assignment",
                        "浅拷贝": "shallow copy",
                        "深拷贝": "deep copy",
                    }
                    outer_objects = unique_objects([source, copied])
                    inner_objects = unique_objects(
                        [item for outer in outer_objects for item in outer]
                    )

                    outer_y = {
                        id(value): y
                        for value, y in zip(
                            outer_objects,
                            vertical_positions(len(outer_objects)),
                            strict=True,
                        )
                    }
                    inner_y = {
                        id(value): y
                        for value, y in zip(
                            inner_objects,
                            vertical_positions(len(inner_objects)),
                            strict=True,
                        )
                    }

                    figure, axis = plt.subplots(figsize=(10, 5))
                    axis.set_xlim(0, 1)
                    axis.set_ylim(0, 1)
                    axis.axis("off")
                    axis.set_title(
                        f"Object references after {mode_labels[copy_mode]}",
                        fontsize=15,
                        pad=16,
                    )

                    variable_positions = {"original": 0.7, "copied": 0.3}
                    variable_targets = {"original": source, "copied": copied}
                    for name, y in variable_positions.items():
                        draw_box(axis, 0.1, y, name, "#e2e8f0")
                        target_y = outer_y[id(variable_targets[name])]
                        draw_arrow(axis, (0.18, y), (0.32, target_y))

                    for index, value in enumerate(outer_objects):
                        y = outer_y[id(value)]
                        label = chr(ord("A") + index)
                        draw_box(axis, 0.42, y, f"outer list {label}\\n{value!r}", "#bfdbfe")
                        for inner in value:
                            draw_arrow(axis, (0.52, y), (0.68, inner_y[id(inner)]))

                    for index, value in enumerate(inner_objects):
                        y = inner_y[id(value)]
                        label = chr(ord("A") + index)
                        draw_box(axis, 0.8, y, f"nested list {label}\\n{value!r}", "#fed7aa")

                    axis.text(0.1, 0.96, "names", ha="center", weight="bold")
                    axis.text(0.42, 0.96, "outer objects", ha="center", weight="bold")
                    axis.text(0.8, 0.96, "nested objects", ha="center", weight="bold")
                    axis.text(
                        0.5,
                        0.02,
                        (
                            f"same outer object: {source is copied}    "
                            f"same first nested object: {source[0] is copied[0]}"
                        ),
                        ha="center",
                        fontsize=11,
                        color="#0f172a",
                    )
                    plt.show()
                    plt.close(figure)


                copy_mode = widgets.Dropdown(
                    options=["直接赋值", "浅拷贝", "深拷贝"],
                    value="浅拷贝",
                    description="复制方式：",
                    style={"description_width": "initial"},
                )
                copy_output = widgets.Output()


                def render_copy_mode(_change=None):
                    with copy_output:
                        clear_output(wait=True)
                        draw_copy_graph(copy_mode.value)


                copy_mode.observe(render_copy_mode, names="value")
                display(widgets.VBox([copy_mode, copy_output]))
                render_copy_mode()
                """
            ),
            markdown(
                """
                ### 3. 用修改实验验证图中的箭头

                下面先修改内层列表，再比较三种方式。不要笼统地说“浅拷贝会联动”，应准确地说：
                **浅拷贝得到的新外层列表仍然引用原来的内层列表。**
                """
            ),
            code(
                """
                for mode in ["直接赋值", "浅拷贝", "深拷贝"]:
                    source, copied = build_copy_example(mode)
                    source[0].append(99)
                    print(f"{mode:<4} source={source!r} copied={copied!r}")
                """
            ),
            markdown(
                """
                ## 函数参数仍然遵循同一模型

                重新绑定局部变量不会改变调用者的名字，但修改可变对象本身会被调用者观察到。
                这不是另一套特殊规则：形参只是函数调用期间新创建的局部变量名。
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
                ## 可变默认参数为什么会复用

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
            markdown(
                """
                ## 常见误解

                - “赋值会复制对象”：赋值只让另一个名字指向对象。
                - “浅拷贝一定不安全”：风险取决于是否修改了继续共享的嵌套对象。
                - “深拷贝永远正确”：深拷贝成本更高，而且外部资源、单例和自定义复制语义需要单独考虑。
                - “Python 是传值还是传引用”：更准确的说法是把对象引用绑定给新的局部形参。

                ## 面试时可以这样解释

                > Python 变量是名字到对象的绑定。浅拷贝创建新的外层容器，但元素引用被原样复制；
                > 深拷贝会递归复制可复制的子对象。因此判断修改是否互相影响时，
                > 要看被修改层级是否共享。

                ## 继续探索

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

                ## 学习目标

                理解函数是一等对象、闭包如何保存状态、装饰器如何包装函数，以及生成器为什么能暂停和
                恢复。本教程最后会直接读取生成器保存的 frame，让“惰性计算”从一句定义变成可观察状态。
                """
            ),
            markdown(
                """
                ## 准备

                使用 `ipywidgets` 选择推进次数，使用 Matplotlib 展示生成器暂停时保存的局部变量。
                """
            ),
            matplotlib_setup(),
            code(
                """
                from functools import wraps
                from itertools import islice
                """
            ),
            markdown(
                """
                ## 函数对象与闭包

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
            markdown(
                """
                ### 2. 闭包保存外层状态

                `counter_factory` 返回后，它的局部调用帧虽然结束了，但 `increment` 仍引用其中的
                `count` 闭包单元。`nonlocal` 修改的是这份被闭包保留的状态。
                """
            ),
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
            markdown(
                """
                ### 3. 装饰器增加横切功能

                `@trace` 的核心等价式是 `multiply = trace(multiply)`。调用者最终拿到的是
                `wrapper`，`wrapper` 再通过闭包找到原函数。
                """
            ),
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
                ## 生成器为什么可以暂停

                调用生成器函数时只创建生成器对象，函数体尚未执行。每次 `next()` 会从上次暂停位置
                继续，运行到下一个 `yield` 后再次暂停。暂停期间，指令位置和局部变量都保存在
                `generator.gi_frame` 中。

                先运行普通示例，再用下面的滑块观察每一次暂停状态。
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
            code(
                """
                def capture_fibonacci_states(step_count=8):
                    sequence = fibonacci()
                    states = []
                    produced = []

                    for step in range(1, step_count + 1):
                        value = next(sequence)
                        produced.append(value)
                        frame_locals = dict(sequence.gi_frame.f_locals)
                        states.append(
                            {
                                "step": step,
                                "yielded": value,
                                "produced": produced.copy(),
                                "left": frame_locals["left"],
                                "right": frame_locals["right"],
                                "line": sequence.gi_frame.f_lineno,
                            }
                        )
                    return states


                fibonacci_states = capture_fibonacci_states()


                def draw_generator_state(step):
                    state = fibonacci_states[step - 1]
                    figure, axis = plt.subplots(figsize=(10, 4.6))
                    axis.set_xlim(0, 10)
                    axis.set_ylim(0, 4)
                    axis.axis("off")
                    axis.set_title(
                        f"After next() #{step}: suspended at yield",
                        fontsize=15,
                    )

                    boxes = [
                        (1.7, 2.2, "values produced", repr(state["produced"]), "#dbeafe"),
                        (
                            5.0,
                            2.2,
                            "saved local state",
                            f"left = {state['left']}\\nright = {state['right']}",
                            "#fef3c7",
                        ),
                        (
                            8.3,
                            2.2,
                            "next next() call",
                            "resume after yield\\nupdate left, right",
                            "#dcfce7",
                        ),
                    ]
                    for x, y, title, detail, color in boxes:
                        axis.text(
                            x,
                            y,
                            f"{title}\\n\\n{detail}",
                            ha="center",
                            va="center",
                            fontsize=11,
                            bbox={
                                "boxstyle": "round,pad=0.6",
                                "facecolor": color,
                                "edgecolor": "#334155",
                            },
                        )

                    for start, end in [((2.8, 2.2), (3.8, 2.2)), ((6.2, 2.2), (7.1, 2.2))]:
                        axis.annotate(
                            "",
                            xy=end,
                            xytext=start,
                            arrowprops={"arrowstyle": "->", "lw": 2, "color": "#475569"},
                        )

                    axis.text(
                        5,
                        0.45,
                        (
                            f"yielded {state['yielded']} at source line {state['line']}; "
                            "local variables remain alive while suspended."
                        ),
                        ha="center",
                        fontsize=10,
                        color="#0f172a",
                    )
                    plt.show()
                    plt.close(figure)


                generator_step = widgets.IntSlider(
                    value=1,
                    min=1,
                    max=len(fibonacci_states),
                    step=1,
                    description="next 次数：",
                    continuous_update=False,
                    style={"description_width": "initial"},
                )
                generator_output = widgets.Output()


                def render_generator_step(_change=None):
                    with generator_output:
                        clear_output(wait=True)
                        draw_generator_state(generator_step.value)


                generator_step.observe(render_generator_step, names="value")
                display(widgets.VBox([generator_step, generator_output]))
                render_generator_step()
                """
            ),
            markdown(
                """
                滑块前进时，`produced` 逐渐增长；图中央的 `left` 和 `right` 是生成器暂停时真实保存的
                局部变量。下一次 `next()` 不会从函数开头重跑，而是从当前 `yield` 之后恢复。

                ## 自定义迭代器协议
                """
            ),
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
            markdown(
                """
                ## 常见误解

                - “生成器保存所有结果”：它主要保存执行状态，已经交给调用者的值不会自动组成列表。
                - “调用生成器函数会立刻执行”：调用只返回生成器对象，第一次 `next()` 才进入函数体。
                - “可迭代对象就是迭代器”：可迭代对象能产生迭代器；迭代器还要保存当前位置并实现
                  `__next__`。
                - “装饰器只是语法”：装饰器会在函数定义阶段替换绑定到函数名上的对象。

                ## 面试时可以这样解释

                > 生成器是保存了指令位置和局部变量的可恢复执行帧。`next()` 从上次 `yield` 后恢复，
                > 运行到下一个 `yield` 再暂停，因此可以按需生成数据，而不必提前构造完整结果。

                ## 继续探索

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

                ## 学习目标

                以“两数之和”为例，对比暴力搜索与哈希表方案，并用参数化样例验证边界条件。
                """
            ),
            markdown(
                """
                ## 准备

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
                ## 分步理解

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
            markdown("## 验证理解"),
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
                ## 继续探索

                1. 给函数增加类型标注。
                2. 解释为什么哈希表查询是“平均” $O(1)$。
                3. 尝试返回所有满足条件的下标对。
                4. 用 pytest 的 `@pytest.mark.parametrize` 改写样例表。
                """
            ),
        ]
    )


def asyncio_timeline_notebook():
    return notebook(
        [
            markdown(
                """
                # asyncio 事件循环与任务时间线

                ## 学习目标

                通过可调时间线理解 coroutine、Task、事件循环和 `await` 的关系，并区分：

                - Task 的创建顺序；
                - I/O 等待完成顺序；
                - `asyncio.gather` 的结果顺序；
                - 取消请求与 `finally` 清理。

                核心心智模型是：`await` 不会让等待本身变快，它让当前 Task 暂停，把事件循环交给其他
                可以继续运行的 Task。
                """
            ),
            markdown(
                """
                ## 准备

                Plotly 负责绘制可悬浮查看的等待时间线，`ipywidgets` 负责调整三个任务的模拟 I/O
                延迟。时间线中的彩色条表示 Task 正在等待外部结果，不表示 CPU 一直在执行该任务。
                """
            ),
            plotly_setup(),
            markdown(
                """
                ## 操作任务时间线

                调整任一延迟后观察两件事：

                1. 三个 Task 都从时间零附近开始等待，说明它们已经并发启动；
                2. 完成顺序由延迟决定，但 `gather` 仍按传入顺序返回结果。
                """
            ),
            code(
                """
                TASK_COLORS = {
                    "任务 A": "#2563eb",
                    "任务 B": "#f97316",
                    "任务 C": "#16a34a",
                }


                def draw_task_timeline(delay_a, delay_b, delay_c):
                    names = ["任务 A", "任务 B", "任务 C"]
                    delays = [delay_a, delay_b, delay_c]
                    indexed_tasks = list(enumerate(zip(names, delays, strict=True)))
                    completed = sorted(indexed_tasks, key=lambda item: (item[1][1], item[0]))
                    completion_order = [name for _, (name, _) in completed]

                    figure = go.Figure()
                    figure.add_trace(
                        go.Bar(
                            x=delays,
                            y=names,
                            orientation="h",
                            marker_color=[TASK_COLORS[name] for name in names],
                            text=[f"等待 {delay:.1f} 秒" for delay in delays],
                            textposition="inside",
                            hovertemplate="%{y}<br>等待：%{x:.1f} 秒<extra></extra>",
                            name="等待外部 I/O",
                        )
                    )
                    figure.add_trace(
                        go.Scatter(
                            x=delays,
                            y=names,
                            mode="markers+text",
                            marker={"size": 14, "color": "#0f172a", "symbol": "diamond"},
                            text=["恢复并完成"] * len(names),
                            textposition="top center",
                            hovertemplate="%{y}<br>在 %{x:.1f} 秒恢复<extra></extra>",
                            name="恢复点",
                        )
                    )
                    figure.update_layout(
                        title="三个 Task 的模拟 I/O 等待与恢复",
                        xaxis_title="相对时间（秒）",
                        yaxis_title="",
                        xaxis={"range": [0, max(delays) + 0.25]},
                        yaxis={"autorange": "reversed"},
                        height=390,
                        margin={"l": 80, "r": 30, "t": 70, "b": 55},
                        showlegend=True,
                    )
                    figure.show(config=PLOTLY_CONFIG)
                    print("实际完成顺序：", " → ".join(completion_order))
                    print("gather 返回顺序：任务 A → 任务 B → 任务 C")


                delay_a = widgets.FloatSlider(
                    value=0.6,
                    min=0.1,
                    max=1.0,
                    step=0.1,
                    description="任务 A：",
                    continuous_update=False,
                )
                delay_b = widgets.FloatSlider(
                    value=0.4,
                    min=0.1,
                    max=1.0,
                    step=0.1,
                    description="任务 B：",
                    continuous_update=False,
                )
                delay_c = widgets.FloatSlider(
                    value=0.2,
                    min=0.1,
                    max=1.0,
                    step=0.1,
                    description="任务 C：",
                    continuous_update=False,
                )
                timeline_output = widgets.interactive_output(
                    draw_task_timeline,
                    {
                        "delay_a": delay_a,
                        "delay_b": delay_b,
                        "delay_c": delay_c,
                    },
                )
                display(
                    widgets.HBox(
                        [widgets.VBox([delay_a, delay_b, delay_c]), timeline_output]
                    )
                )
                """
            ),
            markdown(
                """
                ## 运行真实协程

                上面的图使用确定的延迟构造概念时间线。下面让事件循环真正调度三个协程，并记录它们
                的完成顺序。耗时会受机器调度影响，所以只观察相对顺序，不把具体毫秒数当成固定答案。
                """
            ),
            code(
                """
                import asyncio
                import time


                async def simulated_request(name, delay, completion_log):
                    await asyncio.sleep(delay)
                    completion_log.append(name)
                    return f"{name}:结果"


                async def run_concurrent_requests():
                    completion_log = []
                    started_at = time.perf_counter()
                    results = await asyncio.gather(
                        simulated_request("A", 0.06, completion_log),
                        simulated_request("B", 0.04, completion_log),
                        simulated_request("C", 0.02, completion_log),
                    )
                    elapsed = time.perf_counter() - started_at
                    return completion_log, results, elapsed


                completion_log, results, elapsed = await run_concurrent_requests()
                print("完成顺序:", completion_log)
                print("gather 结果:", results)
                print(f"总耗时约 {elapsed:.3f} 秒，而不是三个延迟简单相加")
                """
            ),
            markdown(
                """
                `C` 最先完成，是因为它等待时间最短；`gather` 的结果仍对应传入的 A、B、C。
                这两个顺序服务不同目的：完成顺序描述调度事实，结果顺序让调用者容易对应输入。

                ## 取消不是强行终止

                `task.cancel()` 会安排在合适的暂停点向 Task 抛出 `CancelledError`。协程仍有机会执行
                `finally`，释放锁、连接或临时资源，然后取消继续向上传播。
                """
            ),
            code(
                """
                async def cancellable_worker(events):
                    events.append("开始")
                    try:
                        await asyncio.sleep(10)
                    finally:
                        events.append("finally 清理")


                async def cancellation_demo():
                    events = []
                    task = asyncio.create_task(cancellable_worker(events))
                    await asyncio.sleep(0)
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        events.append("调用者收到取消")
                    return events


                print("取消过程:", await cancellation_demo())
                """
            ),
            markdown(
                """
                ## 常见误解

                - “asyncio 会让 CPU 计算并行”：事件循环主要提升大量 I/O 等待场景的利用率。
                - “创建 coroutine 就开始运行”：coroutine 需要被 `await` 或包装成 Task 才会推进。
                - “`gather` 的结果顺序就是完成顺序”：结果顺序默认与输入顺序一致。
                - “取消可以忽略”：吞掉 `CancelledError` 会破坏超时、TaskGroup 和服务关闭流程。

                ## 面试时可以这样解释

                > Task 是被事件循环调度的 coroutine。协程遇到尚未完成的 `await` 时保存状态并让出
                > 控制权；等待完成后，事件循环再从暂停点恢复它。取消也是通过异常在暂停点协作传播，
                > 因此清理逻辑应放在 `finally` 中。

                ## 继续探索

                1. 把一个任务中的 `asyncio.sleep` 换成 `time.sleep`，观察其他任务为什么一起变慢。
                2. 用 `TaskGroup` 重写示例，观察一个子任务失败时兄弟任务如何被取消。
                3. 给时间线增加“创建、等待、恢复、完成”四种事件，而不是只画等待区间。
                """
            ),
        ]
    )


NOTEBOOKS = {
    "01_mutability_and_copy.ipynb": mutability_notebook,
    "02_functions_and_generators.ipynb": functions_notebook,
    "03_algorithms_and_complexity.ipynb": algorithms_notebook,
    "04_asyncio_task_timeline.ipynb": asyncio_timeline_notebook,
}


def main() -> None:
    NOTEBOOK_DIR.mkdir(exist_ok=True)
    for filename, factory in NOTEBOOKS.items():
        path = NOTEBOOK_DIR / filename
        nbformat.write(factory(), path)
        print(f"created {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
