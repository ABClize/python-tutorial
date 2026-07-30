# Python assert、LBYL 与 EAFP

Python 常见的检查方式有三种。`assert` 检查程序内部必须成立的条件。LBYL 先检查条件，再执行操作。
EAFP 先执行操作，失败后再捕获异常。三种方式不能随意互换。

<p class="source-note">对应源码：<code>python/python_interview_practice/06_exceptions_context.py</code></p>

## assert 检查内部不变量

下面的函数用 `assert` 检查数量是否大于 0：

```python
def average(total: int, count: int) -> float:
    assert count > 0, "内部不变量：count 必须大于 0"
    return total / count


print(average(30, 3))
```

运行结果：

```text
10.0
```

断言失败会抛出 `AssertionError`：

```python
average(30, 0)
```

运行结果的最后一行类似：

```text
AssertionError: 内部不变量：count 必须大于 0
```

错误消息来自 `assert` 后面的字符串，便于定位哪个内部条件没有成立。

## assert 不能代替输入校验

使用优化模式 `python -O` 时，assert 语句可能被移除。因此下面的代码不适合公开接口：

```python
def withdraw(balance: int, amount: int) -> int:
    assert amount > 0
    return balance - amount
```

外部输入、权限检查和业务规则必须显式抛出异常：

```python
def withdraw(balance: int, amount: int) -> int:
    if amount <= 0:
        raise ValueError("取款金额必须大于 0")
    return balance - amount
```

只有在“条件不成立就说明程序本身有错误”时，才适合使用 `assert`。用户输入不合法是正常失败，应使用
`if` 和 `raise`。

## LBYL：操作前先检查

LBYL 是 “Look Before You Leap” 的缩写：

下面的代码先检查字典中有没有 `"score"`，然后再读取：

```python
student = {"name": "小林", "score": 82}

if "score" in student:
    score = student["score"]
else:
    score = 0

print(score)
```

运行结果：

```text
82
```

这种形式把条件写在操作之前，适合条件本身就是主要业务分支的情况。

## EAFP：先执行再处理失败

EAFP 是 “Easier to Ask Forgiveness than Permission” 的缩写：

下面的代码直接读取 `"score"`。key 不存在时，再捕获 `KeyError`：

```python
student = {"name": "小林", "score": 82}

try:
    score = student["score"]
except KeyError:
    score = 0

print(score)
```

运行结果：

```text
82
```

Python 代码经常使用 EAFP。文件或共享状态可能在检查之后、操作之前发生变化。直接执行操作并处理实际
错误，可以避免这段时间差。

## 选择 LBYL 还是 EAFP

两种写法都不是绝对规则：

| 场景 | 更直接的选择 |
| --- | --- |
| 条件本身决定业务流程 | LBYL |
| 正常情况很常见，失败有明确异常 | EAFP |
| dict 缺少 key 时使用默认值 | `dict.get()` |
| 缺少 key 时还要创建容器 | `defaultdict` 或 `setdefault()` |
| 文件可能被并发删除 | 捕获实际文件操作异常 |
| 需要避免昂贵或不可逆操作 | 操作前显式校验 |

dict 的专用 API 往往比两种通用形式都简单：

```python
student = {"name": "小林"}
score = student.get("score", 0)

print(score)
```

运行结果：

```text
0
```

字典中没有 `"score"`，所以 `get()` 返回给定的默认值 `0`，也不会向字典中新增 key。

## 避免捕获过宽

EAFP 不表示“所有异常都忽略”：

```python
try:
    score = student["score"]
except Exception:
    score = 0
```

这段代码还会把 `student` 类型错误、代码拼写错误等缺陷变成默认分数。只捕获真正代表预期失败的
`KeyError` 更安全。

## 错误处理注意事项

- 数据进入系统时校验外部输入。
- 业务函数用明确的异常表示规则检查失败。
- 数据库和网络错误可以转换成调用方能理解的异常。
- 请求或任务入口统一记录未处理异常。
- 测试用 assert 验证结果，生产输入校验不用 assert。
