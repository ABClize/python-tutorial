"""迭代器、生成器和 itertools。"""

from itertools import chain, islice, pairwise


class Countdown:
    """自定义迭代器：__iter__ 返回自己，__next__ 产生下一个元素。"""

    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


def fibonacci():
    """无限生成器；只在请求下一个值时才计算。"""
    left, right = 0, 1
    while True:
        yield left
        left, right = right, left + right


def read_chunks(text, size):
    for start in range(0, len(text), size):
        yield text[start : start + size]


def main():
    print("自定义迭代器:", list(Countdown(5)))

    fib = fibonacci()
    print("前 10 个斐波那契数:", list(islice(fib, 10)))
    print("分块读取:", list(read_chunks("abcdefghijkl", 4)))

    merged = chain([1, 2], [3, 4], [5])
    print("chain 合并:", list(merged))
    print("相邻元素:", list(pairwise([10, 20, 30, 40])))

    # 生成器表达式比列表推导式更省内存。
    total = sum(number * number for number in range(10))
    print("生成器表达式求和:", total)


if __name__ == "__main__":
    main()
