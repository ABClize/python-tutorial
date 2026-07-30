"""线程池、进程池和锁；sleep 模拟 I/O，平方和模拟 CPU 计算。"""

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from threading import Lock
from time import sleep


def fetch_data(number: int) -> dict[str, int]:
    sleep(0.02)  # 网络请求、读文件等 I/O 等待时，线程可能有效果
    return {"id": number, "value": number * number}


def thread_pool_example() -> list[dict[str, int]]:
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(fetch_data, number) for number in range(1, 6)]
        results = [future.result() for future in as_completed(futures)]
    return sorted(results, key=lambda item: item["id"])


def sum_squares(limit: int) -> tuple[int, int]:
    """计算平方和；模块顶层函数可以交给子进程执行。"""
    total = sum(number * number for number in range(limit))
    return limit, total


def process_pool_example(limits: tuple[int, ...]) -> list[tuple[int, int]]:
    with ProcessPoolExecutor(max_workers=2) as executor:
        return list(executor.map(sum_squares, limits))


def lock_example() -> int:
    """锁保护共享变量；没有锁时自增在多线程中可能发生竞争。"""
    total = 0
    lock = Lock()

    def add_many_times() -> None:
        nonlocal total
        for _ in range(1_000):
            with lock:
                total += 1

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(add_many_times) for _ in range(4)]
        for future in futures:
            future.result()
    return total


def main() -> None:
    print("线程池结果:", thread_pool_example())
    limits = (20_000, 10_000, 15_000)
    print("进程池结果:", process_pool_example(limits))
    print("加锁后的共享计数:", lock_example())


if __name__ == "__main__":
    main()
