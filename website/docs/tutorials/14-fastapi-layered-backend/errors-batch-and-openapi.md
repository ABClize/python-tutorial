# 错误响应、批量接口与 OpenAPI

一个接口不仅要定义成功结果，还要定义失败时的状态码和响应结构。批量、分页等接口又会带来并发量和
结果组织问题。FastAPI 可以生成契约，但前提是代码把这些边界明确写出来。

<p class="source-note">对应源码：<code>python/backend_interview/main.py</code>、<code>python/backend_interview/api.py</code>、<code>python/backend_interview/service.py</code></p>

## 在 HTTP 边界统一映射异常

领域层和服务层抛出与 HTTP 无关的应用异常，`main.py` 再转换成状态码：

| 应用异常 | HTTP 状态 | 含义 |
| --- | --- | --- |
| `OrderNotFoundError` | 404 | 订单不存在 |
| `ProductUnavailableError` | 409 | 商品当前不可用 |
| `InsufficientInventoryError` | 409 | 库存不足 |
| `InvalidStatusTransitionError` | 409 | 状态转换不允许 |
| `OptimisticLockError` | 409 | 版本冲突 |
| `UpstreamTimeoutError` | 504 | 上游未按时完成 |
| 其他 `BackendInterviewError` | 400 | 其他应用错误 |

业务错误使用稳定外壳：

```json
{
  "error": {
    "code": "insufficient_inventory",
    "message": "商品 ASYNC-LAB 库存不足：需要 100，可用 20"
  },
  "request_id": "7fd84f5f2be74ee997cf1cb4eb81d737"
}
```

`code` 适合程序判断，`message` 供人阅读，`request_id` 用来关联日志。客户端不应通过匹配中文错误文案
来决定业务分支。

## 422 表示请求没有通过校验

路径、Query、Header 或请求体校验失败时，路径函数尚未执行。项目把
`RequestValidationError` 转成：

```json
{
  "error": {
    "code": "request_validation_error",
    "details": [
      {
        "location": ["body", "items", 0, "quantity"],
        "message": "Input should be greater than 0",
        "type": "greater_than"
      }
    ]
  },
  "request_id": "7fd84f5f2be74ee997cf1cb4eb81d737"
}
```

`location` 指向错误位置，`type` 是相对稳定的机器标识，`message` 是说明。一个请求可以同时返回多个
校验错误，前端可以据此标记对应字段。

400、409 与 422 的区别不是绝对语法规则，而是接口契约的一部分。本项目用 422 表达输入结构校验失败，
用 409 表达请求结构正确但与当前业务状态冲突。

## 分页接口

```bash
curl \
  'http://127.0.0.1:8000/orders?offset=0&limit=20' \
  -H 'X-API-Key: development-only-key'
```

响应使用泛型 `Page[OrderResponse]`：

```json
{
  "items": [],
  "total": 0,
  "offset": 0,
  "limit": 20
}
```

`items` 是当前页，`total` 是符合条件的总数。客户端不能用 `items` 长度替代 `total`，因为最后一页
之前它只表示本页大小。

仓储的列表读取和总数查询互不依赖，服务层用 `asyncio.gather()` 并发等待。真实数据库还要保证排序
稳定，否则翻页期间新增数据可能造成重复或遗漏。

## 批量创建与并发上限

`POST /orders/bulk` 接受 1 到 20 个条目。服务层不是无限制地同时创建，而是让每个任务先获取
Semaphore：

```python
async def create_bounded(command, key):
    async with self._bulk_semaphore:
        return await self.create_order(command, key)
```

这能控制一次批量请求内部的在途数量，但当前依赖会为每个 HTTP 请求创建一个 `OrderService`，所以
Semaphore 不是全进程限流器。两个批量请求仍各自拥有一份上限。

批量接口还应明确失败语义：

- 任一项失败，整批取消；
- 成功项保留，逐项返回结果；
- 整批放进事务；
- 接受任务后异步处理。

本项目使用 TaskGroup 的“兄弟任务共同成功”语义。业务要求不同，响应模型和持久化方式也要一起改变。

## 摘要接口中的并发

`GET /orders/{order_id}/summary` 先读取订单，再并发执行风控评估和商品标签查询：

```json
{
  "order": {},
  "risk_level": "low",
  "product_labels": {
    "PY-BOOK": "Python Interview Book"
  }
}
```

这里的 `order` 实际是完整的 `OrderResponse`，示例省略字段只是为了突出摘要新增内容。两个查询只有在
都依赖订单、彼此不依赖时才适合并发。

## OpenAPI 从代码中生成什么

FastAPI 会把这些信息写入 `/openapi.json`：

- 路径、HTTP 方法与 tags；
- 路径、Query、Header 和请求体参数；
- Pydantic 生成的 JSON Schema；
- `response_model` 和成功状态码；
- 参数是否必填、默认值和范围。

Swagger UI 读取 OpenAPI，再生成可交互页面。它不是另一份独立文档，因此模型约束和路由声明变化后，
页面也会跟着变化。

修改接口时，应检查：

1. 必填字段、默认值和范围是否准确；
2. Header、Query 和路径参数名称是否正确；
3. 实际返回值是否符合 `response_model`；
4. 错误响应是否有稳定结构；
5. 字段删除、改名或类型变化是否破坏调用方。

## 当前认证在文档中的限制

订单路由通过普通 `Depends(require_api_key)` 校验 API Key，而不是 FastAPI 的安全方案对象。因此
OpenAPI 不会自动生成可点击的授权按钮或 `securitySchemes`。

接口“确实执行了认证”与“OpenAPI 正确描述认证”是两个不同问题。面向外部调用方的生产 API，应使用
合适的安全依赖并检查生成契约。

## 分层应用的检查清单

- 路由只做协议适配，不承载完整业务流程；
- validator 不执行数据库和网络 I/O；
- `async def` 内部使用非阻塞依赖；
- 进程资源放 lifespan，请求资源放 `yield` 依赖；
- 业务异常在 API 边界映射，不把 `HTTPException` 传入领域层；
- 幂等和版本约束由持久化原子操作保证；
- `response_model` 与真实返回保持一致；
- 测试应用时让 lifespan 真正进入和退出。

这些约束共同决定接口是否容易理解和维护，不是目录数量越多就越“分层”。
