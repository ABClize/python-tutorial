# FastAPI 分层后端

这一章把前面的类型、异常、依赖注入、asyncio 和测试放进一个可运行订单 API。重点不是记住
FastAPI 装饰器，而是看清一次请求如何穿过 HTTP 边界、服务编排、领域模型和持久化端口。

<p class="source-note">对应源码：<code>python/backend_interview/</code></p>

## 一次创建订单请求

<div class="concept-map">
  <div class="concept-step"><small>HTTP 边界</small><strong>api.py</strong><code>POST /orders</code></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>依赖组装</small><strong>dependencies.py</strong></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>用例编排</small><strong>service.py</strong></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>业务状态</small><strong>domain.py</strong></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>持久化端口</small><strong>repository.py</strong></div>
</div>

每层只处理自己的变化来源：

- 路由适配 Header、Query、请求体和状态码；
- 依赖层从应用状态组装仓储、网关和配置；
- 服务层协调多个组件完成一个用例；
- 领域层维护订单状态和金额不变量；
- 仓储负责保存、查询和并发一致性。

## 应用工厂是组合根

`main.py::create_app()` 创建 FastAPI 应用。lifespan 在进程启动时构造仓储和外部网关，结束时关闭
资源；这里是运行时依赖图的组合根。

```python
@asynccontextmanager
async def lifespan(application: FastAPI):
    repository = InMemoryOrderRepository()
    application.state.order_repository = repository
    try:
        yield
    finally:
        await repository.close()
```

资源创建放在启动边界，而不是每个请求里临时创建。请求级依赖可以使用 `yield`，在响应完成后释放
连接或事务。

## 依赖注入是一棵请求图

FastAPI 会根据函数签名解析 `Depends`，缓存同一请求中的依赖结果，并把验证后的 Header、Query
和 Path 参数传入。依赖可以继续依赖其他依赖，因此认证、配置和服务组装形成一棵图。

`yield` 依赖适合事务、会话和临时资源。`yield` 前是获取，`finally` 是释放；资源范围必须与响应
生命周期匹配，尤其要注意 StreamingResponse 和后台任务何时真正完成。

测试可以通过 `app.dependency_overrides` 替换图中的某个节点，不必 patch FastAPI 内部实现。

## 中间件与 ContextVar

示例中间件读取或生成 `X-Request-ID`，同时写入 response header 和 ContextVar。请求处理链中的
日志即使没有显式接收 Request，也能附加关联 ID。

中间件适合跨全部路由的传输层行为，例如追踪、CORS 和统一计时；业务授权和资源查找通常更适合
依赖。中间件顺序会影响异常、响应头和性能，不能把所有逻辑都塞进一条全局链。

## Schema 与领域对象分工

Pydantic Schema 负责外部契约：

- 字段类型、长度和范围；
- JSON 解析与序列化；
- API 错误位置；
- OpenAPI 文档。

领域对象负责业务语义：

- 状态能否转换；
- 金额如何计算；
- 对象创建时必须成立的不变量；
- 与 HTTP、数据库实现无关的行为。

不要在 Pydantic validator 中访问数据库或网络。需要 I/O 的校验属于服务层编排，否则模型构造会
变成隐藏的异步副作用。

`response_model` 还承担输出过滤和 OpenAPI 契约。不要直接返回 ORM 或领域对象的全部字段，避免
内部状态、密钥或未来新增字段意外泄露。

## 服务层编排并发

创建订单需要同时查询商品和确认库存。`TaskGroup` 表达“这些子任务属于同一个操作”：

```python
async with asyncio.timeout(self.timeout_seconds):
    async with asyncio.TaskGroup() as group:
        product_task = group.create_task(catalog.get_product(sku))
        group.create_task(inventory.ensure_available(sku, quantity))
```

兄弟任务失败时，任务组取消其余任务并等待清理。外层 timeout 把总等待限制在业务预算内，服务层
再把超时转换为稳定领域异常。

批量接口还使用 Semaphore 限制扇出，避免一个请求瞬间创建无限 Task 压垮下游。

## 请求、事务与外部副作用

真实下单可能同时写数据库、扣库存和发消息，单个数据库事务无法原子覆盖远程系统。常见设计包括：

- 先在本地事务中保存订单和 outbox，再异步发布事件；
- 外部调用带幂等 key，允许安全重试；
- 失败后执行补偿，而不是假装存在跨服务 ACID；
- 用状态机表达 pending、confirmed、failed 等中间状态。

路由返回 200 不等于所有异步副作用都已完成。接口契约应明确同步完成到哪一步、后续状态如何查询。

## 幂等需要原子边界

服务层先查询幂等 key 只能优化普通重试，不能解决两个请求同时到达的竞争：

