# Single-flight、竞争请求与任务组

Single-flight 会把相同键的并发请求合并成一次实际加载。竞争请求会同时调用多个等价来源，只保留
第一个成功结果。`TaskGroup` 适合组织一组需要共同成功的子任务。

三种方式处理的不是同一种问题。混用会产生重复流量、遗漏错误或错误取消。

<p class="source-note">对应源码：<code>python/backend_interview/async_patterns.py</code>、<code>python/backend_interview/service.py</code></p>

## 缓存未命中的惊群

普通缓存到期时，许多请求可能同时发现未命中：

```text
请求 A：未命中 -> 调用下游
请求 B：未命中 -> 调用下游
请求 C：未命中 -> 调用下游
```

如果 key 相同，三次加载做的是重复工作。single-flight 让同一个 key 同时只有一个加载者：

```text
请求 A：获取 key 对应的锁并加载
请求 B：等待同一把锁
请求 A：写入缓存并释放锁
请求 B：锁内再次检查，直接读取缓存
```

不同 key 使用不同锁，仍然可以并发加载。

## 锁内为什么必须再次检查

仓库先做无锁快速读取，未命中再获取 key 对应的锁：

```python
async def load_under_key_lock(
    self,
    key,
    factory,
):
    lock = await self._lock_for(key)

    async with lock:
        cached = self._fresh_value(key)
        if cached is not None:
            return cached

        value = await factory()
        self._entries[key] = CacheEntry(
            value=value,
            expires_at=(
                self.clock()
                + self.ttl_seconds
            ),
        )
        return value
```

请求 B 在锁外看到未命中后，可能等待了很久。等它获得锁时，请求 A 已经填充缓存。若省略第二次检查，
B 仍会重复调用 factory。

这种结构称为双重检查，但正确性来自“第二次检查发生在同一把 key 锁内”。

## 当前缓存实现还缺少什么

`AsyncSingleFlightCache` 适合展示核心逻辑，但有这些限制：

- `None` 表示未命中，所以不能有效缓存 `None`；
- 每个新 key 的锁会保留，key 空间无限时字典增长；
- factory 失败时不缓存失败，等待者之后会依次重新加载；
- TTL 只在读取时判断，没有后台清理；
- 缓存只在当前进程生效，多实例不共享。

是否需要负缓存、锁清理和分布式协调，要由值类型、key 数量和部署方式决定。

## 多个等价来源竞争成功结果

当几个来源语义相同，可以同时发起并返回第一个成功结果。仓库的 `first_success()`：

```python
async def first_success(operations):
    tasks = [
        asyncio.ensure_future(operation)
        for operation in operations
    ]
    if not tasks:
        raise ValueError("至少需要一个操作")

    errors = []
    try:
        for completed in asyncio.as_completed(
            tasks
        ):
            try:
                return await completed
            except Exception as error:
                errors.append(error)
        raise ExceptionGroup(
            "所有操作都失败",
            errors,
        )
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )
```

执行过程是：

1. 同时安排所有来源；
2. 按完成顺序读取结果；
3. 一个来源失败后继续等其他来源；
4. 第一个成功结果立即返回；
5. `finally` 取消并等待剩余任务；
6. 全部失败时抛出 `ExceptionGroup`。

取消后继续 `gather()` 是为了让任务真正收尾并读取异常，不能只调用 `cancel()` 就丢掉引用。

竞争请求会增加下游流量，只适合少量、结果确实等价且容量彼此独立的来源。

## TaskGroup 表达共同成败

订单创建需要同时查询商品并检查库存。任何一项失败，订单都不能继续：

```python
async with asyncio.timeout(
    self.timeout_seconds
):
    try:
        async with asyncio.TaskGroup() as group:
            for item in command.items:
                product_tasks[item.sku] = (
                    group.create_task(
                        self.catalog.get_product(
                            item.sku
                        )
                    )
                )
                group.create_task(
                    self.inventory.ensure_available(
                        item.sku,
                        item.quantity,
                    )
                )
    except* BackendInterviewError as group_error:
        raise group_error.exceptions[0] from None
```

TaskGroup 退出时保证所有子任务已经结束。一个子任务失败，它会取消尚未完成的兄弟任务，并用
`ExceptionGroup` 汇总异常。

## 两种并发语义不能混用

| 场景 | 成功条件 | 合适工具 |
| --- | --- | --- |
| 商品与库存都必须成功 | 全部成功 | TaskGroup |
| 两个镜像来源任选一个 | 任一成功 | `first_success()` |
| 相同 key 只需加载一次 | 一个加载，其余共享结果 | single-flight |

如果把商品和库存查询写成 first-success，只成功一个也会继续，业务结果明显错误。若把镜像来源放进
TaskGroup，一个快速失败会取消另一个可能成功的来源。

选择并发工具时，要直接检查失败怎样传播、取消哪些任务，以及结果怎样返回。

## 任务数量也需要边界

TaskGroup 会管理它创建的任务生命周期，却不会自动限制数量。对大输入仍要结合 Semaphore 或固定 worker。
single-flight 减少相同 key 的重复加载，也不能限制大量不同 key 同时未命中。

结构化并发解决“这些子任务属于谁、何时完成”，容量限制解决“同时允许多少任务”。两个问题都要明确。
