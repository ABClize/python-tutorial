# Python 异常基础：传播、捕获与清理

异常表示代码在运行时无法继续完成当前操作。转换失败、文件不存在、索引越界和除数为零都会产生
异常。能够处理错误的代码使用 `try` 和 `except` 捕获异常；不能处理时，就让异常继续向上传播。

<p class="source-note">对应源码：<code>python/python_interview_practice/06_exceptions_context.py</code></p>

## 语法错误与运行时异常

语法错误表示 Python 无法解析代码。例如下面的 `if` 缺少冒号：

```text
if score >= 60
    print("通过")
```

解释器会在程序正常运行前报告 `SyntaxError`。

异常发生在语法正确的代码执行期间。下面四行代码会分别产生四种异常：

```python
int("abc")                  # ValueError
{"name": "小林"}["age"]    # KeyError
[1, 2][9]                   # IndexError
10 / 0                      # ZeroDivisionError
```

这些语句分别违反了值转换、字典查找、序列索引和除法的运行时规则。Ruff、编辑器和类型检查器可以提前
发现一部分静态问题，但不能取代运行时错误处理。

## 异常沿调用栈传播

函数内部没有捕获异常时，异常会传到调用它的上一层。下面的错误从 `parse_score()` 传到
`load_score()`：

```python
def parse_score(text: str) -> int:
    return int(text)


def load_score() -> int:
    return parse_score("abc")


load_score()
```

运行结果的最后一行是：

```text
ValueError: invalid literal for int() with base 10: 'abc'
```

完整 traceback 会同时列出 `load_score()` 和 `parse_score()` 的调用位置。阅读 traceback 时，通常
先看最后一行的异常类型和消息，再向上寻找最靠近自己代码的调用帧。

传播过程中，只要某一层出现匹配的 `except`，Python 就会进入对应处理分支。一直没有被捕获的异常到达
程序入口后，解释器会报告 traceback；发生在主线程时，程序通常随之退出。

## try 与 except

`try` 中放置可能失败的操作，`except` 处理特定异常。下面的示例捕获整数转换失败：

```python
raw_score = "abc"

try:
    score = int(raw_score)
except ValueError:
    print("分数必须是整数")
```

运行结果：

```text
分数必须是整数
```

`int()` 抛出 `ValueError` 后，`try` 中后续语句不会继续执行，Python 直接寻找匹配的 `except`。

使用 `as` 可以取得异常对象：

```python
try:
    score = int("abc")
except ValueError as error:
    print(type(error).__name__)
    print(error)
```

运行结果：

```text
ValueError
invalid literal for int() with base 10: 'abc'
```

`try` 范围应尽量小。范围过大时，同类型的编程错误可能被误当成预期输入错误。

## 捕获多个异常

不同异常需要不同处理时，使用多个 `except`。下面的代码分别处理文件不存在和内容格式错误：

```python
from pathlib import Path

path = Path("score.txt")

try:
    text = path.read_text(encoding="utf-8")
    score = int(text)
except FileNotFoundError:
    print("文件不存在")
except ValueError:
    print("文件内容不是整数")
```

异常分支按从上到下的顺序匹配。子类异常应写在父类异常前面：

```python
try:
    read_data()
except FileNotFoundError:
    print("指定文件不存在")
except OSError:
    print("其他操作系统错误")
```

`FileNotFoundError` 是 `OSError` 的子类。如果先写 `except OSError`，后面的文件不存在分支永远不会
执行。

多个异常使用相同处理逻辑时，可以写成 tuple：

```python
try:
    value = int(raw_value)
except (TypeError, ValueError) as error:
    print(f"无法转换：{error}")
```

只捕获当前层知道如何恢复、转换或反馈的异常。下面的写法会隐藏真正原因：

```python
try:
    do_everything()
except Exception:
    pass
```

`Exception` 已经覆盖绝大多数应用异常。裸 `except:` 范围更宽，还会捕获 `KeyboardInterrupt`、
`SystemExit` 等通常应继续传播的异常。

## else 与 finally

完整的异常结构还可以包含 `else` 和 `finally`。下面的转换会成功，因此执行 `else`；无论是否成功，
`finally` 都会执行：

```python
try:
    score = int("82")
except ValueError:
    print("输入错误")
else:
    print("解析成功：", score)
finally:
    print("本次解析结束")
```

运行结果：

```text
解析成功： 82
本次解析结束
```

各部分的执行条件：

| 区域 | 执行条件 | 适合放置 |
| --- | --- | --- |
| `try` | 正常进入 | 可能失败的最小操作 |
| `except` | 匹配到异常 | 恢复、转换或用户反馈 |
| `else` | `try` 正常执行完毕 | 依赖成功结果的后续逻辑 |
| `finally` | 离开整个结构时 | 必须执行的清理 |

“正常执行完毕”表示 `try` 没有抛出异常，也没有通过 `return`、`break` 或 `continue` 提前离开。
把成功后的逻辑放进 `else`，可以避免它抛出的同类型异常被前面的 `except` 意外捕获。

`finally` 在正常结束、捕获异常、继续抛出异常和函数返回时都会执行。不要在 `finally` 中使用
`return`、`break` 或 `continue` 覆盖正在传播的异常或返回值。

## 捕获异常的注意事项

捕获异常后通常只有三种合理处理：

- 恢复并继续，例如缺少可选配置时使用默认值；
- 转换成当前代码更容易处理的异常；
- 在程序入口或任务入口记录并向用户反馈。

如果当前层不知道如何处理，允许异常继续传播通常比返回一个含义不明的空值更安全。
