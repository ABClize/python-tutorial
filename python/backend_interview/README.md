# 现代 Python 后端面试场景

这个目录是一套可运行的订单 API，用真实项目结构串起 FastAPI、Pydantic v2、
asyncio、分层架构和测试，而不是只展示一个 `@app.get("/")`。

## 运行

```bash
uv sync --group dev
uv run uvicorn backend_interview.main:app --reload
```

打开：

- Swagger UI：`http://127.0.0.1:8000/docs`
- OpenAPI：`http://127.0.0.1:8000/openapi.json`
- 健康检查：`http://127.0.0.1:8000/health`

创建订单：

```bash
curl -X POST http://127.0.0.1:8000/orders \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: development-only-key' \
  -H 'Idempotency-Key: interview-order-001' \
  -d '{
    "customer_email": "learner@example.com",
    "items": [{"sku": "PY-BOOK", "quantity": 2}]
  }'
```

## 代码地图

| 文件 | 面试重点 |
| --- | --- |
| `main.py` | 应用工厂、lifespan、中间件、异常处理 |
| `api.py` | 路由、Header/Query、响应模型、分页 |
| `dependencies.py` | `Annotated + Depends`、认证、`yield` 清理 |
| `schemas.py` | Pydantic v2 字段/模型校验、泛型、判别联合 |
| `domain.py` | 与框架解耦的领域对象和状态转换 |
| `repository.py` | Protocol、原子幂等、乐观锁 |
| `gateways.py` | 外部服务端口和可测试 Fake |
| `service.py` | TaskGroup、超时、并发限制、服务编排 |
| `async_patterns.py` | 限流、重试、first-success、single-flight、队列 |
| `pydantic_patterns.py` | TypeAdapter、RootModel、严格模式、序列化 |
| `QUESTIONS.md` | 60 道项目场景面试追问与答题要点 |


## 学习路径：一次请求经过哪些层？

以 `POST /orders` 为例，可以按下面顺序阅读代码：

1. `main.py::create_app` 在 lifespan 中创建仓储和外部网关，并挂到 `app.state`。
2. 请求先经过 `request_context_middleware`，生成或透传 `X-Request-ID`，方便日志和错误响应串联。
3. `api.py::create_order` 声明请求体、认证依赖和 `Idempotency-Key` 请求头；路由只做 HTTP 适配，不写业务规则。
4. `dependencies.py::get_order_service` 从依赖图中组装服务层所需的仓储、网关和配置。
5. `service.py::OrderService.create_order` 并发调用目录和库存网关，处理超时、上游错误和幂等创建。
6. `repository.py::InMemoryOrderRepository.create` 在锁内完成“查幂等键 + 插入订单”，模拟数据库唯一索引保证的原子性。
7. `schemas.py::OrderResponse.from_domain` 把领域对象转换为稳定的 API 响应模型。

这个项目刻意把“HTTP 边界、业务编排、领域状态、持久化端口、外部服务端口”拆开，
面试时可以说明：分层不是为了显得复杂，而是为了让每一层的失败模式、测试方式和替换成本都更清楚。

## 关键设计说明

### 幂等创建

客户端必须传 `Idempotency-Key`。服务层会先查已有结果，但真正防并发重复创建的是仓储层的原子 `create`：
同一个 key 即使被多个请求同时提交，也只会有一个订单被保存，其他请求拿到第一次保存的结果并返回 `created=false`。
真实系统中通常用数据库唯一索引、事务或 `INSERT ... ON CONFLICT` 实现同样约束。

### 乐观锁状态更新

`PATCH /orders/{order_id}/status` 使用 `If-Match` 请求头传入客户端看到的版本号。
仓储保存前比较当前版本和期望版本：一致才更新并递增版本，不一致返回 409。
这能避免两个调用方基于旧状态互相覆盖。

### asyncio 并发边界

服务层使用 `TaskGroup` 同时请求商品目录、库存或风控；任一子任务失败时，其余任务会被取消，避免“半失败”后继续浪费资源。
`asyncio.timeout` 把上游慢请求统一转换为领域异常，再由 FastAPI 异常处理器映射为 HTTP 504。
批量创建使用 `Semaphore` 控制并发，避免一次请求启动过多任务压垮下游。

### Pydantic 与领域对象分工

`schemas.py` 负责外部输入输出契约，例如字段范围、邮箱格式、判别联合和分页响应。
`domain.py` 负责框架无关的业务状态，例如订单状态流转和金额计算。
不要把需要数据库或网络 I/O 的规则放进 Pydantic validator；那类规则应留在服务层或领域服务里。

### 测试如何对应架构

- API 测试覆盖路由、依赖、异常映射和 OpenAPI 契约。
- 服务测试直接替换仓储和网关，聚焦幂等、超时和并发行为。
- Schema 测试覆盖 Pydantic v2 的合法输入、边界值和错误结构。
- async pattern 测试覆盖可复用并发工具，避免只在端到端测试里碰运气。

## 推荐断点

1. `dependencies.py::require_api_key`：观察依赖树如何注入设置。
2. `service.py::create_order`：观察 TaskGroup 中目录和库存任务。
3. `repository.py::create`：观察幂等键并发竞争为何只能创建一个订单。
4. `repository.py::save`：修改 `If-Match`，观察乐观锁冲突。
5. `main.py::request_context_middleware`：观察请求 ID 的设置与清理。
6. `async_patterns.py::AsyncSingleFlightCache.get_or_create`：观察并发未命中合并。

## 测试

```bash
uv run pytest tests/backend -v
uv run pytest tests/backend --cov=backend_interview --cov-report=term-missing
```

测试覆盖：

- FastAPI `TestClient` 端到端请求；
- HTTPX `AsyncClient + ASGITransport` 异步请求；
- `app.dependency_overrides` 替换认证；
- Pydantic v2 正常、边界和非法输入；
- 服务层幂等、超时、乐观锁和并发；
- asyncio 限流、取消、重试和 single-flight。

## 官方参考

- <https://fastapi.tiangolo.com/tutorial/dependencies/>
- <https://fastapi.tiangolo.com/advanced/testing-dependencies/>
- <https://docs.pydantic.dev/latest/concepts/validators/>
- <https://docs.python.org/3.11/library/asyncio-task.html>
