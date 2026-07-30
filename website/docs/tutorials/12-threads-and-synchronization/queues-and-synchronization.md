# 队列与线程同步工具

`queue.Queue` 是线程安全队列。生产者负责放入任务，消费者负责取出任务。队列内部已经处理并发
访问，生产者和消费者不必共同修改普通列表。

<!-- 对应源码：python/interview_exercises/concurrency.py -->

## 生产者与消费者

下面创建一个生产者线程和一个消费者线程，通过 Queue 传递任务：

```python
from queue import Queue
from threading import Thread

tasks: Queue[str | None] = Queue(maxsize=2)


def worker() -> None:
    while True:
        task = tasks.get()
        try:
            if task is None:
                return
            print("处理", task)
        finally:
            tasks.task_done()


thread = Thread(target=worker)
thread.start()

for name in ["A", "B", "C"]:
    tasks.put(name)
tasks.put(None)

tasks.join()
thread.join()
```

可能的结果：

```text
处理 A
处理 B
处理 C
```

单个消费者会按队列顺序取任务。多个消费者时，任务完成顺序不保证与入队顺序一致。

## get、task_done 与 join

三组操作必须正确配对：

- 每次成功 `get()` 都对应一次 `task_done()`；
- `Queue.join()` 等待未完成任务计数归零；
- 每个消费者都要收到一个停止哨兵。

把 `task_done()` 放在 `finally` 中，可以覆盖普通任务、异常和哨兵。遗漏它会让 `join()` 一直等待。

有限 `maxsize` 可以形成背压：队列满时，生产者的 `put()` 等待消费者腾出空间。无界队列不会限制
积压。

## 保持输出顺序

并发计算完成顺序不稳定，但可以让任务携带原始下标。仓库中的 `queue_pipeline()` 将结果写入
`index -> value` 字典，最后按下标组装：

```python
from interview_exercises.concurrency import (
    queue_pipeline,
)

print(
    queue_pipeline(
        [5, 2, 8, 1],
        worker_count=2,
    )
)
```

运行结果：

```text
[25, 4, 64, 1]
```

工作线程仍然并发处理，最终列表只是在收集阶段恢复输入顺序。

## 常用同步工具

| 工具 | 作用 | 常见场景 |
| --- | --- | --- |
| `Lock` | 同一时刻允许一个线程进入 | 保护共享状态 |
| `RLock` | 同一线程可以重复获取 | 加锁方法嵌套调用 |
| `Semaphore` | 同时允许固定数量进入 | 限制连接或资源并发 |
| `Event` | 广播一个开关状态 | 停止或初始化通知 |
| `Condition` | 等待共享条件变化 | 缓冲区、状态协调 |
| `Barrier` | 等待固定数量线程到齐 | 分阶段并行 |
| `Queue` | 安全传递数据 | 生产者—消费者 |

`Event` 适合“是否发生”的状态，不携带任务数据；`Condition` 需要和锁配合，在状态改变后通知等待者；
`Semaphore` 只限制同时进入的数量，不保证先等待者一定先获得。

优先使用直接表达需求的工具。任务传递使用 Queue，不要用共享列表、锁和循环 sleep 重新实现队列。
