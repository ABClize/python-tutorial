# Python 可迭代对象与迭代器

可迭代对象是可以被 `for` 循环遍历的对象，例如列表、字符串和文件。迭代器负责逐个返回元素，
并记录当前遍历到的位置。

<p class="source-note">对应源码：<code>python/python_interview_practice/04_iterators_generators.py</code></p>

## 可迭代对象和迭代器

`for` 循环通过迭代协议获取数据。下面先用 `iter()` 从列表创建迭代器，再用 `next()` 取值：

```python
numbers = [10, 20]
iterator = iter(numbers)

print(next(iterator))
print(next(iterator))
```

运行结果：

```text
10
20
```

两次调用分别得到 `10` 和 `20`。再调用一次 `next(iterator)` 会抛出 `StopIteration`，
表示迭代结束。

- 可迭代对象实现 `__iter__()`，可以传给 `iter()`，例如 list、tuple、str；
- 迭代器实现 `__iter__()` 和 `__next__()`，记录当前遍历位置；
- `iter(iterator) is iterator` 对迭代器通常为 `True`。

下面自定义一个倒计时迭代器：

```python
class Countdown:
    def __init__(self, start: int) -> None:
        self.current = start

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


print(list(Countdown(3)))
```

运行结果：

```text
[3, 2, 1]
```

`list()` 不断调用 `__next__()`，得到 `3`、`2`、`1`。当 `current` 变为 `0` 时，
`__next__()` 抛出 `StopIteration`。

容器通常可以重复遍历；迭代器保存消费进度，耗尽后不能自动回到开头。
