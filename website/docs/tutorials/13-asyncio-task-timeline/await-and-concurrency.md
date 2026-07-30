# await 与并发等待

`await` 等待一个 awaitable 的结果。等待对象尚未完成时，当前协程暂停并把控制权还给事件循环，其他
可运行 Task 才能继续。

<p class="source-note">对应源码：<code>python/python_interview_practice/13_asyncio_concurrency.py</code></p>

## await 是切换边界

异步函数中仍然可以写阻塞代码：

```python
import time


async def blocked() -> None:
    time.sleep(1)
```

`time.sleep()` 不会把控制权交给事件循环，因此整个线程中的所有 Task 都要等待。应使用异步版本：

```python
import asyncio


async def non_blocking() -> None:
    await asyncio.sleep(1)
```

无法替换的同步 I/O 可以放入工作线程：

```python
result = await asyncio.to_thread(
    blocking_function,
    argument,
)
```

`to_thread()` 主要用于阻塞 I/O，不会让纯 Python CPU 计算自动使用多个核心。

## 顺序 await

```python
async def serial() -> list[str]:
    first = await fetch("A", 0.2)
    second = await fetch("B", 0.1)
    return [first, second]
```

第二个调用要等第一个返回后才开始，总时间约为 0.3 秒。

## 并发等待

```python
async def concurrent() -> list[str]:
    first, second = await asyncio.gather(
        fetch("A", 0.2),
        fetch("B", 0.1),
    )
    return [first, second]


asyncio.run(concurrent())
```

典型输出：

```text
A 开始
B 开始
B 完成
A 完成
```

总时间接近较慢任务的 0.2 秒。B 先完成，但 `gather()` 的结果仍按传入顺序排列，`first` 对应 A。

仓库示例记录了三项任务：

```text
实际完成顺序: ['C', 'B', 'A']
gather 返回顺序: ['A:完成', 'B:完成', 'C:完成']
```

## 异步不等于并行计算

asyncio 的并发来自等待时让出控制权。默认事件循环仍运行在一个线程中：

```text
Task A 执行 → 等待 I/O
                 ↓
Task B 执行 → 等待 I/O
                 ↓
Task A 的 I/O 完成 → 恢复
```

长时间 CPU 循环没有 await，事件循环就无法切换。此类工作要优化算法、放入进程池或使用原生实现。

## 何时创建 Task

以下写法仍然串行：

```python
first = await operation_a()
second = await operation_b()
```

两个操作互不依赖时，可以用 `gather()`、`TaskGroup`，或先创建 Task：

```python
first_task = asyncio.create_task(operation_a())
second_task = asyncio.create_task(operation_b())

first = await first_task
second = await second_task
```

后一种方式需要自己负责兄弟任务失败、取消和异常处理。共同组成一个用例的任务通常使用 TaskGroup 更
清楚。
