# 一次请求如何穿过各层

分层是把不同职责放到不同模块。API 层处理 HTTP，Schema 处理输入输出结构，服务层组织业务步骤，
领域对象保存业务规则，仓储负责数据存取，网关负责调用外部系统。

创建订单时，请求依次经过这些模块。每一层只处理自己的工作，再把结果交给下一层。

<!-- 对应源码：python/backend_interview/api.py、python/backend_interview/schemas.py、python/backend_interview/service.py、python/backend_interview/domain.py -->

## 创建订单的执行顺序

一次 `POST /orders` 大致经过：

```text
main.py
  中间件建立 request_id
        ↓
api.py
  读取 Header 和请求体，执行认证依赖
        ↓
schemas.py
  校验邮箱、SKU、数量和列表长度
        ↓
dependencies.py
  从 app.state 取得仓储和网关，组装 OrderService
        ↓
service.py
  查找幂等结果，并发查询商品和库存
        ↓
domain.py
  创建 OrderItem 和 Order，计算金额与初始状态
        ↓
repository.py
  原子检查幂等键并保存
        ↓
schemas.py
  把领域对象转换成响应模型
        ↓
main.py
  添加响应头，或把异常映射成 HTTP 响应
```

每一层都只处理自己理解的概念。

## API 层只做协议适配

路由函数很短：

```python
async def create_order(
    command: CreateOrderRequest,
    service: ServiceDep,
    idempotency_key: str,
) -> CreateOrderResponse:
    result = await service.create_order(
        command,
        idempotency_key,
    )
    return CreateOrderResponse(
        order=OrderResponse.from_domain(result.order),
        created=result.created,
    )
```

它负责把 HTTP 输入交给服务，再把服务结果转换为 HTTP 响应模型。库存检查、价格计算和数据保存都不在
这里。

如果把整个流程写进路径函数，会出现几个问题：

- 不启动 Web 应用就很难调用业务流程；
- HTTPException 和业务规则混在一起；
- 后台任务或 CLI 想复用下单逻辑时只能复制代码；
- 单元测试必须构造大量 HTTP 上下文。

## Schema 只检查当前输入

`CreateOrderRequest` 能检查外部数据的形状：

```python
class CreateOrderRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    customer_email: EmailStr
    items: Annotated[
        list[CreateOrderItem],
        Field(min_length=1, max_length=20),
    ]
```

它可以判断：

- 邮箱格式是否有效；
- 商品列表是否为空或过长；
- 数量是否在允许范围；
- 同一 SKU 是否重复；
- 是否夹带未知字段。

它不能判断商品是否存在、库存是否充足，因为这些答案不在请求体中，需要访问外部状态。Pydantic
validator 不应发数据库或网络请求。

## 服务层编排一个用例

`OrderService.create_order()` 把多个能力组合为一个完整动作：

1. 查找相同幂等键是否已有订单；
2. 在超时范围内启动一个 `TaskGroup`；
3. 为每个商品查询目录并检查库存；
4. 把查询结果转换成领域 `OrderItem`；
5. 调用 `Order.create()` 建立候选订单；
6. 交给仓储执行原子幂等创建；
7. 返回订单和 `created` 标记。

商品目录查询与库存检查互不依赖，所以可以并发：

```python
async with asyncio.timeout(self.timeout_seconds):
    async with asyncio.TaskGroup() as task_group:
        for item in command.items:
            product_tasks[item.sku] = (
                task_group.create_task(
                    self.catalog.get_product(item.sku)
                )
            )
            task_group.create_task(
                self.inventory.ensure_available(
                    item.sku,
                    item.quantity,
                )
            )
```

任一任务失败，TaskGroup 会取消尚未完成的兄弟任务。整体等待超过配置值，则服务层转换成
`UpstreamTimeoutError`。

服务层知道“下单需要哪些步骤”，但不知道 API 路径、Header 名称和 HTTP 状态码。

## 领域对象保存业务规则

订单不是随意拼起来的字典：

```python
@dataclass(frozen=True, slots=True)
class Order:
    id: UUID
    customer_email: str
    items: tuple[OrderItem, ...]
    status: OrderStatus
    created_at: datetime
    version: int
```

`Order.create()` 决定新订单的 UUID、UTC 创建时间、初始状态 `pending` 和版本 1。`total` 根据每个
订单项的 `subtotal` 计算。

状态转换也属于订单本身：

```text
pending   ──> confirmed
pending   ──> cancelled
confirmed ──> cancelled
cancelled ──> 不允许继续转换
```

请求模型可以检查 `"confirmed"` 是合法枚举值，却无法只凭输入判断当前订单是否允许转到该状态。这个
规则需要读取订单当前状态，因此放在 `Order.transition_to()`。

## 仓储和网关隔离外部系统

服务层依赖抽象能力：

- `OrderRepository` 保存和查询订单；
- `CatalogGateway` 查询商品；
- `InventoryGateway` 检查库存；
- `RiskGateway` 评估风险。

当前仓库提供内存仓储和确定性的 Fake 网关，所以示例无需数据库或真实远程服务就能运行。以后替换成
PostgreSQL 或 HTTP Client 时，服务层的用例流程不需要随之重写。

## 响应模型不是领域对象

`OrderResponse.from_domain()` 显式转换领域对象：

```python
@classmethod
def from_domain(cls, order: Order) -> "OrderResponse":
    payload = {
        "id": order.id,
        "customer_email": order.customer_email,
        "items": order.items,
        "status": order.status,
        "created_at": order.created_at.isoformat(),
        "version": order.version,
        "total": order.total,
    }
    return cls.model_validate(payload)
```

显式映射看起来比直接返回对象多几行，却能清楚决定：

- 哪些字段允许公开；
- 字段是否重命名；
- 时间、金额如何表示；
- 内部模型变化是否影响 API。

领域对象不需要为了 JSON 格式而改变，API 也不会意外暴露内部字段。

## 如何判断是否值得单独分层

一层值得存在，通常因为它有独立的输入、规则或失败方式：

| 层 | 主要关心的问题 |
| --- | --- |
| API | 路径、Header、状态码、响应模型 |
| Schema | 外部数据的类型、格式和局部关系 |
| Service | 一个用例要按什么顺序协调哪些能力 |
| Domain | 业务状态、计算和合法转换 |
| Repository / Gateway | 数据库与外部系统的交互 |

如果两个文件只是转发参数，没有独立语义，继续拆分不会自动让架构更好。分层应减少耦合，而不是追求
目录形式。
