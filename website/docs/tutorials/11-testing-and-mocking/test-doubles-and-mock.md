# 测试替身与 Mock

测试替身代替真实外部依赖。不同替身强调的能力不同：有的保存状态，有的只返回固定值，有的用于验证
调用参数。

<p class="source-note">对应源码：<code>python/python_interview_practice/14_testing_and_mocking.py</code></p>

## Fake、Stub、Mock 和 Spy

| 替身 | 主要用途 | 示例 |
| --- | --- | --- |
| Fake | 提供简化但可工作的实现 | 内存仓储 |
| Stub | 为调用提供预设结果 | 固定返回库存充足 |
| Mock | 记录交互并提供调用断言 | 验证支付金额 |
| Spy | 包装真实对象并记录调用 | 观察真实实现是否被调用 |

一个对象可能同时具有多种特征。选择替身时先判断测试关注最终状态，还是发给外部系统的命令。

## Fake 示例

```python
class FakeUserRepository:
    def __init__(self, users: dict[int, str]) -> None:
        self.users = users

    def find_name(self, user_id: int) -> str | None:
        return self.users.get(user_id)


def welcome_user(
    user_id: int,
    repository: FakeUserRepository,
) -> str:
    name = repository.find_name(user_id)
    if name is None:
        raise LookupError("用户不存在")
    return f"欢迎，{name}"
```

```python
def test_existing_user_is_welcomed() -> None:
    repository = FakeUserRepository({1: "小林"})

    result = welcome_user(1, repository)

    assert result == "欢迎，小林"
```

Fake 保存有意义的状态，适合结果导向的测试。

## Mock 的基本用法

```python
from unittest.mock import Mock

sender = Mock()
sender.send("user@example.com", "课程已开始")

print(sender.send.call_count)
```

运行结果：

```text
1
```

设置返回值：

```python
inventory = Mock()
inventory.reserve.return_value = True

print(inventory.reserve("PYTHON-BOOK", 2))
```

运行结果：

```text
True
```

## 验证调用

```python
sender.send.assert_called_once_with(
    "user@example.com",
    "课程已开始",
)
```

| 断言 | 作用 |
| --- | --- |
| `assert_called()` | 至少调用一次 |
| `assert_called_once()` | 恰好调用一次 |
| `assert_called_with(...)` | 最后一次调用参数匹配 |
| `assert_called_once_with(...)` | 只调用一次且参数匹配 |
| `assert_not_called()` | 没有调用 |
| `assert_has_calls(...)` | 包含指定调用序列 |

`assert_called_with()` 只检查最后一次调用，不能代替 `assert_called_once_with()`。

## 使用 spec

```python
from unittest.mock import Mock

inventory = Mock(spec=Inventory)
inventory.reserve.return_value = True

print(inventory.reserve("BOOK", 1))
```

运行结果：

```text
True
```

访问不存在的方法会更早失败：

```python
inventory.resreve("BOOK", 1)
```

结果类似：

```text
AttributeError: Mock object has no attribute 'resreve'
```

`spec` 主要限制属性名称，不完整检查调用签名。需要严格匹配签名时使用 `create_autospec()`。

## 测试结账成功

下面的测试与仓库中真实的 `CheckoutService`、`Receipt` 接口一致：

```python
from unittest.mock import Mock

inventory = Mock(spec=Inventory)
payment = Mock(spec=PaymentGateway)
notifier = Mock(spec=Notifier)

inventory.reserve.return_value = True
payment.charge.return_value = "txn-001"

service = CheckoutService(
    inventory,
    payment,
    notifier,
)
receipt = service.checkout(
    customer_id="customer-7",
    sku="PYTHON-BOOK",
    quantity=2,
    unit_price_cents=4_500,
)

assert receipt == Receipt(
    "PYTHON-BOOK",
    2,
    9_000,
    "txn-001",
)
inventory.reserve.assert_called_once_with(
    "PYTHON-BOOK",
    2,
)
payment.charge.assert_called_once_with(
    "customer-7",
    9_000,
)
notifier.send.assert_called_once_with(
    "customer-7",
    "支付成功：9000 分",
)
```

返回值和三个外部交互都是结账成功的直接结果。

## 测试失败后的副作用

库存不足时，服务抛出 `OutOfStockError`，支付和通知都不能执行：

```python
import pytest

inventory.reserve.return_value = False

with pytest.raises(
    OutOfStockError,
    match="PYTHON-BOOK",
):
    service.checkout(
        customer_id="customer-7",
        sku="PYTHON-BOOK",
        quantity=1,
        unit_price_cents=4_500,
    )

payment.charge.assert_not_called()
notifier.send.assert_not_called()
```

失败分支不仅检查异常，还要检查明确禁止的副作用。纯计算函数通常只验证返回值，不需要为了使用 Mock 而
断言内部每一步。
