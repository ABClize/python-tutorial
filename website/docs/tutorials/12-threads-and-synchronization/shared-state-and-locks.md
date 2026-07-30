# 共享状态与锁

同一进程中的线程可以访问同一个对象。多个线程同时执行“读取、判断、写入”时，最终结果可能随执行
顺序变化。这种错误叫竞争条件。`Lock` 会让同一时刻只有一个线程进入受保护的代码。

<!-- 对应源码：python/python_interview_practice/07_concurrency.py、python/interview_exercises/concurrency.py -->

## 竞争条件

下面的函数对共享计数器执行读取和写入：

```python
counter = 0


def increment() -> None:
    global counter
    counter += 1
```

`counter += 1` 在语义上包含：

1. 读取旧值；
2. 计算旧值加一；
3. 写回新值。

两个线程都读到同一旧值时，其中一次增加可能被覆盖。

<ThreadLockDiagram />

图中展示的是业务操作交错。CPython 的 GIL 保护解释器内部状态，不保证多步业务规则原子执行；I/O 和
一些原生扩展也可能释放 GIL。

## 使用 Lock

下面用同一把锁保护计数器的更新：

```python
from threading import Lock

counter = 0
counter_lock = Lock()


def increment() -> None:
    global counter
    with counter_lock:
        counter += 1
```

`with counter_lock:` 在进入时获取锁，退出时释放。临界区抛出异常时也能正确释放。

仓库中的线程安全计数器：

```python
import threading


class ThreadSafeCounter:
    def __init__(self) -> None:
        self._value = 0
        self._lock = threading.Lock()

    def increment(self, amount: int = 1) -> None:
        with self._lock:
            self._value += amount

    @property
    def value(self) -> int:
        with self._lock:
            return self._value
```

读取也遵守同一把锁，避免观察到一组更新的中间状态。

## 锁保护完整不变量

提款规则是“余额足够时才能扣减”。检查和扣减必须位于同一个临界区：

```python
def withdraw(amount: int) -> bool:
    global balance

    with balance_lock:
        if balance < amount:
            return False
        balance -= amount
        return True
```

只给 `balance -= amount` 加锁仍然不够，因为两个线程可能同时通过余额检查。

锁保护的是一条必须共同成立的规则，不只是某个变量名。临界区应尽量短，不要在持锁期间执行网络请求、
长时间休眠或未知回调。

## Lock 与 RLock

普通 `Lock` 被同一线程再次获取时也会阻塞：

```python
with lock:
    with lock:
        pass
```

`RLock` 是可重入锁，同一线程可以重复获取，每次获取仍要对应释放。它适合同一对象的加锁方法之间存在
嵌套调用。

不需要重入时使用 `Lock`，它的所有权关系更简单。不要用 `RLock` 掩盖循环调用或锁范围不清。

## 锁与数据所有权

同步问题常有两种解决方向：

- 多个线程确实需要共同修改状态：用锁保护不变量；
- 工作可以划分给单一消费者：用 Queue 传递任务和所有权。

锁越多并不代表越安全。多把锁会引入获取顺序和死锁问题，先减少共享可变状态通常更容易维护。
