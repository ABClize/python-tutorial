# Python 可迭代对象与迭代器

可迭代对象是可以被 `for` 循环遍历的对象，例如列表、字符串和文件。迭代器负责逐个返回元素，
并记录当前遍历到的位置。

<!-- 对应源码：python/python_interview_practice/04_iterators_generators.py -->

## 可迭代对象和迭代器的区别

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

同一个列表可以创建多个互不影响的迭代器：

```python
numbers = [10, 20]
first = iter(numbers)
second = iter(numbers)

print(next(first))
print(next(first))
print(next(second))
```

运行结果：

```text
10
20
10
```

`first` 已经走到列表末尾，`second` 仍停在开头。列表保存数据，迭代器保存“下一次从哪里取”的状态。

## for 循环怎样使用迭代器

下面的 `for` 循环：

```python
for number in [10, 20]:
    print(number)
```

在概念上相当于：

```python
iterator = iter([10, 20])

while True:
    try:
        number = next(iterator)
    except StopIteration:
        break
    print(number)
```

运行结果都是：

```text
10
20
```

实际的 `for` 循环由 Python 解释器处理 `StopIteration`，不需要自己编写 `try/except`。理解这个过程
可以解释为什么列表、文件、生成器和自定义对象都能放进 `for`：只要 `iter(value)` 能返回迭代器即可。

## 自定义迭代器

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

## 迭代器只能向前消费

迭代器保存消费进度，耗尽后不能自动回到开头：

```python
iterator = iter([1, 2])

print(list(iterator))
print(list(iterator))
```

运行结果：

```text
[1, 2]
[]
```

第一次 `list(iterator)` 已经取完所有元素，第二次只能得到空列表。需要重新遍历列表时，可以再次调用
`iter(numbers)`；文件、生成器等对象是否能够重新遍历，则取决于对象自身。

> 进阶预览：下面的 `Iterable[T]` 和 `Iterator[T]` 是类型标注，`T` 表示元素类型。这两个名称来自
> `collections.abc`，泛型标注将在[泛型](../07-typing-and-protocols/generics)中详细说明。

函数接收一个“可以遍历的数据源”时，通常标注为 `Iterable[T]`。函数接收的是调用者已经开始消费、
并希望继续使用同一进度的对象时，才标注为 `Iterator[T]`。

## 使用哨兵值停止 iter

哨兵值是专门用来表示“停止”的特殊值。`iter()` 可以接收一个无参数函数和一个哨兵值，重复调用函数，
直到函数返回这个哨兵：

```python
source = iter(["A", "B", "END"])


def read_value() -> str:
    return next(source)


values = list(iter(read_value, "END"))
print(values)
```

运行结果：

```text
['A', 'B']
```

`"END"` 只负责表示停止，不会出现在结果中。这种写法常用于“重复读取，直到得到结束标记”的场景。
调用函数如果抛出其他异常，异常仍会向外传播；如果数据源先耗尽，`StopIteration` 也会结束迭代。

容器通常保存全部数据，并能创建新的迭代器重复遍历；迭代器只保存当前遍历状态，适合一次向前读取。
