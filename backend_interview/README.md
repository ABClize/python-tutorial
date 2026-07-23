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
