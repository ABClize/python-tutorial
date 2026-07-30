# 协程、Task 与事件循环

asyncio 中，协程描述一段可以暂停的工作，Task 把协程交给事件循环调度，事件循环在可运行任务和等待
结果之间切换。

<p class="source-note">对应源码：<code>python/python_interview_practice/13_asyncio_concurrency.py</code></p>

## 三个基本概念

| 名称 | 含义 |
| --- | --- |
| 协程对象 | 调用 `async def` 函数得到的可等待对象 |
| `Task` | 已经交给事件循环调度的协程 |
| 事件循环 | 记录可运行和等待中的任务，并负责恢复 |

定义协程函数：

```python
async def fetch() -> str:
    return "完成"
```

调用函数不会立即执行函数体：

```python
coroutine = fetch()
print(type(coroutine).__name__)
coroutine.close()
```

运行结果：

```text
coroutine
```

协程对象必须被 `await`，或者包装成 Task 后等待。完全不处理通常会得到
`RuntimeWarning: coroutine was never awaited`。

## asyncio.run

```python
import asyncio


async def fetch(name: str, delay: float) -> str:
    print(name, "开始")
    await asyncio.sleep(delay)
    print(name, "完成")
    return f"{name} 的结果"


async def main() -> None:
    result = await fetch("A", 0.1)
    print(result)


asyncio.run(main())
```

运行结果：

```text
A 开始
A 完成
A 的结果
```

执行过程：

1. `asyncio.run(main())` 创建事件循环；
2. 事件循环运行 `main()`；
3. `main()` 等待 `fetch()`；
4. `fetch()` 在 `asyncio.sleep()` 处暂停；
5. 定时等待完成后恢复；
6. 入口协程结束，事件循环完成收尾并关闭。

`asyncio.run()` 通常只在程序入口调用一次。已经运行事件循环的 Jupyter 单元格中，使用
`await main()`，不要嵌套调用 `asyncio.run()`。

## 创建 Task

```python
async def main() -> None:
    task = asyncio.create_task(
        fetch("A", 0.1),
        name="request:A",
    )

    print(task.get_name())
    print(task.done())

    result = await task
    print(result)
    print(task.done())
```

`create_task()` 安排协程运行，当前协程继续向下执行。子任务通常要等当前协程到达下一个 await，事件
循环才有机会切换过去。

Task 的常用接口：

- `get_name()`：读取诊断名称；
- `done()`：是否已经结束；
- `result()`：成功结束后读取结果；
- `exception()`：读取异常；
- `cancel()`：请求取消；
- `cancelled()`：是否以取消结束。

普通父子调用直接 `await coroutine()` 更简单。只有工作需要与当前协程重叠时才创建 Task。

## Task 的所有权

创建 Task 后要保存引用，并明确由谁：

- 等待结果；
- 处理异常；
- 应用关闭时取消；
- 取消后继续 await，等待清理结束。

“创建后不管”的后台 Task 会失去可靠的错误和关闭入口。长期后台任务通常应由应用生命周期对象统一
保存和管理。