```text
请求 A：查询不存在 ─┐
                    ├─ 两边都准备创建
请求 B：查询不存在 ─┘
```

真正约束必须位于仓储或数据库原子边界。示例仓储在锁内完成“查 key + 插入”；生产数据库通常使用
唯一索引、事务或 `INSERT ... ON CONFLICT`。

## 乐观锁防止丢失更新

客户端通过 `If-Match` 提交自己读到的版本。仓储保存前比较期望版本和当前版本：

- 相等：保存并把版本加一；
- 不相等：返回冲突，让调用方重新读取和决策。

它适合冲突较少、读取频繁的状态更新。高冲突场景可能需要悲观锁、队列串行化或重新设计所有权。

## 异常只在边界映射为 HTTP

服务和领域抛出 `OrderNotFoundError`、`OptimisticLockError` 等稳定异常；FastAPI 异常处理器统一
映射为 404、409、504 和错误 envelope。

这样领域层可以被 CLI、worker 或测试直接复用，不需要知道 `HTTPException`。

## 认证、授权与输入信任边界

认证回答“调用者是谁”，授权回答“他能否操作这个资源”。示例 API key 只用于教学，生产系统还需
密钥轮换、HTTPS、最小权限和审计。

即使 Pydantic 已验证字段形状，调用者仍可能无权访问某个 order_id；即使客户端隐藏某按钮，服务端
也必须重新授权。日志中不要记录 SecretStr 原值、完整 token、支付信息或个人敏感数据。

## OpenAPI 是公开契约的一部分

路由状态码、请求/响应模型、错误 envelope、分页规则和 Header 都会影响客户端。修改字段含义或把
可选字段变成必填，可能是破坏性变更。可以通过契约测试或保存的 schema diff 检查无意变化。

## 测试如何对应分层

| 测试位置 | 验证内容 |
| --- | --- |
| `tests/backend/test_schemas.py` | 输入校验和错误结构 |
| `test_service.py` | 幂等、超时、并发编排 |
| `test_api.py` | 路由、认证、状态码、异常映射 |
| `test_async_api.py` | 完整异步 ASGI 请求 |
| `test_async_patterns.py` | 重试、限流、single-flight |

FastAPI 的 `dependency_overrides` 用于替换认证等请求依赖；服务测试则直接注入 Fake 仓储和网关。

## 如何运行和阅读

在 `python/` 目录执行：

```bash
uv sync --group dev
uv run uvicorn backend_interview.main:app --reload
```

然后打开 `http://127.0.0.1:8000/docs`。建议依次阅读：

1. `main.py`：应用和资源如何启动；
2. `api.py`：HTTP 契约；
3. `dependencies.py`：对象如何组装；
4. `service.py`：用例与并发；
5. `domain.py`：业务不变量；
6. `repository.py`：一致性边界。

交互文档会根据路由签名和 Pydantic Schema 生成请求表单。也可以直接用 curl 发送一笔完整请求：

```bash
curl -i http://127.0.0.1:8000/orders \
  -X POST \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: development-only-key' \
  -H 'Idempotency-Key: tutorial-order-001' \
  -d '{
    "customer_email": "learner@example.com",
    "items": [{"sku": "PY-BOOK", "quantity": 1}]
  }'
```

第一次成功创建返回 `201 Created`。响应中的 `created` 表示这次是否真正创建；用相同
`Idempotency-Key` 重试时会返回已有订单，帮助读者把“HTTP 请求”“幂等协议”和前面的仓储原子
边界联系起来。

如果得到 `401`，先检查 `X-API-Key`；如果得到 `422`，查看错误中的字段位置和约束；如果得到
`409`，通常是库存、商品或状态冲突。按状态码回到对应层定位，比从所有文件里搜索错误字符串更快。

## 常见误区

### 分层就是每层只转发参数

如果某层没有独立变化原因或契约，只是机械转发，就可能是无效抽象。示例中的每层都对应不同的失败
模式和测试方式。

### 服务层返回 HTTPException 最方便

这会让业务用例绑定 FastAPI。领域异常应在传输边界统一映射。

### 先查幂等 key 就不会重复

查询与写入之间存在竞态。最终一致性约束必须落在原子仓储操作或数据库唯一约束。

## 面试时怎么表述

> 路由层负责 HTTP 适配，服务层编排用例，领域层维护业务不变量，仓储和网关通过 Protocol 隔离
> 外部系统。应用工厂是组合根，领域异常在 API 边界映射为状态码。幂等和乐观锁的最终约束落在
> 原子持久化边界，并发 I/O 用 TaskGroup、timeout 和 Semaphore 控制生命周期与压力。
