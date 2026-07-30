# Python 线程、线程池与同步

线程是进程中的执行单元。同一进程里的线程共享内存，可以在一个线程等待网络或文件时运行其他线程。
共享内存也会带来竞争条件，因此还要学习锁、线程安全队列和死锁。

<p class="source-note">对应源码：<code>python/python_interview_practice/07_concurrency.py</code>、<code>python/interview_exercises/concurrency.py</code></p>

## 本章内容

- [线程与线程池](./12-threads-and-synchronization/thread-basics-and-pools)：区分 I/O 和 CPU 任务，
  创建线程，并使用 `ThreadPoolExecutor`、`Future` 和 `as_completed()`。
- [共享状态与锁](./12-threads-and-synchronization/shared-state-and-locks)：理解竞争条件，使用 `Lock`
  保护完整业务不变量，并区分修改和同步边界。
- [队列与同步工具](./12-threads-and-synchronization/queues-and-synchronization)：使用线程安全 Queue
  传递任务，理解哨兵、`task_done()`、背压及其他同步工具。
- [死锁、GIL 与线程使用原则](./12-threads-and-synchronization/deadlocks-gil-and-guidelines)：统一锁顺序，
  理解 GIL 对 CPU 任务的影响，并确定线程的关闭和错误处理方式。
