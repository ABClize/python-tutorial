# Python asyncio：协程、任务与事件循环

`asyncio` 是 Python 标准库中的异步 I/O 框架。事件循环会在多个协程之间切换，让一个线程同时等待
许多网络、数据库或消息队列操作。程序还要显式处理任务、异常、超时、取消和并发数量。

<p class="source-note">对应源码：<code>python/python_interview_practice/13_asyncio_concurrency.py</code>、<code>python/backend_interview/async_patterns.py</code></p>

## 本章内容

- [协程、Task 与事件循环](./13-asyncio-task-timeline/coroutines-tasks-and-loop)：理解 `async def`
  调用后得到什么，事件循环怎样运行入口协程，以及 Task 负责什么。
- [await 与并发等待](./13-asyncio-task-timeline/await-and-concurrency)：区分串行 await 和并发等待，
  避免阻塞事件循环。
- [任务时间线、gather 与 TaskGroup](./13-asyncio-task-timeline/task-timeline-gather-and-taskgroup)：
  观察任务暂停与恢复，并比较两种任务组合方式。
- [超时与取消](./13-asyncio-task-timeline/timeouts-and-cancellation)：用 timeout 和 wait_for 设置
  上限，正确传播取消并执行清理。
- [并发限制、队列与异步资源](./13-asyncio-task-timeline/limits-queues-and-async-resources)：使用
  Semaphore、Queue、异步生成器和异步上下文管理器。
