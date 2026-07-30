# 测试隔离与依赖注入

测试隔离是指每个测试都能单独运行，不依赖其他测试的顺序和残留数据。依赖注入是把仓储、支付或通知
对象从外部传给业务代码，而不是在业务函数内部直接创建。测试时可以传入简单的替代实现。

<!-- 对应源码：python/python_interview_practice/14_testing_and_mocking.py -->

## 常见状态污染

- 修改模块全局变量后没有恢复；
- 多个测试共用可变对象；
- 数据库事务没有回滚；
- 固定文件名互相覆盖；
- patch 离开测试后仍然生效；
- 缓存没有清理；
- 时间、随机数和环境变量没有控制。

每个测试单独运行和整套运行都应得到相同结果。fixture、`tmp_path`、`monkeypatch` 和 Mock 上下文管理器
可以帮助恢复状态，但最根本的做法是减少隐式全局依赖。

## 用 Protocol 描述外部能力

仓库中的结账服务依赖库存、支付和通知：

```python
from typing import Protocol


class Inventory(Protocol):
    def reserve(self, sku: str, quantity: int) -> bool: ...


class PaymentGateway(Protocol):
    def charge(self, customer_id: str, amount: int) -> str: ...


class Notifier(Protocol):
    def send(
        self,
        customer_id: str,
        message: str,
    ) -> None: ...
```

Protocol 只描述服务需要的方法。真实对象和测试替身不必继承这些类，只要提供相同接口即可。

## 真实的 CheckoutService 接口

返回值是不可变收据：

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Receipt:
    sku: str
    quantity: int
    total_cents: int
    transaction_id: str


class OutOfStockError(Exception):
    pass
```

服务通过构造函数接收依赖：

```python
class CheckoutService:
    def __init__(
        self,
        inventory: Inventory,
        payment: PaymentGateway,
        notifier: Notifier,
    ) -> None:
        self.inventory = inventory
        self.payment = payment
        self.notifier = notifier

    def checkout(
        self,
        *,
        customer_id: str,
        sku: str,
        quantity: int,
        unit_price_cents: int,
    ) -> Receipt:
        if quantity <= 0:
            raise ValueError("quantity 必须大于 0")

        if not self.inventory.reserve(sku, quantity):
            raise OutOfStockError(sku)

        total = quantity * unit_price_cents
        transaction_id = self.payment.charge(
            customer_id,
            total,
        )
        self.notifier.send(
            customer_id,
            f"支付成功：{total} 分",
        )
        return Receipt(
            sku,
            quantity,
            total,
            transaction_id,
        )
```

调用顺序体现了业务边界：

1. 参数无效时，不调用任何外部依赖；
2. 库存预留失败时，不扣款、不通知；
3. 预留成功后计算整数分金额；
4. 支付成功后发送通知并返回 `Receipt`。

金额使用整数分，避免二进制浮点数直接表示货币小数。

## 为什么依赖注入便于测试

如果 `checkout()` 内部直接创建网络客户端，测试只能 patch 内部实现或访问真实服务。构造函数注入后，
测试可以传入内存 Fake 或 Mock：

```python
inventory = FakeInventory({"PYTHON-BOOK": 5})
payment = FakePayment()
notifier = FakeNotifier()

service = CheckoutService(
    inventory,
    payment,
    notifier,
)
```

业务对象不知道依赖是 HTTP 客户端、数据库适配器还是测试替身。测试可以专注于结账规则，而集成测试再
确认真实适配器能正确连接外部系统。

依赖注入不是“为了 Mock 而拆函数”。依赖本来就是系统边界，显式传入只是让边界在代码中可见。
