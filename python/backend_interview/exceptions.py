"""Domain and application exceptions independent of HTTP."""


class BackendInterviewError(Exception):
    """Base class for errors that can be translated at the API boundary."""

    code = "backend_error"


class OrderNotFoundError(BackendInterviewError):
    code = "order_not_found"

    def __init__(self, order_id: str) -> None:
        super().__init__(f"订单 {order_id} 不存在")


class ProductUnavailableError(BackendInterviewError):
    code = "product_unavailable"

    def __init__(self, sku: str) -> None:
        super().__init__(f"商品 {sku} 不存在或不可售")


class InsufficientInventoryError(BackendInterviewError):
    code = "insufficient_inventory"

    def __init__(self, sku: str, requested: int, available: int) -> None:
        super().__init__(f"商品 {sku} 库存不足：需要 {requested}，可用 {available}")


class InvalidStatusTransitionError(BackendInterviewError):
    code = "invalid_status_transition"

    def __init__(self, current: str, target: str) -> None:
        super().__init__(f"订单状态不能从 {current} 变更为 {target}")


class OptimisticLockError(BackendInterviewError):
    code = "optimistic_lock_conflict"

    def __init__(self, expected: int, actual: int) -> None:
        super().__init__(f"版本冲突：期望 {expected}，实际 {actual}")


class UpstreamTimeoutError(BackendInterviewError):
    code = "upstream_timeout"

    def __init__(self) -> None:
        super().__init__("上游服务调用超时")
