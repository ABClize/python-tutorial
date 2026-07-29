# 线程、线程池与同步

Python 线程很适合让多个阻塞 I/O 等待重叠，但共享内存也带来竞态。理解线程题的关键不是背 GIL，
而是区分任务类型、任务提交、结果收集和共享状态保护。

<p class="source-note">对应源码：<code>python/python_interview_practice/07_concurrency.py</code>、<code>python/interview_exercises/concurrency.py</code></p>

## 先判断 I/O 密集还是 CPU 密集

| 工作类型 | 主要时间花费 | 常见选择 |
| --- | --- | --- |
| 网络、文件、数据库等待 | 阻塞等待外部资源 | 线程池或 asyncio |
| 纯 Python 大量计算 | 执行 Python 字节码 | 多进程、原生扩展、任务系统 |
| 混合工作 | 两者都有 | 先 profile，再拆分边界 |

CPython 的 GIL 让同一进程中通常只有一个线程执行 Python 字节码，因此线程一般不能加速纯 Python
CPU 密集计算。但线程等待 I/O 时可以释放执行机会，多个请求仍能重叠。

## ThreadPoolExecutor 管理线程生命周期

```python
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch_data(number: int) -> str:
    sleep(0.1)  # 模拟阻塞 I/O
    return f"result-{number}"


with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(fetch_data, number)
        for number in range(1, 6)
    ]
    results = [future.result() for future in as_completed(futures)]

print(sorted(results))
```

```text
['result-1', 'result-2', 'result-3', 'result-4', 'result-5']
```

`submit()` 返回 Future，它代表尚未完成的结果。`as_completed()` 按完成顺序产出 Future；
如果业务要求输入顺序，可以使用 `executor.map()`，或在结果中带上标识后重新排序。

### worker 数量是容量决策

`max_workers` 不是越大越好。线程会占用栈、调度时间、连接和下游并发额度。合理上限至少受以下约束：

- 数据库或 HTTP 连接池大小；
- 下游限流和服务容量；
- 单任务阻塞比例；
- 进程可用内存和文件描述符；
- 请求超时与队列长度。

线程池只有固定 worker，提交速度长期高于完成速度时，内部待办队列会持续增长。生产系统还需要
入口背压、有界队列或拒绝策略。

## `total += 1` 不是不可分割动作

它至少包含读取、计算和写回。两个线程可能读取同一个旧值，再互相覆盖结果：

<ThreadLockDiagram />

GIL 不等于业务操作原子性。即使某个内置操作在当前 CPython 实现中碰巧原子，也不应据此组合出
跨多个步骤的不变量。

## Lock 保护的是不变量

```python
from threading import Lock

lock = Lock()

with lock:
    total += 1
```

锁的范围应覆盖必须整体成立的读改写过程，同时尽量短，不在持锁期间做慢 I/O。多把锁需要统一获取
顺序，否则可能死锁。

如果共享状态可以改成队列传递、不可变消息或单一所有者，往往比添加更多锁更容易证明正确。

## Lock、RLock、Condition 与 Semaphore

不同同步原语表达不同约束：

| 原语 | 表达的关系 |
| --- | --- |
| `Lock` | 同一时刻只有一个线程进入临界区 |
| `RLock` | 同一线程可以重复获得，适合递归调用的内部锁 |
| `Condition` | 在锁保护下等待某个状态条件改变 |
| `Event` | 一次状态通知，多个等待者可观察 |
| `Semaphore` | 同时最多允许 N 个参与者 |
| `Barrier` | 多个线程到齐后一起继续 |

Condition 必须在循环中重新检查谓词，因为线程被唤醒时条件可能已被其他线程改变。Semaphore 控制
并发数量，但不自动保证公平顺序。

## Queue 建立所有权和背压

`queue.Queue` 内部完成线程安全同步，适合生产者把消息交给消费者。共享可变对象仍可能出问题，
因此消息最好是不可变值或明确移交所有权。

有界 `Queue(maxsize=N)` 会在生产过快时阻塞或拒绝，从而把背压传播到入口。消费者必须对每个
`get()` 配对 `task_done()`，等待方才能通过 `join()` 知道任务全部处理完成。

```python
from queue import Queue
from threading import Thread

jobs: Queue[str | None] = Queue(maxsize=10)


def worker() -> None:
    while True:
        job = jobs.get()
        try:
            if job is None:
                return
            print(f"处理 {job}")
        finally:
            jobs.task_done()


thread = Thread(target=worker)
thread.start()
jobs.put("订单-1")
jobs.put(None)  # 哨兵通知消费者退出
jobs.join()
thread.join()
```

哨兵值也属于线程之间的协议：生产者负责发送，消费者负责识别。多个消费者通常需要对应数量的
退出哨兵。

## 死锁与锁顺序

如果线程 A 持有锁 1 等锁 2，线程 B 持有锁 2 等锁 1，就形成循环等待。常见预防方法：

- 所有代码按同一全局顺序获取多把锁；
- 减少同时持有多把锁；
- 在锁外做 I/O 和回调；
- 使用超时帮助发现卡死，但不要把重试当成根治；
- 用队列或单一所有者减少共享状态。

## Future 的异常不会自动消失

工作线程中的异常会存进 Future，在调用 `future.result()` 时重新抛出。如果提交后从不读取结果，
失败可能长期不被观察。

线程池退出上下文时默认等待任务结束。超时取消需要区分：

- 取消尚未开始的 Future；
- 已经在线程中运行的阻塞函数通常不能被 Python 强制安全终止；
- 上层超时不代表底层操作已经停止。

## 线程局部状态与 ContextVar

`threading.local()` 为每个线程保存独立状态，适合遗留同步上下文；异步和混合并发通常更适合
`contextvars.ContextVar`，它能随异步任务上下文传播。两者都不应成为隐藏依赖的借口。

## 多进程解决另一类问题

`ProcessPoolExecutor` 用多个进程绕开单进程 GIL，适合可序列化、计算量足够大的 CPU 任务。代价是
进程启动、pickle 序列化、进程间通信和独立内存。

传给进程池的函数和参数必须可 pickle，Windows 和 spawn 启动方式还要求入口放在
`if __name__ == "__main__":` 下。小任务的通信成本可能超过并行收益。

## 常见误区

### 有 GIL 就不需要 Lock

GIL 保护解释器内部状态，不保护跨多步的业务不变量，也不承诺所有实现和未来版本的细节。

### 线程越多吞吐越高

线程有调度、栈内存和下游压力成本。worker 数量应根据阻塞比例、资源池大小和压测结果设置。

### Future 超时会终止线程函数

调用方停止等待不等于工作停止。底层客户端应提供自己的超时和可取消机制。

## 面试时怎么表述

> 线程适合阻塞 I/O，因为等待期间其他线程可以推进；纯 Python CPU 密集任务通常考虑多进程。
> ThreadPoolExecutor 管理提交和回收，Future 承载结果与异常。共享读改写需要 Lock 或更好的
> 所有权模型，GIL 不能替代业务同步。
