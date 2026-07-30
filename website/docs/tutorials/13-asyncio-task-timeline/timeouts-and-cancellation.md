# 超时与取消

超时限制一次等待最多持续多久。取消表示调用方要求 Task 停止。Task 通常在下一个 `await` 处收到
取消，并抛出 `CancelledError`。退出前仍要在 `finally` 中释放资源。

<!-- 对应源码：python/python_interview_practice/13_asyncio_concurrency.py -->

## asyncio.timeout

下面为代码块中的等待设置 0.1 秒上限：

```python
async def main() -> None:
    try:
        async with asyncio.timeout(0.1):
            await fetch("A", 1)
    except TimeoutError:
        print("请求超时")
```

运行结果：

```text
A 开始
请求超时
```

`asyncio.timeout()` 取消当前 Task 中的等待，并在上下文外表现为内置 `TimeoutError`。一个超时上下文
可以包围多次 await，让它们共享一个时间上限。

## asyncio.wait_for

下面只限制一个 awaitable 的等待时间：

```python
result = await asyncio.wait_for(
    fetch("A", 0.05),
    timeout=0.5,
)
```

- 多次 await 共享上限：使用 `asyncio.timeout()`；
- 单个 awaitable 设置上限：可以使用 `wait_for()`；
- 多层调用链：维护总 deadline，避免每层重新得到完整 timeout。

超时只说明调用方不再等待，不保证远端副作用没有完成。

## finally 清理资源

仓库示例在超时后仍关闭资源：

```python
events: list[str] = []


async def resource_operation(delay: float) -> str:
    events.append("资源已打开")
    try:
        await asyncio.sleep(delay)
        return "操作成功"
    finally:
        events.append("资源已关闭")
```

正常返回、普通异常和取消都会进入 `finally`。

## 主动取消 Task

下面创建一个长任务，随后调用 `cancel()` 请求停止：

```python
async def worker() -> None:
    try:
        print("开始")
        await asyncio.Event().wait()
    finally:
        print("释放资源")


async def main() -> None:
    task = asyncio.create_task(worker())
    await asyncio.sleep(0)

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("任务已取消")


asyncio.run(main())
```

运行结果：

```text
开始
释放资源
任务已取消
```

`cancel()` 只是发出请求。Task 在下一个可取消等待点收到 `CancelledError`。取消后仍要 await Task，
等待清理和最终状态完成。

## 不要吞掉取消

`CancelledError` 继承自 `BaseException`，普通 `except Exception` 不会捕获它。清理后通常继续传播
取消，否则会破坏外层 timeout、TaskGroup 和应用关闭流程。

```python
async def worker() -> None:
    try:
        await long_operation()
    except asyncio.CancelledError:
        await save_cleanup_state()
        raise
```

CPU 循环没有 await 时不能及时收到取消。已经提交到远端的操作也可能无法撤销，因此取消语义要和具体
资源协议一起设计。
