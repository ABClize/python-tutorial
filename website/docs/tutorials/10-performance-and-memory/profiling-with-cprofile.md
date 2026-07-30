# 使用 cProfile 定位热点

当程序包含多层函数调用时，只对入口计时只能知道“整体慢”，无法知道时间花在哪里。`cProfile`
会记录函数调用次数和耗时，帮助找到值得继续检查的调用链。

<p class="source-note">对应源码：<code>python/python_interview_practice/15_performance_and_memory.py</code></p>

## 从命令行分析脚本

在仓库的 `python/` 目录运行：

```bash
uv run python -m cProfile -s cumulative \
  python_interview_practice/15_performance_and_memory.py
```

`-s cumulative` 表示按累计耗时排序。输出中的常见列如下：

| 列 | 含义 |
| --- | --- |
| `ncalls` | 调用次数 |
| `tottime` | 函数自身耗时，不含它调用的其他函数 |
| 第一个 `percall` | `tottime / ncalls` |
| `cumtime` | 函数自身及其所有子调用的累计耗时 |
| 第二个 `percall` | `cumtime` 除以原始调用次数 |
| `filename:lineno(function)` | 函数所在文件、行号和名称 |

同一个函数可能显示成 `200/1` 这样的调用数，通常表示有递归调用：前面是总调用数，后面是原始调用
数。

## 怎样读 profile

可以按下面的顺序查看：

1. 从 `cumtime` 较高的入口和调用链开始；
2. 检查 `ncalls` 是否远高于预期；
3. 比较 `tottime` 与 `cumtime`；
4. 进入热点函数，确认成本来自算法、对象分配还是下游调用；
5. 修改后对相同输入重新运行。

如果一个函数 `tottime` 很低、`cumtime` 很高，说明它自身代码不慢，时间主要花在它调用的函数中。
如果 `tottime` 很高，则函数内部本身就是热点。

单次只需几微秒的函数，调用数百万次后也可能成为主要成本。因此调用次数和单次耗时需要一起看。

## 在代码中使用 Profile

项目源码把一个文本处理工作负载拆成三个函数：

```python
from collections.abc import Iterable


def normalize_words(lines: Iterable[str]) -> list[str]:
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
```

用 `Profile.runcall()` 执行并收集统计：

```python
import cProfile

profiler = cProfile.Profile()
result = profiler.runcall(profiling_workload, 200)

print(result)
print(len(profiler.getstats()) > 0)
```

运行结果：

```text
2400
True
```

`runcall(function, *args, **kwargs)` 返回原函数结果，统计信息保存在 `profiler` 中。
`getstats()` 可以读取结构化数据；人工排查时，格式化后的命令行表格通常更直观。

也可以把统计保存到文件：

```python
profiler.dump_stats("profile.prof")
```

然后用标准库 `pstats` 阅读和筛选：

```python
import pstats

stats = pstats.Stats("profile.prof")
stats.strip_dirs().sort_stats("cumulative").print_stats(20)
```

`print_stats(20)` 只显示前 20 项，避免大量标准库调用淹没关键结果。

## profiler 的开销怎样理解

`cProfile` 是确定性 profiler，会为函数调用记录事件，因此会增加额外开销。profile 输出中的总时间
不能直接当作未插桩程序的生产性能。

它的主要用途是比较“时间相对集中在哪些函数和调用链”。定位热点后，再用更小范围的基准或真实负载
验证修改效果。

## 热点不一定在 Python 计算中

`cProfile` 很适合分析 Python 函数调用，但下面几种情况需要其他证据：

- 等待数据库或 HTTP 请求：结合链路追踪、慢查询和依赖延迟；
- 等待锁或连接池：观察等待时间和并发数量；
- C 扩展内部计算：Python 层可能只显示一个耗时较长的调用；
- 多进程任务：每个进程需要分别采集或使用支持多进程的工具；
- 线上偶发长尾：离线单进程 profile 不一定能复现。

先根据现象选择工具。CPU 调用热点、外部等待和并发排队不是同一种问题。

## 从热点到修改

发现耗时函数后，不要立即做局部语法替换。还应检查：

- 函数为什么被调用这么多次；
- 相同结果是否被重复计算；
- 是否在循环中重复执行 I/O；
- 能否批量处理；
- 数据结构是否使查询随规模变慢；
- 修改会不会改变顺序、异常或副作用。

较好的优化往往是减少不必要调用或更换算法，而不是把热点函数的每一行都改得更复杂。
