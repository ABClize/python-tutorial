# 依赖注入、应用生命周期与中间件

一个路由通常需要配置、数据库仓储、外部服务客户端和认证信息。如果路径函数自己创建这些对象，资源
生命周期会混乱，测试也难以替换。FastAPI 的依赖系统负责“当前请求需要什么”，lifespan 负责“应用
进程启动和关闭时要做什么”。

<p class="source-note">对应源码：<code>python/backend_interview/dependencies.py</code>、<code>python/backend_interview/main.py</code></p>

## 路由器上的公共依赖

订单接口通过 `APIRouter` 共享前缀、文档标签和依赖：

```python
router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    dependencies=[
        Depends(require_api_key),
        Depends(audit_request),
    ],
)
```

因此 `/orders` 下的每个接口都会先校验 API Key，并执行审计依赖。没有必要在七个路径函数中重复写
相同参数。

项目中的 `require_api_key()` 从请求头读取 `X-API-Key`：

```python
async def require_api_key(
    settings: SettingsDep,
    x_api_key: Annotated[
        str | None,
        Header(alias="X-API-Key"),
    ] = None,
) -> Principal:
    if x_api_key != settings.api_key.get_secret_value():
        raise HTTPException(status_code=401, detail="无效的 API Key")
    return Principal(...)
```

这是便于运行示例的认证方式。生产系统还需要安全的密钥管理、常量时间比较、密钥轮换和更完整的身份
授权方案。

## `Depends` 会递归解析

依赖不是简单调用一个辅助函数。FastAPI 会继续查看依赖函数本身还需要哪些参数。

仓库先声明配置和仓储的类型别名：

```python
SettingsDep = Annotated[
    Settings,
    Depends(get_app_settings),
]
RepositoryDep = Annotated[
    OrderRepository,
    Depends(get_repository),
]
```

服务依赖又使用这两个依赖：

```python
def get_order_service(
    request: Request,
    settings: SettingsDep,
    repository: RepositoryDep,
) -> OrderService:
    return OrderService(
        repository=repository,
        catalog=request.app.state.catalog_gateway,
        inventory=request.app.state.inventory_gateway,
        risk=request.app.state.risk_gateway,
        timeout_seconds=settings.request_timeout_seconds,
        max_concurrency=settings.max_concurrency,
    )


ServiceDep = Annotated[
    OrderService,
    Depends(get_order_service),
]
```

当路径函数声明 `service: ServiceDep` 时，解析关系是：

```text
get_app_settings ─┐
                  ├──> get_order_service ───> 路径函数
get_repository ───┘
app.state 中的 gateways ────────────────────┘
```

同一请求中，同一个依赖默认会缓存结果。依赖函数适合读取配置、认证、组装服务和管理请求级资源，不应
承载完整的下单流程。

## `yield` 依赖管理一次请求

`audit_request()` 在路径函数前后各记录一次：

```python
async def audit_request(
    request: Request,
) -> AsyncIterator[None]:
    path = request.url.path
    request.app.state.audit_log.append(("start", path))
    try:
        yield
    finally:
        request.app.state.audit_log.append(("finish", path))
```

执行顺序如下：

```text
执行 yield 之前的代码
        ↓
路径函数和后续响应处理
        ↓
执行 finally 中的清理
```

数据库会话、临时文件和请求级锁也可以采用这种结构。`finally` 很重要，因为路径函数抛错时资源仍要
释放。

## lifespan 管理整个应用

`create_app()` 为 FastAPI 配置 lifespan：

```python
@asynccontextmanager
async def lifespan(application: FastAPI):
    repository = InMemoryOrderRepository()
    application.state.order_repository = repository
    application.state.catalog_gateway = FakeCatalogGateway()
    application.state.inventory_gateway = FakeInventoryGateway()
    application.state.risk_gateway = FakeRiskGateway()
    application.state.audit_log = []
    try:
        yield
    finally:
        await repository.close()
```

`yield` 之前只在应用启动时执行一次，`yield` 之后在应用关闭时执行一次。真实项目常在这里创建和关闭：

- 数据库连接池；
- 共享 HTTP Client；
- 消息系统连接；
- 需要预加载的模型或索引。

两种生命周期不能混淆：

| 机制 | 范围 | 典型资源 |
| --- | --- | --- |
| lifespan | 应用进程 | 连接池、共享客户端 |
| `yield` 依赖 | 一次请求 | 数据库会话、请求审计 |

## 应用工厂为什么有用

模块最后创建默认应用：

```python
app = create_app()
```

但 `create_app(settings)` 允许调用者传入另一套设置。测试可以得到一个全新的应用实例，而不用修改全局
配置；部署代码也能在创建应用之前决定配置来源。

应用工厂的价值不是“多写一层函数”，而是把应用组装集中在一个明确入口。

## 中间件包围整个请求

中间件接收请求和 `call_next`，可以在请求前后执行通用逻辑：

```python
@application.middleware("http")
async def request_context_middleware(request, call_next):
    request_id = (
        request.headers.get("X-Request-ID")
        or uuid4().hex
    )
    request.state.request_id = request_id
    token = request_id_context.set(request_id)
    started = perf_counter()
    try:
        response = await call_next(request)
    finally:
        request_id_context.reset(token)

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = (
        f"{perf_counter() - started:.6f}"
    )
    return response
```

这里的请求 ID 有两个保存位置：

- `request.state`：显式取得 `Request` 的代码可以读取；
- `ContextVar`：没有逐层传递 `Request` 的深层代码也能关联当前异步上下文。

`ContextVar.reset(token)` 放在 `finally` 中，防止本次请求的值泄漏到后续请求。

## 三个扩展点怎样选择

可以用一个简单判断来区分：

- 所有请求都要执行，并且需要包围后续处理：中间件；
- 某组路由需要对象、认证或请求级资源：依赖；
- 整个进程共用，而且要在关闭时释放：lifespan。

把所有事情都塞进中间件会丢失清晰的依赖关系；把连接池放进请求依赖又会反复创建昂贵资源。选择范围
与资源真实生命周期一致，代码才容易推理。
