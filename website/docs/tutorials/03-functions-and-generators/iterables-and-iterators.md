# Python 可迭代对象与迭代器

for 循环之所以能遍历列表、字符串和文件，是因为这些对象遵守迭代协议。本页会区分“可以被遍历的对象”和“记录遍历位置的对象”，并手写一个最小迭代器。

<p class="source-note">对应源码：<code>python/python_interview_practice/04_iterators_generators.py</code></p>

## 可迭代对象和迭代器

`for` 循环通过迭代协议获取数据：

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

再调用一次 `next(iterator)` 会抛出 `StopIteration`，表示迭代结束。

- 可迭代对象实现 `__iter__()`，可以传给 `iter()`，例如 list、tuple、str；
- 迭代器实现 `__iter__()` 和 `__next__()`，记录当前遍历位置；
- `iter(iterator) is iterator` 对迭代器通常为 `True`。

自定义倒计时迭代器：

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

容器通常可以重复遍历；迭代器保存消费进度，耗尽后不能自动回到开头。
