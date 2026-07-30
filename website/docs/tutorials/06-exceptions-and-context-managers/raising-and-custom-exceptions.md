# Python 主动抛出与自定义异常

函数发现参数、状态或业务规则不成立时，可以使用 `raise` 主动终止当前操作。异常类型和消息共同构成
函数的失败接口，调用方可以据此选择恢复方式。

<p class="source-note">对应源码：<code>python/python_interview_practice/06_exceptions_context.py</code></p>

## 使用 raise 主动抛出异常

```python
def withdraw(balance: int, amount: int) -> int:
    if amount <= 0:
        raise ValueError("取款金额必须大于 0")
    if amount > balance:
        raise RuntimeError("余额不足")
    return balance - amount


print(withdraw(100, 30))
```

运行结果：

```text
70
```

异常类型应尽量表达失败原因：

| 异常 | 常见含义 |
| --- | --- |
| `TypeError` | 值的类型不符合接口 |
| `ValueError` | 类型正确，但值不在允许范围 |
| `KeyError`、`IndexError` | key 或索引不存在 |
| `FileNotFoundError` | 指定文件不存在 |
| `RuntimeError` | 没有更准确内置类型的运行状态错误 |

业务调用方需要稳定识别某类错误时，可以定义自定义异常。

## 重新抛出当前异常

在 `except` 中单独写 `raise`，会保留原 traceback 并继续传播：

```python
def parse_port(text: str) -> int:
    try:
        return int(text)
    except ValueError:
        print(f"无法解析端口：{text!r}")
        raise
```

不要使用 `raise error` 代替裸 `raise`。前者会把重新抛出的位置加入 traceback，通常会干扰原始错误
位置的阅读。

捕获、记录再抛出可能造成同一个异常被多层重复记录。一般在请求入口、命令入口或后台任务入口记录一次
完整异常。

## 自定义异常

自定义异常通常继承 `Exception` 或语义接近的内置异常：

```python
class InvalidAgeError(ValueError):
    """年龄超出允许范围。"""


def validate_age(age: object) -> int:
    if not isinstance(age, int):
        raise TypeError("年龄必须是整数")
    if not 0 <= age <= 150:
        raise InvalidAgeError("年龄应在 0 到 150 之间")
    return age
```

这与对应源码的判断一致。调用方可以分别处理类型错误和范围错误：

```python
for value in [20, -1, "18"]:
    try:
        print("合法年龄：", validate_age(value))
    except InvalidAgeError as error:
        print("年龄范围错误：", error)
    except TypeError as error:
        print("年龄类型错误：", error)
```

运行结果：

```text
合法年龄： 20
年龄范围错误： 年龄应在 0 到 150 之间
年龄类型错误： 年龄必须是整数
```

## bool 是 int 的子类

Python 中 `bool` 是 `int` 的子类：

```python
print(isinstance(True, int))
print(validate_age(True))
```

运行结果：

```text
True
True
```

因此源码中的 `isinstance(age, int)` 会接受 `True` 和 `False`。如果业务规则不允许布尔值，需要明确
排除：

```python
if isinstance(age, bool) or not isinstance(age, int):
    raise TypeError("年龄必须是整数")
```

这属于额外业务约束，不是 `isinstance(value, int)` 的默认行为。

## 建立异常层次

同一业务领域可以使用一个公共父异常：

```python
class OrderError(Exception):
    """订单操作失败。"""


class OrderNotFoundError(OrderError):
    """订单不存在。"""


class OrderStateError(OrderError):
    """订单状态不允许当前操作。"""
```

调用方可以捕获具体子类，也可以在统一边界捕获 `OrderError`。异常层次不宜过深；只有调用方确实需要
区分处理方式时，才值得新增子类。

## 异常链

跨抽象边界转换异常时，使用 `raise ... from ...` 保留原始原因：

```python
class ConfigError(Exception):
    pass


def read_port(text: str) -> int:
    try:
        return int(text)
    except ValueError as error:
        raise ConfigError("配置项 port 必须是整数") from error
```

traceback 会同时展示底层 `ValueError` 和上层 `ConfigError`，并说明两者的因果关系。

不希望向用户展示底层上下文时，可以写：

```python
raise ConfigError("配置无效") from None
```

`from None` 只抑制 traceback 对直接上下文的显示，原异常仍可能保存在 `__context__`。日志和用户响应
需要分层处理，不能依靠它清除敏感信息。

## 自定义异常的注意事项

- 异常名称通常以 `Error` 结尾。
- 消息应说明哪个约束失败，不要只写“操作失败”。
- 不要把密码、令牌、完整 SQL 或隐私数据放进异常消息。
- 异常负责表达失败，不应被当成普通成功分支的返回值。
- 公共函数应在文档中说明调用方需要处理的主要异常。
