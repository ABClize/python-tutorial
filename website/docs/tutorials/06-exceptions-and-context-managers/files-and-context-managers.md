# Python 文件与上下文管理器

上下文管理器用于自动释放资源。文件、连接和锁使用完后都要释放。把它们放进 `with` 代码块后，无论
代码正常结束还是抛出异常，Python 都会调用退出逻辑。

<p class="source-note">对应源码：<code>python/python_interview_practice/06_exceptions_context.py</code></p>

## 手动关闭文件

不使用上下文管理器时，需要通过 `finally` 保证关闭。下面的示例读取内存文件，然后检查文件是否已经
关闭：

```python
from io import StringIO

file = StringIO("82\n91\n")
try:
    content = file.read()
finally:
    file.close()

print(content.splitlines())
print(file.closed)
```

运行结果：

```text
['82', '91']
True
```

如果只在正常路径调用 `close()`，读取或处理过程抛出异常时就可能跳过清理。

## 使用 with 管理文件

同一段文件读取代码可以改用 `with`：

```python
from io import StringIO

with StringIO("82\n91\n") as file:
    content = file.read()

print(content.splitlines())
print(file.closed)
```

运行结果：

```text
['82', '91']
True
```

`as file` 接收上下文管理器进入时返回的对象。正常离开、提前 `return` 或代码块内抛出异常时，文件
都会关闭。

真实文件同样使用这个结构：

```python
with open("scores.txt", encoding="utf-8") as file:
    content = file.read()
```

这段代码假定当前目录已经存在 `scores.txt`。文件不存在时会抛出 `FileNotFoundError`。

## pathlib 读写小文件

`Path.read_text()` 和 `write_text()` 会自动打开和关闭文件。下面的示例写入两个分数，再把它们读
回来：

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as directory:
    path = Path(directory) / "scores.txt"
    path.write_text("82\n91\n", encoding="utf-8")
    content = path.read_text(encoding="utf-8")

print(content.splitlines())
```

运行结果：

```text
['82', '91']
```

这两个方法适合能一次放入内存的小文件。大文件、逐行数据或需要设置换行和缓冲参数时，使用
`with path.open(...)`：

```python
from pathlib import Path

path = Path("large.log")
with path.open(encoding="utf-8") as file:
    for line in file:
        process(line.rstrip("\n"))
```

## 同时管理多个资源

资源数量固定时，可以在同一个 `with` 中列出。下面的示例同时打开输入文件和输出文件：

```python
with (
    open("input.txt", encoding="utf-8") as source,
    open("output.txt", "w", encoding="utf-8") as target,
):
    target.write(source.read())
```

这个示例假定 `input.txt` 已经存在。上下文管理器从左到右进入，从右到左退出。如果打开输出文件失败，
已经成功打开的输入文件仍会关闭。

## 上下文管理协议

对象实现 `__enter__()` 和 `__exit__()` 后，就可以用于 `with`。下面的 `Timer` 记录代码块运行时间：

```python
from time import perf_counter


class Timer:
    def __enter__(self):
        self.started_at = perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.elapsed = perf_counter() - self.started_at
        return False


with Timer() as timer:
    total = sum(range(100_000))

print(total)
print(timer.elapsed >= 0)
```

运行结果：

```text
4999950000
True
```

进入 `with` 时调用 `__enter__()`，它的返回值绑定到 `as` 后面的变量。退出时调用 `__exit__()`：

- 正常退出时，三个异常参数都是 `None`；
- 异常退出时，参数分别是异常类型、异常对象和 traceback；
- 返回 `False` 或 `None` 表示异常继续传播；
- 返回 `True` 表示异常已经被上下文管理器处理。

除非上下文管理器明确负责恢复某种异常，否则应返回 `False`，让错误继续传播。

## 上下文管理器不等于异常处理

`with` 保证退出逻辑得到调用，但不会默认吞掉代码块中的异常：

```python
class Resource:
    def __enter__(self):
        print("进入")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("退出")
        return False


with Resource():
    raise ValueError("处理失败")
```

输出会先出现“进入”和“退出”，随后 `ValueError` 继续向外传播。

## 文件处理注意事项

- 文本文件显式指定 `encoding="utf-8"`。
- 不要假定文件一定存在或一定有权限，按调用场景处理 `OSError` 子类。
- `read()` 和 `read_text()` 会一次读取全部内容，大文件应逐行处理。
- 写入重要文件时还要考虑临时文件、原子替换和并发写入。
- 上下文管理器负责生命周期，不会自动验证文件内容。
