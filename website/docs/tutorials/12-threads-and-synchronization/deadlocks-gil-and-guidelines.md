# 死锁、GIL 与线程使用原则

死锁是多个线程互相等待资源，导致所有线程都无法继续。GIL 是 CPython 的全局解释器锁，它限制同一
时刻执行 Python 字节码的线程数量。GIL 不会自动保护业务数据，修改共享状态时仍可能需要锁。

<p class="source-note">对应源码：<code>python/interview_exercises/concurrency.py</code>、<code>python/python_interview_practice/07_concurrency.py</code></p>

## 死锁怎样发生

下面的时间线展示两把锁以相反顺序获取时的等待关系：

```text
线程 A：持有 account_a_lock，等待 account_b_lock
线程 B：持有 account_b_lock，等待 account_a_lock
```

双方都在等待对方释放资源，任何一方都无法继续。

获取多把锁时，应规定统一顺序。仓库中的转账函数为账户记录创建顺序：

```python
first, second = sorted(
    (source, target),
    key=lambda account: account._lock_order,
)

with first._lock, second._lock:
    if source._balance_cents < amount_cents:
        raise ValueError("余额不足")
    source._balance_cents -= amount_cents
    target._balance_cents += amount_cents
```

无论 A 转给 B 还是 B 转给 A，都按相同顺序获取两把锁，因此不会形成 ABBA 等待。

预防死锁：

- 所有代码按相同顺序获取多把锁；
- 缩短持锁时间；
- 不在持锁时调用未知回调或外部 I/O；
- 用队列传递所有权，减少共享状态；
- 对可超时锁获取记录线程和资源信息。

超时能让程序避免永久等待，但不能替代一致的锁顺序。

## GIL 保护什么

CPython 的全局解释器锁通常只允许一个线程同时执行 Python 字节码。它保护解释器内部结构，但不保证：

- 一组读取、检查和写回不可分割；
- I/O 前后状态不会被其他线程修改；
- 原生扩展执行期间一定持有 GIL；
- 业务不变量自动成立。

因此共享状态仍要用 Lock 或其他同步协议。

## CPU 密集任务

大量纯 Python 计算通常不会因线程数增加而线性加速，可以依次考虑：

1. 改进算法和数据结构；
2. 使用 NumPy 等在原生代码中计算的库；
3. 使用 `ProcessPoolExecutor` 或 `multiprocessing`；
4. 把热点实现为原生扩展。

多进程有启动、通信和对象序列化成本。提交给进程池的可调用对象、参数和返回值通常需要能够 pickle，
很小且频繁的任务可能得不偿失。

## 线程任务的错误和关闭

线程函数抛出的异常不会自动出现在提交者当前调用栈中。使用线程池时，应读取每个 Future：

```python
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(process, item)
        for item in items
    ]
    for future in futures:
        future.result()
```

`result()` 会重新抛出异常。若完全丢弃 Future，失败可能只留下不明显的日志或被忽略。

线程和线程池都要有明确关闭条件：

- 普通线程由谁 `join()`；
- 队列消费者怎样收到停止哨兵；
- 阻塞 I/O 是否有 timeout；
- 长任务怎样响应停止信号；
- 进程退出前哪些工作必须完成。

守护线程会在只剩守护线程时随进程退出，不适合承载必须落盘或必须清理的数据任务。

## 线程使用注意事项

- 不依赖没有同步保证的执行顺序；
- 用锁保护完整不变量，不只保护某行赋值；
- 锁内避免慢 I/O；
- Future 超时不会停止正在运行的函数；
- 每个 Future 的结果或异常都要处理；
- Queue 容量和线程池容量都要与下游资源协调；
- 纯 Python CPU 密集任务优先考虑算法或多进程。
