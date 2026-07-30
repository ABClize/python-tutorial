# 线程与线程池

进程是一个正在运行的程序。线程是进程中的执行单元。同一进程里的线程共享大部分内存，但每个线程
都有自己的执行位置。

I/O 是 input/output（输入/输出）的缩写，包括网络、文件和数据库操作。I/O 操作经常需要等待外部
结果，等待时可以运行其他线程。CPU 密集任务主要执行计算，增加线程通常不能让纯 Python 计算按核心
数线性加速。

<p class="source-note">对应源码：<code>python/python_interview_practice/07_concurrency.py</code>、<code>python/interview_exercises/concurrency.py</code></p>

## I/O 密集与 CPU 密集

| 类型 | 主要耗时 | 常见选择 |
| --- | --- | --- |
| I/O 密集 | 等待网络、文件、数据库 | 线程或 asyncio |
| CPU 密集 | 执行大量计算 | 算法优化、多进程、原生库 |

用 `sleep()` 模拟三次 I/O：

```python
from time import perf_counter, sleep


def fetch(name: str) -> str:
    sleep(0.2)
    return f"{name} 完成"


started_at = perf_counter()
results = [fetch(name) for name in ["A", "B", "C"]]

print(results)
print(f"{perf_counter() - started_at:.1f} 秒")
```

典型结果：

```text
['A 完成', 'B 完成', 'C 完成']
0.6 秒
```

三次等待依次发生。线程不能缩短单次操作的 0.2 秒，但可以让等待重叠。

## 创建线程

下面创建两个线程，启动后再等待它们结束：

```python
from threading import Thread


def show_message(name: str) -> None:
    print(f"{name} 正在运行")


thread = Thread(
    target=show_message,
    args=("worker-1",),
)
thread.start()
thread.join()

print("主线程结束")
```

运行结果：

```text
worker-1 正在运行
主线程结束
```

- `start()` 启动新线程；
- `join()` 等待线程结束；
- `is_alive()` 检查是否仍在运行。

直接调用 `thread.run()` 只会在当前线程执行普通方法，不会启动新线程。线程调度由操作系统决定，不应
依赖没有同步保证的打印或完成顺序。

## ThreadPoolExecutor

线程池复用固定数量的工作线程：

```python
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

started_at = perf_counter()

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(
        executor.map(fetch, ["A", "B", "C"])
    )

print(results)
print(f"{perf_counter() - started_at:.1f} 秒")
```

典型结果：

```text
['A 完成', 'B 完成', 'C 完成']
0.2 秒
```

`executor.map()` 并发执行任务，但按输入顺序产生结果。仓库中的有序 map：

```python
from interview_exercises.concurrency import (
    parallel_map_ordered,
    square,
)

result = parallel_map_ordered(
    square,
    [3, 1, 4, 2],
    max_workers=2,
)
print(result)
```

运行结果：

```text
[9, 1, 16, 4]
```

结果顺序仍与输入 `[3, 1, 4, 2]` 一致，不受各线程实际完成顺序影响。

## submit 与 Future

`submit()` 提交一个调用并立即返回 `Future`：

```python
with ThreadPoolExecutor(max_workers=2) as executor:
    future = executor.submit(fetch, "A")
    result = future.result(timeout=1)
    print(result)
```

运行结果：

```text
A 完成
```

Future 表示将来可能得到的结果：

- `result()` 返回结果，或重新抛出工作函数异常；
- `result(timeout=...)` 等待超时会抛出 `TimeoutError`；
- `done()` 检查任务是否完成；
- `exception()` 读取任务异常；
- `cancel()` 只能取消尚未开始的任务。

Future 的等待超时不会终止已经运行的线程函数。长任务需要由函数自己检查停止信号。

## 按完成顺序处理

下面使用 `as_completed()`，哪个任务先完成就先处理哪个结果：

```python
from concurrent.futures import as_completed
from time import sleep


def fetch_with_delay(name: str, delay: float) -> str:
    sleep(delay)
    return f"{name} 完成"


jobs = [("A", 0.03), ("B", 0.02), ("C", 0.01)]

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(fetch_with_delay, name, delay)
        for name, delay in jobs
    ]
    for future in as_completed(futures):
        print(future.result())
```

典型结果：

```text
C 完成
B 完成
A 完成
```

`map()` 适合保持输入顺序；`submit()` 配合 `as_completed()` 适合结果完成后立即处理。

## 线程池关闭与容量

退出 `with ThreadPoolExecutor(...)` 时会停止接收新任务，并默认等待已提交任务结束。工作函数永久阻塞
时，程序也会停在出口。

`max_workers` 不是越大越好。线程过多会增加栈内存、调度开销、锁竞争和下游连接压力。容量要结合
连接池、下游限额、单任务延迟和机器资源设置。
