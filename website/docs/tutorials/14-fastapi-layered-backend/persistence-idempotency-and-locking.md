# 持久化、幂等与乐观锁

存储可以使用内存、文件或数据库。持久化通常特指把数据写入进程重启后仍能保留的文件或数据库；当前
内存仓储只实现存储接口，不提供这种持久性。幂等表示同一个请求重复执行时，不会重复产生副作用。
乐观锁使用版本号检查数据是否已被其他请求修改。

网络请求可能重发，多个客户端也可能同时写入。只在服务层“先查询、再写入”仍然会出现竞态，最终
检查必须和写入放在同一个原子操作中。

<!-- 对应源码：python/backend_interview/repository.py、python/backend_interview/service.py、python/backend_interview/domain.py -->

## 服务依赖仓储协议

`OrderRepository` 使用 `Protocol` 声明服务层需要的操作：

```python
class OrderRepository(Protocol):
    async def create(
        self,
        order: Order,
        idempotency_key: str,
    ) -> tuple[Order, bool]: ...

    async def get(
        self,
        order_id: UUID,
    ) -> Order | None: ...

    async def save(
        self,
        order: Order,
        expected_version: int,
    ) -> Order: ...
```

服务层只依赖这些行为，不关心数据存在字典、SQL 数据库还是远程存储中。

当前的 `InMemoryOrderRepository` 使用字典保存数据。它适合教学和测试，但进程退出后数据会消失，
多个应用实例之间也不会共享。

## 为什么需要幂等键

假设客户端发出创建订单请求，服务端已经保存成功，但响应在网络中丢失。客户端无法判断结果，只能重发：

```text
第一次请求：订单已保存 ──X── 响应丢失
第二次请求：客户端重新发送相同操作
```

如果每次都生成新订单，就会得到重复数据。客户端为同一次逻辑操作提供稳定的
`Idempotency-Key`，服务端便能识别重放。

相同键再次提交时，项目返回第一次创建的订单，并把：

```json
{
  "created": false
}
```

`created: false` 表示这次请求复用了已有订单，没有再次执行创建操作。

## 服务层提前查询可以减少重复工作

服务先查询已有结果：

```python
async def find_replay(
    repository,
    idempotency_key: str,
):
    existing = (
        await repository.find_by_idempotency_key(
            idempotency_key
        )
    )
    if existing is not None:
        return CreateOrderResult(
            existing,
            created=False,
        )
    return None
```

这能让常见重放少做商品和库存查询，但不能独自保证并发安全：

```text
请求 A 查询：不存在
请求 B 查询：不存在
请求 A 创建
请求 B 创建
```

两个请求完全可能在写入前都看到“不存在”。

## 原子检查必须靠近写入

内存仓储在同一把 `asyncio.Lock` 内完成检查和写入：

```text
获取仓储锁
  ↓
检查幂等键是否已经关联订单
  ↓
不存在才保存订单和键的映射
  ↓
释放仓储锁
```

锁需要同时包住检查和写入。这样其他协程就不能在两步之间插入修改。

真实数据库通常使用：

- 幂等键唯一索引；
- 数据库事务；
- `INSERT ... ON CONFLICT`；
- 原子条件更新。

只在 Python 进程中加锁无法约束其他进程或其他服务器实例。

## 幂等键还要绑定请求内容

完整实现通常会保存请求体摘要：

```text
相同 key + 相同请求内容  -> 返回第一次结果
相同 key + 不同请求内容  -> 拒绝，提示幂等键冲突
```

否则调用方误用旧键发送另一笔订单时，可能收到一个看似成功但内容不匹配的旧结果。当前教学仓储没有
保存请求摘要，这是示例的明确边界。

幂等记录还要考虑保留时间。永久保存会持续占用空间，过早清理又可能让迟到的重试重新产生副作用。

## 乐观锁解决并发更新

订单响应带有 `version`。客户端更新状态时，把读到的整数版本放入自定义请求头
`X-Expected-Version`：

```bash
curl -X PATCH \
  http://127.0.0.1:8000/orders/ORDER_UUID/status \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: development-only-key' \
  -H 'X-Expected-Version: 1' \
  -d '{"status": "confirmed"}'
```

仓储保存前比较版本：

```text
存储中的 version == X-Expected-Version
    是：保存新状态，并把版本加 1
    否：抛出 OptimisticLockError
```

假设 A、B 都读到版本 1：

```text
A 携带 X-Expected-Version: 1，更新成功，版本变成 2
B 仍携带 X-Expected-Version: 1，更新失败，返回 409
```

没有这个比较时，B 会基于旧数据覆盖 A 的更新。

这里没有使用标准 `If-Match`，因为 `If-Match` 应携带服务器通过 `ETag` 返回的实体标签
（entity-tag），例如 `If-Match: "1"`，条件不满足时通常返回 `412 Precondition Failed`。本项目
选择自定义整数版本头，并把版本不匹配作为业务并发冲突返回 409。

## 乐观锁与互斥锁不是一回事

- 互斥锁让同一时刻只有一个执行者进入临界区；
- 乐观锁允许大家先读取，写入时检查数据是否已经变化。

Web 请求可能跨进程、跨机器，无法一直持有一把 Python 锁等待用户提交。版本列配合数据库条件更新更适合
这种场景，例如：

```sql
UPDATE orders
SET status = :status, version = version + 1
WHERE id = :id AND version = :expected_version
```

受影响行数为 0 时，就表示订单不存在或版本冲突。

## 重复设置相同状态

领域对象在目标状态与当前状态相同时返回自身。服务层不会调用 `save()`，版本也不会增加。

这里采用“状态没有变化就不写入”的处理方式。它是否适合真实系统，要看业务是否还需要记录每一次操作
尝试、审计事件或命令 ID，不能仅凭技术习惯决定。

## 仓储写入需要保证什么

应用层可以提前判断以改善错误信息和性能，但最终一致性约束应由持久化层保证：

- 幂等键唯一；
- 版本匹配后才能更新；
- 多项写入要么一起成功，要么一起失败；
- 数据关系不被并发请求破坏。

把这些约束只写在路由或服务的 `if` 中，单请求测试可能通过，一遇到并发或多实例就会失效。
