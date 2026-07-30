# 任务时间线、gather 与 TaskGroup

调用异步函数会得到协程对象。协程对象可以由当前协程直接 `await`；需要让它与当前工作并发运行时，
再把它包装成 Task 交给事件循环调度。Task 运行到 `await` 时可能暂停，等待完成后再继续。
`gather()` 和 `TaskGroup` 都能组织多个 Task，但失败处理方式不同。

<!-- 对应源码：python/python_interview_practice/13_asyncio_concurrency.py、python/backend_interview/async_patterns.py -->

## Task 状态时间线

<ClientOnly>
  <AsyncioTimeline />
</ClientOnly>

图中过程：

1. 调用协程函数，只创建协程对象；
2. `create_task()` 把协程交给事件循环；
3. Task 执行到尚未完成的 await；
4. Task 等待，事件循环运行其他任务；
5. 等待对象完成，Task 再次变为可运行；
6. 协程 return，Task 保存结果并完成。

切换发生在 await 等明确边界，不是任意一行代码之间都可能切走。

## gather 收集结果

下面并发运行两个协程，并按传入顺序收集结果：

```python
results = await asyncio.gather(
    operation_a(),
    operation_b(),
)
```

结果顺序与传入 awaitable 的顺序一致，不与完成顺序绑定。

默认情况下，一个 awaitable 抛出异常时，调用 `gather()` 的位置得到该异常。`gather()` 不是完整的
兄弟任务生命周期管理器；需要一项失败就取消其余项时，TaskGroup 的行为更明确。

## 把异常作为结果收集

下面启用 `return_exceptions=True`，让异常出现在结果列表中：

```python
async def divide(a: int, b: int) -> float:
    await asyncio.sleep(0)
    return a / b


results = await asyncio.gather(
    divide(8, 2),
    divide(8, 0),
    return_exceptions=True,
)

for result in results:
    if isinstance(result, BaseException):
        print(type(result).__name__)
    else:
        print(result)
```

运行结果：

```text
4.0
ZeroDivisionError
```

这种写法适合需要收集每项成功或失败的批处理。调用方必须逐项识别异常，不能把异常对象当作正常数据。

## TaskGroup

Python 3.11 提供 `TaskGroup`。它把一组相关的子任务放在同一个代码块中：退出代码块前会等待这些任务
结束，一个任务失败时会统一取消仍在运行的其他任务并处理异常。这种由明确范围统一管理子任务的做法，
称为结构化并发：

```python
async def main() -> None:
    async with asyncio.TaskGroup() as group:
        first = group.create_task(fetch("A", 0.2))
        second = group.create_task(fetch("B", 0.1))

    print(first.result())
    print(second.result())
```

离开 `async with` 前，组内任务都会结束。一个子任务抛出普通异常时，TaskGroup 会取消仍在运行的兄弟
任务，等待清理，再用 `ExceptionGroup` 传播错误。

## 保存 TaskGroup 结果

仓库的 `map_bounded()` 保存创建顺序：

```python
async def run_all(values, run_one):
    tasks = []

    async with asyncio.TaskGroup() as task_group:
        for value in values:
            tasks.append(
                task_group.create_task(run_one(value))
            )

    return [task.result() for task in tasks]
```

退出 TaskGroup 后任务已经完成，可以调用 `result()`。列表按任务创建顺序读取，因此输出顺序稳定。

## 选择 gather 还是 TaskGroup

| 需求 | 选择 |
| --- | --- |
| 并发等待并按输入顺序收集 | `gather()` |
| 收集每项结果或异常 | `gather(return_exceptions=True)` |
| 一项失败，整组取消并收尾 | `TaskGroup` |
| 需要独立控制单个长期任务 | 保存 `create_task()` 返回值 |

选择的重点是谁负责管理任务，以及一个任务失败后其他任务怎么办，不是哪个写法行数更少。
