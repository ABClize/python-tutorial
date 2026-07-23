"""线程、线程池和锁；此例使用 sleep 模拟 I/O 等待。"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from time import sleep


def fetch_data(number):
    sleep(0.02)  # 网络请求、读文件等 I/O 等待时，线程可能有效果
    return {"id": number, "value": number * number}


def thread_pool_example():
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(fetch_data, number) for number in range(1, 6)]
        results = [future.result() for future in as_completed(futures)]
    return sorted(results, key=lambda item: item["id"])


def lock_example():
    """锁保护共享变量；没有锁时自增在多线程中可能发生竞争。"""
    total = 0
    lock = Lock()

    def add_many_times():
        nonlocal total
        for _ in range(1_000):
            with lock:
                total += 1

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(add_many_times) for _ in range(4)]
        for future in futures:
            future.result()
    return total


def main():
    print("线程池结果:", thread_pool_example())
    print("加锁后的共享计数:", lock_example())
    print("提示：CPU 密集型任务通常优先考虑 multiprocessing，而非线程。")


if __name__ == "__main__":
    main()
