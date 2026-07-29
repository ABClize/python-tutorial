# 异常与上下文管理器

异常不是“程序坏了”的同义词，而是一条从底层失败点向合适处理边界传播的信息通道。上下文管理器
则保证无论代码正常返回还是异常退出，资源生命周期都能完整收尾。

<p class="source-note">对应源码：<code>python/python_interview_practice/06_exceptions_context.py</code></p>

## 先区分语法错误和运行时异常

语法错误表示代码无法被 Python 正确解析；异常则发生在语法合法、程序已经开始运行之后。例如
`int("abc")` 会在运行时抛出 `ValueError`。

```python
raw_count = "abc"

try:
    count = int(raw_count)
except ValueError as error:
    print(f"数量格式错误：{error}")
```

```text
数量格式错误：invalid literal for int() with base 10: 'abc'
```

`raise` 用来主动报告失败。内置异常已经能准确表达含义时优先复用，例如类型不对用 `TypeError`、
值超出范围用 `ValueError`；只有业务调用方需要稳定区分时，才定义领域异常。

异常处理的目标不是让所有代码“永不报错”，而是把失败变成可理解、可恢复或可追踪的结果。无法
恢复时继续抛出，通常比返回模糊的 `None` 更安全。

## 在知道如何处理的地方捕获

```python
class InvalidAgeError(ValueError):
    """年龄超出业务允许范围。"""


def validate_age(age: object) -> int:
    if not isinstance(age, int):
        raise TypeError("年龄必须是整数")
    if not 0 <= age <= 150:
        raise InvalidAgeError("年龄应在 0 到 150 之间")
    return age
```

底层函数负责报告具体失败，上层边界决定记录、重试、转换为 HTTP 响应还是终止任务。如果某一层
无法增加上下文或恢复，就让异常继续传播，不要捕获后原样吞掉。

## `try` 的四个区域各有职责

```python
try:
    age = validate_age(raw_age)
except (TypeError, InvalidAgeError) as error:
    report(error)
else:
    save(age)
finally:
    close_trace()
```

- `try`：只包围真正可能失败的操作，范围越小越清楚；
- `except`：处理明确知道的异常类型；
- `else`：仅在没有异常时执行，避免把后续 bug 误捕获；
- `finally`：无论正常、异常或提前返回都执行，适合收尾。

不要默认写 `except Exception: pass`。它会把编程错误和业务失败一起隐藏，让调用方误以为操作成功。

## 异常链保留根因

转换异常时使用 `raise NewError(...) from error`，让日志同时保留领域语义和底层根因：

```python
try:
    payload = json.loads(text)
except json.JSONDecodeError as error:
    raise ConfigurationError("配置不是合法 JSON") from error
```

若底层异常属于预期实现细节、不应展示给调用者，可使用 `from None` 抑制展示，但诊断价值也会降低。

## 上下文管理器管理生命周期

`with` 背后是 `__enter__` / `__exit__` 协议：

<div class="concept-map">
  <div class="concept-step"><small>进入 with</small><code>__enter__</code></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>使用资源</small><strong>代码块</strong></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>正常或异常</small><code>__exit__</code></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>决定是否传播</small><strong>返回值</strong></div>
</div>

`__exit__` 返回真值会吞掉异常，通常只有非常明确的协议才应该这样做。

简单生命周期可以用 `contextlib.contextmanager`：

```python
from contextlib import contextmanager


@contextmanager
def managed_resource(name: str):
    resource = acquire(name)
    try:
        yield resource
    finally:
        release(resource)
```

异步资源使用 `async with` 和 `__aenter__` / `__aexit__`，适合连接池、HTTP 客户端和异步锁。

文件就是最常见的上下文管理器。退出代码块时文件会自动关闭，即使解析过程中抛出异常也一样：

```python
from pathlib import Path

path = Path("settings.txt")

with path.open("r", encoding="utf-8") as file:
    first_line = file.readline().strip()

print(first_line)
```

不要把已经关闭的 `file` 对象传到外部长期使用；需要保留的是读取结果，而不是过期资源本身。

## 异常类型也是接口

调用方会根据异常类型决定行为，因此自定义异常应表达稳定语义，而不是把每个错误字符串都变成新类。
常见层次可以是：

```python
class ApplicationError(Exception):
    pass


class NotFoundError(ApplicationError):
    pass


class ConflictError(ApplicationError):
    pass
```

API 边界再把领域异常映射为 HTTP 状态码，领域层不需要导入 FastAPI。

## 异常层次决定捕获范围

大多数普通错误继承 `Exception`；`KeyboardInterrupt`、`SystemExit` 和 `GeneratorExit` 直接或
间接继承 `BaseException`，通常不应被业务代码吞掉。`asyncio.CancelledError` 也具有控制流语义，
清理后通常需要继续传播。

```python
try:
    await operation()
except DomainError:
    ...
except Exception:
    # 记录未预期故障，并继续抛出
    logger.exception("unexpected failure")
    raise
```

捕获顺序从具体到宽泛。父类异常写在前面会让后面的子类分支永远无法到达。

## 多个并发错误与 ExceptionGroup

Python 3.11 的 `ExceptionGroup` 可以同时携带多个异常，`except*` 按类型拆分处理：

```python
try:
    async with asyncio.TaskGroup() as group:
        group.create_task(load_user())
        group.create_task(load_orders())
except* TimeoutError as group:
    for error in group.exceptions:
        report_timeout(error)
```

普通 `except` 与 `except*` 的语义不同。结构化并发中，多个兄弟任务可能在取消生效前同时失败，
不能假设永远只有一个根因。

## 清理本身也可能失败

如果业务操作抛异常，随后 `finally` 的清理又抛出新异常，新异常会成为最终传播对象，原异常保留在
异常上下文中。资源清理应尽量幂等、短小，并避免用清理失败掩盖更重要的根因。

多个资源可以使用 `contextlib.ExitStack` 或 `AsyncExitStack` 动态注册清理动作，退出时按后进先出
顺序执行。这比手写层层嵌套的 try/finally 更易维护。

## 常见误区

### `finally` 中 return 可以安全覆盖结果

`finally` 中的 `return` 会压过原返回值，甚至吞掉正在传播的异常，通常应避免。

### 日志记录后必须重新包装异常

如果没有新增语义，直接 `raise` 保留原 traceback 更好。重复记录同一个异常还可能制造多份噪声日志。

### 上下文管理器只用于文件

任何具有“获取 → 使用 → 释放”生命周期的资源都适用，包括锁、事务、临时目录、追踪 span 和连接。

## 面试时怎么表述

> 异常应在能恢复或转换语义的边界捕获；`else` 放成功路径，`finally` 做必需清理。上下文管理器把
> 获取和释放封装成协议，保证正常和异常路径都收尾。转换异常时用异常链保留根因，避免宽泛捕获和
> 静默吞错。
