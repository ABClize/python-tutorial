# 启动应用、认识路由与请求参数

路由把“HTTP 方法和 URL 路径”对应到一个 Python 函数。例如，`POST /orders` 会调用创建订单的
路径函数。FastAPI 会把路径参数、查询参数、请求头和 JSON 请求体转换成函数参数，并把返回值转换成
HTTP 响应。

HTTP 是客户端与服务器交换请求和响应的协议。JSON 是表示对象、数组、字符串、数字、布尔值和
`null` 的文本格式。

<!-- 对应源码：python/backend_interview/main.py、python/backend_interview/api.py -->

## 启动订单 API

在仓库根目录执行：

```bash
cd python
uv sync --group dev
uv run uvicorn backend_interview.main:app --reload
```

ASGI 是 Python Web 服务器与异步 Web 应用之间的调用规范。`backend_interview.main:app` 的含义是：
导入 `backend_interview/main.py`，找到其中名为 `app` 的 ASGI 应用。`--reload` 会在源码变化时重启
开发服务器，只适合本地开发。

启动后可以访问：

| 地址 | 用途 |
| --- | --- |
| `http://127.0.0.1:8000/health` | 检查应用是否正常启动 |
| `http://127.0.0.1:8000/docs` | 在 Swagger UI 中查看和调用接口 |
| `http://127.0.0.1:8000/openapi.json` | 查看机器可读的 OpenAPI 文档 |

```bash
curl http://127.0.0.1:8000/health
```

```json
{
  "status": "ok",
  "environment": "development"
}
```

`/health` 是系统接口，不要求 API Key；`/orders` 下的接口都要携带
`X-API-Key: development-only-key`。

## 一个最小的请求体路由

下面的例子包含 FastAPI 路由最核心的三个部分：

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class CreateItemRequest(BaseModel):
    name: str
    quantity: int = Field(gt=0)


@app.post("/items")
async def create_item(command: CreateItemRequest) -> dict[str, object]:
    return {
        "name": command.name,
        "quantity": command.quantity,
    }
```

- `@app.post("/items")` 把函数注册为 `POST /items`；
- `command: CreateItemRequest` 表示请求体应按这个 Pydantic 模型校验；
- 函数返回的字典会被序列化为 JSON。

发送下面的请求体：

```json
{
  "name": "Python Book",
  "quantity": 2
}
```

FastAPI 会依次读取 JSON、创建 `CreateItemRequest`、调用路径函数，再把返回值写入响应。若
`quantity` 是 `0`，校验会在路径函数执行之前失败。

## 项目中有哪些路由

订单路由器统一使用 `/orders` 前缀：

| 方法与路径 | 用途 | 主要输入 |
| --- | --- | --- |
| `POST /orders` | 创建一个订单 | JSON、`Idempotency-Key` |
| `POST /orders/bulk` | 批量创建订单 | 批量 JSON |
| `POST /orders/payment/validate` | 校验支付方式结构 | 判别联合 JSON |
| `GET /orders` | 分页查询订单 | `offset`、`limit` |
| `GET /orders/{order_id}` | 查询一个订单 | UUID 路径参数 |
| `PATCH /orders/{order_id}/status` | 修改订单状态 | JSON、`If-Match` |
| `GET /orders/{order_id}/summary` | 查询订单与风控摘要 | UUID 路径参数 |

大括号包围的是路径参数。访问 `/orders/abc` 时，FastAPI 会尝试把 `abc` 转成路由声明的 UUID；转换
失败会直接返回 422。

## 参数是怎样找到的

创建订单的函数签名包含三种输入：

```python
async def create_order(
    command: CreateOrderRequest,
    service: ServiceDep,
    idempotency_key: Annotated[
        str,
        Header(
            alias="Idempotency-Key",
            min_length=8,
            max_length=64,
        ),
    ],
) -> CreateOrderResponse:
    ...
```

| 参数 | FastAPI 从哪里取得 |
| --- | --- |
| `command` | JSON 请求体 |
| `service` | `Depends` 依赖图 |
| `idempotency_key` | `Idempotency-Key` 请求头 |

分页参数则显式标记为 Query：

```python
offset: Annotated[int, Query(ge=0)] = 0
limit: Annotated[int, Query(ge=1, le=100)] = 20
```

请求 `GET /orders?offset=20&limit=10` 时，两个字符串会被转换成整数。`offset=-1`、`limit=0` 或
`limit=500` 都无法通过约束。

## 调用创建订单接口

下面使用 curl 发送包含请求头和 JSON 请求体的创建请求：

```bash
curl -X POST http://127.0.0.1:8000/orders \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: development-only-key' \
  -H 'Idempotency-Key: tutorial-order-001' \
  -d '{
    "customer_email": "learner@example.com",
    "items": [
      {"sku": "PY-BOOK", "quantity": 2}
    ]
  }'
```

成功时返回 `201 Created`：

```json
{
  "order": {
    "id": "3bbf3c2c-58b3-4aa5-b3b4-1827f9b6d1bf",
    "customer_email": "learner@example.com",
    "items": [
      {
        "sku": "PY-BOOK",
        "product_name": "Python Interview Book",
        "quantity": 2,
        "unit_price": "59.90",
        "subtotal": "119.80"
      }
    ],
    "status": "pending",
    "created_at": "2026-07-30T08:00:00+00:00",
    "version": 1,
    "total": "119.80"
  },
  "created": true
}
```

`id` 和 `created_at` 每次创建时生成，实际值不会与示例相同。

## `response_model` 是输出契约

项目的创建路由声明了响应模型和成功状态：

```python
@router.post(
    "",
    response_model=CreateOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    command: CreateOrderRequest,
    service: ServiceDep,
) -> CreateOrderResponse:
    ...
```

`response_model` 有三项作用：

1. 生成响应的 JSON Schema；
2. 按模型序列化并过滤输出；
3. 检查服务端返回值是否符合声明。

它不是给编辑器看的装饰。如果实现返回了错误形状，说明服务端违反了自己的契约，FastAPI 不会把未知
数据不加检查地交给客户端。

## `def` 还是 `async def`

路径函数可以使用两种形式：

- 内部要等待异步数据库驱动、异步 HTTP Client 等 awaitable 时，使用 `async def`；
- 调用的是阻塞库且暂时无法替换时，可以使用普通 `def`，由 FastAPI 放进线程池。

把阻塞 I/O 直接写进 `async def` 会堵住事件循环。函数写了 `async`，并不代表内部调用就自动变成非阻塞。
