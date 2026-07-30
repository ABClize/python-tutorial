# patch、side_effect 与 monkeypatch

依赖无法直接注入时，可以在测试期间替换被测代码实际读取的名字。替换必须有明确作用域，测试结束后
恢复原对象。

<p class="source-note">对应源码：<code>python/python_interview_practice/14_testing_and_mocking.py</code></p>

## patch 替换名字

假设 `service.py`：

```python
from mailer import send_email


def register(email: str) -> None:
    send_email(email, "注册成功")
```

测试替换 `service.send_email`：

```python
from service import register
from unittest.mock import patch


def test_register_sends_email() -> None:
    with patch("service.send_email") as send_email:
        register("user@example.com")

    send_email.assert_called_once_with(
        "user@example.com",
        "注册成功",
    )
```

`register()` 运行时从 `service` 模块的全局命名空间读取名字，所以 patch 的是
`service.send_email`，不是它最初定义的 `mailer.send_email`。

判断 patch 路径：

1. 找到被测函数使用的名字；
2. 确认运行时从哪个模块命名空间读取；
3. 替换该模块中的名字。

可以通过构造函数或函数参数注入的依赖，通常比大量 patch 模块全局对象更清楚。

## patch.object

已持有类或对象时：

```python
from unittest.mock import patch


class TokenFactory:
    @staticmethod
    def generate() -> str:
        return "real-token"


with patch.object(
    TokenFactory,
    "generate",
    return_value="fixed-token",
):
    print(TokenFactory.generate())

print(TokenFactory.generate())
```

运行结果：

```text
fixed-token
real-token
```

## side_effect 抛出异常

```python
from unittest.mock import Mock

request = Mock(
    side_effect=TimeoutError("请求超时")
)

try:
    request()
except TimeoutError as error:
    print(error)
```

运行结果：

```text
请求超时
```

## side_effect 表示连续结果

```python
request = Mock(
    side_effect=[
        TimeoutError("第一次超时"),
        {"status": "ok"},
    ]
)

try:
    request()
except TimeoutError:
    print("准备重试")

print(request())
print(request.call_count)
```

运行结果：

```text
准备重试
{'status': 'ok'}
2
```

列表耗尽后继续调用会抛出 `StopIteration`。

## side_effect 根据参数计算

```python
def fake_shipping(weight_kg: float) -> int:
    return round(weight_kg * 100)


shipping_fee = Mock(side_effect=fake_shipping)

print(shipping_fee(0.5))
print(shipping_fee(2.0))
```

运行结果：

```text
50
200
```

side_effect 适合模拟重试、超时和参数相关结果，不应复制完整业务实现。

## monkeypatch

pytest 的 `monkeypatch` fixture 可以临时修改属性、字典、工作目录和环境变量：

```python
import os


def read_mode() -> str:
    return os.getenv("APP_MODE", "development")


def test_mode_comes_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("APP_MODE", "test")

    assert read_mode() == "test"
```

测试结束后环境变量会恢复。常用方法：

- `setenv()` / `delenv()`；
- `setattr()` / `delattr()`；
- `setitem()` / `delitem()`；
- `chdir()`。

patch 和 monkeypatch 都是临时替换工具，重点是替换正确位置并保证自动恢复。
