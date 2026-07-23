"""unittest 与 unittest.mock 面试示例。

本文件把“业务代码”和“测试代码”放在一起，方便直接阅读和运行。真实项目中通常会
把它们分别放到应用包和 tests/ 目录。

覆盖：
- 单元测试的 Arrange（准备）/ Act（执行）/ Assert（断言）
- dependency injection（依赖注入）：让核心逻辑不依赖真实网络和数据库
- Mock 的 spec、调用断言和返回值
- patch 与 patch.object：临时替换“被测代码查找依赖的位置”
- side_effect：模拟连续结果、动态行为和异常
- setUp：为每个测试创建彼此隔离的新对象

所有例子只使用标准库，不会发送真实请求或产生真实付款。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass
from typing import Protocol
from unittest.mock import Mock, call, patch

# ---------------------------------------------------------------------------
# 被测业务代码
# ---------------------------------------------------------------------------


class Inventory(Protocol):
    def reserve(self, sku: str, quantity: int) -> bool:
        """预留库存，成功时返回 True。"""


class PaymentGateway(Protocol):
    def charge(self, customer_id: str, amount: int) -> str:
        """收款并返回交易编号。金额单位为分，避免浮点金额误差。"""


class Notifier(Protocol):
    def send(self, customer_id: str, message: str) -> None:
        """向客户发送通知。"""


@dataclass(frozen=True)
class Receipt:
    sku: str
    quantity: int
    total_cents: int
    transaction_id: str


class OutOfStockError(Exception):
    """库存不足。"""


class CheckoutService:
    """只编排业务规则，外部系统通过构造函数注入。"""

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
        transaction_id = self.payment.charge(customer_id, total)
        self.notifier.send(customer_id, f"支付成功：{total} 分")
        return Receipt(sku, quantity, total, transaction_id)


class RemoteClient:
    """用于提供 Mock spec 的接口示例；测试不会实例化真实客户端。"""

    def fetch(self, key: str) -> dict[str, int]:
        raise NotImplementedError


def fetch_with_retry(
    client: RemoteClient,
    key: str,
    *,
    attempts: int = 3,
) -> dict[str, int]:
    """只重试 TimeoutError；最后一次仍失败时保留原异常。"""
    if attempts < 1:
        raise ValueError("attempts 至少为 1")

    for attempt in range(1, attempts + 1):
        try:
            return client.fetch(key)
        except TimeoutError:
            if attempt == attempts:
                raise

    raise AssertionError("循环逻辑保证这里不可达")


def request_json(url: str) -> dict[str, object]:
    """代表真实 HTTP 边界；单元测试必须 patch 它，避免网络请求。"""
    raise RuntimeError(f"测试不应访问真实网络: {url}")


def load_user_name(user_id: int) -> str:
    """注意：测试应替换本模块中的 request_json，而不是它最初定义的位置。"""
    payload = request_json(f"https://example.invalid/users/{user_id}")
    name = payload.get("name")
    if not isinstance(name, str):
        raise ValueError("响应中缺少字符串 name")
    return name


class TokenFactory:
    @staticmethod
    def generate() -> str:
        """真实项目可能生成随机 UUID；测试用 patch 固定它。"""
        return "real-token"


def create_session(user_id: int) -> dict[str, object]:
    return {"user_id": user_id, "token": TokenFactory.generate()}


def shipping_fee(weight_kg: float) -> int:
    """简单运费函数，作为 patch(side_effect=函数) 的替换目标。"""
    return 1000 if weight_kg <= 1 else 1500


def quote_orders(weights: list[float]) -> list[int]:
    return [shipping_fee(weight) for weight in weights]


# ---------------------------------------------------------------------------
# 测试代码
# ---------------------------------------------------------------------------


class CheckoutServiceTests(unittest.TestCase):
    """依赖注入让每个外部交互都能被精确验证。"""

    def setUp(self) -> None:
        # spec 限制 Mock 只能访问接口中存在的属性，可尽早发现拼写错误。
        self.inventory = Mock(spec=Inventory)
        self.payment = Mock(spec=PaymentGateway)
        self.notifier = Mock(spec=Notifier)
        self.service = CheckoutService(
            inventory=self.inventory,
            payment=self.payment,
            notifier=self.notifier,
        )

    def test_checkout_success_calls_dependencies_in_expected_way(self) -> None:
        # Arrange
        self.inventory.reserve.return_value = True
        self.payment.charge.return_value = "txn-001"

        # Act
        receipt = self.service.checkout(
            customer_id="customer-7",
            sku="PYTHON-BOOK",
            quantity=2,
            unit_price_cents=4500,
        )

        # Assert
        self.assertEqual(
            receipt,
            Receipt("PYTHON-BOOK", 2, 9000, "txn-001"),
        )
        self.inventory.reserve.assert_called_once_with("PYTHON-BOOK", 2)
        self.payment.charge.assert_called_once_with("customer-7", 9000)
        self.notifier.send.assert_called_once_with(
            "customer-7",
            "支付成功：9000 分",
        )

    def test_out_of_stock_stops_later_side_effects(self) -> None:
        self.inventory.reserve.return_value = False

        with self.assertRaisesRegex(OutOfStockError, "PYTHON-BOOK"):
            self.service.checkout(
                customer_id="customer-7",
                sku="PYTHON-BOOK",
                quantity=1,
                unit_price_cents=4500,
            )

        # 库存失败后，付款和通知都不应该发生。
        self.payment.charge.assert_not_called()
        self.notifier.send.assert_not_called()

    def test_invalid_quantity_does_not_call_any_dependency(self) -> None:
        with self.assertRaisesRegex(ValueError, "quantity"):
            self.service.checkout(
                customer_id="customer-7",
                sku="PYTHON-BOOK",
                quantity=0,
                unit_price_cents=4500,
            )

        self.inventory.reserve.assert_not_called()
        self.payment.charge.assert_not_called()
        self.notifier.send.assert_not_called()


class PatchExamplesTests(unittest.TestCase):
    """patch 只在 with 块内生效，退出后自动恢复原对象。"""

    def test_patch_function_where_the_code_looks_it_up(self) -> None:
        fake_payload = {"id": 7, "name": "Guido"}

        # __name__ 在直接运行时为 "__main__"，被导入时为模块完整名称；
        # 动态构造目标可让两种运行方式都正确。
        with patch(f"{__name__}.request_json", return_value=fake_payload) as mocked:
            result = load_user_name(7)

        self.assertEqual(result, "Guido")
        mocked.assert_called_once_with("https://example.invalid/users/7")

    def test_patch_object_replaces_a_class_attribute_temporarily(self) -> None:
        with patch.object(TokenFactory, "generate", return_value="fixed-token") as mocked:
            session = create_session(42)

        self.assertEqual(session, {"user_id": 42, "token": "fixed-token"})
        mocked.assert_called_once_with()
        # with 块结束后原方法已经恢复。
        self.assertEqual(TokenFactory.generate(), "real-token")

    def test_patch_side_effect_callable_can_compute_from_arguments(self) -> None:
        def fake_shipping(weight_kg: float) -> int:
            return round(weight_kg * 100)

        with patch(
            f"{__name__}.shipping_fee",
            side_effect=fake_shipping,
        ) as mocked:
            fees = quote_orders([0.5, 2.0, 3.5])

        self.assertEqual(fees, [50, 200, 350])
        self.assertEqual(mocked.call_args_list, [call(0.5), call(2.0), call(3.5)])


class SideEffectExamplesTests(unittest.TestCase):
    """side_effect 可表达“第一次失败、第二次成功”等时间序列。"""

    def test_iterable_side_effect_models_retry_then_success(self) -> None:
        client = Mock(spec=RemoteClient)
        client.fetch.side_effect = [
            TimeoutError("第一次超时"),
            {"value": 42},
        ]

        result = fetch_with_retry(client, "answer", attempts=3)

        self.assertEqual(result, {"value": 42})
        self.assertEqual(client.fetch.call_count, 2)
        self.assertEqual(
            client.fetch.call_args_list,
            [call("answer"), call("answer")],
        )

    def test_exception_side_effect_is_raised_after_all_retries(self) -> None:
        client = Mock(spec=RemoteClient)
        client.fetch.side_effect = TimeoutError("服务不可用")

        with self.assertRaisesRegex(TimeoutError, "服务不可用"):
            fetch_with_retry(client, "answer", attempts=3)

        self.assertEqual(client.fetch.call_count, 3)

    def test_callable_side_effect_can_depend_on_input(self) -> None:
        client = Mock(spec=RemoteClient)
        values = {"one": 1, "two": 2}

        def fake_fetch(key: str) -> dict[str, int]:
            return {"value": values[key]}

        client.fetch.side_effect = fake_fetch

        self.assertEqual(client.fetch("one"), {"value": 1})
        self.assertEqual(client.fetch("two"), {"value": 2})


def main() -> None:
    # unittest.main() 也可用；显式构造 runner 便于在脚本中检查结果并返回非零状态。
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
