# Python contextlib 与高级异常

标准库 `contextlib` 提供了一组上下文管理工具。它可以把生成器函数变成上下文管理器，也可以管理
数量不固定的资源。Python 3.11 还提供了 `ExceptionGroup`，用于一次保存多个异常。

<p class="source-note">对应源码：<code>python/python_interview_practice/06_exceptions_context.py</code></p>

## 使用 @contextmanager

进入和退出逻辑较短时，可以使用 `contextlib.contextmanager`。下面的示例在进入代码块时打印“获取
资源”，在离开时打印“释放资源”：

```python
from contextlib import contextmanager


@contextmanager
def managed_resource(name: str):
    print(f"获取资源：{name}")
    try:
        yield {"name": name, "status": "ready"}
    finally:
        print(f"释放资源：{name}")


with managed_resource("数据库连接") as resource:
    print("使用资源：", resource["status"])
```

运行结果：

```text
获取资源：数据库连接
使用资源： ready
释放资源：数据库连接
```

输出顺序说明：先获取资源，再执行 `with` 代码块，最后释放资源。`yield` 之前是进入逻辑，`yield`
的值绑定到 `as` 后面的变量，`finally` 中的代码负责退出。被
`@contextmanager` 装饰的生成器在一次上下文进入中必须恰好 yield 一次。

## suppress：忽略一种已知异常

删除一个可能不存在的临时文件时，“文件不存在”可以等同于目标已经达到：

```python
from contextlib import suppress
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as directory:
    path = Path(directory) / "temporary.txt"

    with suppress(FileNotFoundError):
        path.unlink()

print("清理完成")
```

运行结果：

```text
清理完成
```

`suppress()` 只适合异常确实可以安全忽略的窄代码块。不要用它包住大量操作，也不要用宽泛
`suppress(Exception)` 隐藏缺陷。

## closing 与 nullcontext

`closing(obj)` 在退出时调用 `obj.close()`。下面的 `LegacyResource` 有 `close()` 方法，但没有实现
`__enter__()` 和 `__exit__()`：

```python
from contextlib import closing


class LegacyResource:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


resource = LegacyResource()
with closing(resource):
    print(resource.closed)

print(resource.closed)
```

运行结果：

```text
False
True
```

`nullcontext(value)` 不增加进入和退出行为。下面的示例把已有的 `StringIO` 直接交给 `with` 使用：

```python
from contextlib import nullcontext
from io import StringIO

existing = StringIO("Python")

with nullcontext(existing) as file:
    print(file.read())
```

运行结果：

```text
Python
```

`nullcontext` 不会替调用方关闭已有资源，资源所有权仍需明确。

## ExitStack 动态管理多个资源

资源数量在运行时才确定时，可以使用 `ExitStack`。下面的示例根据 `paths` 列表打开两个文件：

```python
from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as directory:
    root = Path(directory)
    paths = [root / "a.txt", root / "b.txt"]
    paths[0].write_text("A", encoding="utf-8")
    paths[1].write_text("B", encoding="utf-8")

    with ExitStack() as stack:
        files = [
            stack.enter_context(path.open(encoding="utf-8"))
            for path in paths
        ]
        contents = [file.read() for file in files]

print(contents)
```

运行结果：

```text
['A', 'B']
```

`ExitStack` 按后进先出顺序执行登记的退出逻辑。进入中途失败时，先前成功进入的资源也会得到清理。
资源数量固定时，普通多项 `with` 更直观。

## ExceptionGroup

Python 3.11 的 `ExceptionGroup` 可以携带多个独立异常。下面的异常组同时保存一个值错误和一个超时
错误：

```python
try:
    raise ExceptionGroup(
        "批量任务失败",
        [ValueError("输入错误"), TimeoutError("请求超时")],
    )
except* ValueError as errors:
    print("值错误数量：", len(errors.exceptions))
except* TimeoutError as errors:
    print("超时数量：", len(errors.exceptions))
```

运行结果：

```text
值错误数量： 1
超时数量： 1
```

`except*` 会从异常组中拆出匹配部分。多个 `except*` 可以分别处理同一个异常组中的不同子异常，没有被
处理的部分继续传播。

普通顺序代码通常仍使用普通异常。`ExceptionGroup` 常见于结构化并发和批量操作，因为多个子任务可能
在相近时间分别失败。

## contextlib 使用注意事项

- 要说明资源由谁关闭，避免重复关闭或无人关闭。
- `@contextmanager` 的清理逻辑放在 `finally` 中。
- `suppress()` 的范围和异常类型保持最小。
- 动态资源使用 `ExitStack`，固定资源使用普通 `with`。
- `ExceptionGroup` 用于保留多个失败，不应随意把无关错误打包。
