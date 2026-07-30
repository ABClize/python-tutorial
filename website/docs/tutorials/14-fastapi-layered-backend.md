# FastAPI 分层后端

FastAPI 是用于编写 HTTP API 的 Python Web 框架。仓库中的订单 API 把路由、输入模型、业务服务、
领域对象、数据仓储和外部服务分别放在不同模块中。本章按一次请求的执行顺序介绍这些代码。

<!-- 对应源码：python/backend_interview/ -->

## 本章内容

- [启动应用、认识路由与请求参数](./14-fastapi-layered-backend/running-routes-and-requests)：
  启动服务，调用接口，并区分路径、查询、请求头和请求体参数。
- [依赖注入、应用生命周期与中间件](./14-fastapi-layered-backend/dependencies-and-lifecycle)：
  使用 `Depends` 提供对象，并管理请求级和应用级资源。
- [一次请求如何穿过各层](./14-fastapi-layered-backend/request-flow-and-layers)：
  查看 API、请求与响应模型、服务、领域、仓储和网关分别处理什么。
- [持久化、幂等与乐观锁](./14-fastapi-layered-backend/persistence-idempotency-and-locking)：
  防止重复创建和并发更新覆盖数据。
- [错误响应、批量接口与 OpenAPI](./14-fastapi-layered-backend/errors-batch-and-openapi)：
  统一错误结构，限制批量并发，并生成接口文档。
