# FastAPI 分层后端

仓库中的订单 API 不只是几个路由示例。它把 HTTP 协议、输入校验、业务流程、领域规则、数据存取和外部
服务分开放置，正好可以用来观察一个 FastAPI 请求从进入应用到生成响应的完整过程。

<p class="source-note">对应源码：<code>python/backend_interview/</code></p>

## 本章内容

- [启动应用、认识路由与请求参数](./14-fastapi-layered-backend/running-routes-and-requests)
- [依赖注入、应用生命周期与中间件](./14-fastapi-layered-backend/dependencies-and-lifecycle)
- [一次请求如何穿过各层](./14-fastapi-layered-backend/request-flow-and-layers)
- [持久化、幂等与乐观锁](./14-fastapi-layered-backend/persistence-idempotency-and-locking)
- [错误响应、批量接口与 OpenAPI](./14-fastapi-layered-backend/errors-batch-and-openapi)
