# 测试、依赖注入与 Mock

好的测试验证行为契约，而不是复制实现。依赖注入把业务规则与网络、数据库、时间和随机数分开，
Mock 才能用在清晰边界上，而不是把整个调用栈 patch 成无法理解的剧本。

<p class="source-note">对应源码：<code>python/python_interview_practice/14_testing_and_mocking.py</code>、<code>python/tests/</code></p>

## 一个测试只讲一个行为

Arrange / Act / Assert 让测试意图清楚：

```python
def test_checkout_charges_after_inventory_reservation():
    # Arrange
    inventory = FakeInventory(available=True)
    payment = FakePayment(transaction_id="txn-001")
    service = CheckoutService(inventory, payment)

    # Act
    receipt = service.checkout("BOOK", quantity=2, unit_price_cents=4500)

    # Assert
    assert receipt.total_cents == 9000
    assert payment.charges == [9000]
```

测试名应描述条件和结果，而不是被测方法名。失败时，阅读名字和断言就能知道哪条契约被破坏。

## 依赖注入先建立边界

业务服务通过构造函数接收库存、支付和通知接口，不在方法内部创建真实客户端：

<div class="concept-map">
  <div class="concept-step"><small>输入与规则</small><strong>CheckoutService</strong></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>端口</small><strong>Inventory</strong></div>
  <span class="concept-arrow">+</span>
  <div class="concept-step"><small>端口</small><strong>PaymentGateway</strong></div>
  <span class="concept-arrow">+</span>
  <div class="concept-step"><small>端口</small><strong>Notifier</strong></div>
</div>

生产环境注入真实实现，单元测试注入 Fake 或 Mock。这样核心测试不发送网络请求，也不需要启动
FastAPI。

## Fake、Stub 和 Mock 的侧重点

- **Stub**：提供预设返回值，让被测代码能继续运行；
- **Fake**：有简化但可工作的实现，例如内存仓储；
- **Mock**：记录交互，并允许断言调用次数与参数；
- **Spy**：包装真实行为，同时记录调用。

能用状态断言和简单 Fake 表达时，通常比大量交互断言更稳。只有“是否调用外部副作用”本身就是
契约时，Mock 调用断言才最有价值。

## patch 要替换查找位置

如果模块 `service` 执行了 `from client import request_json`，测试应 patch
`service.request_json`，因为被测代码从这里查找依赖，而不是 patch 原定义位置。

```python
with patch("service.request_json", return_value={"name": "Guido"}) as mocked:
    assert load_user_name(7) == "Guido"

mocked.assert_called_once_with("https://example.invalid/users/7")
```

`spec` 或 `autospec` 可以限制 Mock 接口，尽早发现属性拼写或签名错误。

## side_effect 表达时间序列

```python
client.fetch.side_effect = [
    TimeoutError("第一次超时"),
    {"value": 42},
]
```

这适合验证重试、失败后停止副作用等行为。不要把生产代码的每个内部步骤都写成调用序列，否则一次
无行为变化的重构就会击碎测试。

## 测试层次对应不同风险

| 层次 | 主要验证 | 常用替身 |
| --- | --- | --- |
| 纯函数 / 领域 | 规则、边界、不变量 | 通常不需要 |
| 服务层 | 编排、失败、并发语义 | Fake、Mock |
| API | 路由、校验、认证、错误映射 | 依赖覆盖 |
| 端到端 | 真实组件能否协作 | 尽量少替换 |

属性测试适合验证大量输入上的普遍不变量，例如“排序结果有序且元素不丢失”。它不是随机多跑几次，
而是生成输入并把失败样例收缩到最小。

## pytest fixture 管理测试依赖

fixture 表达测试所需对象和生命周期，可以组合而不是继承：

```python
@pytest.fixture
def repository():
    value = InMemoryRepository()
    yield value
    value.close()


def test_save_and_load(repository):
    repository.save("key", 42)
    assert repository.get("key") == 42
```

fixture scope 决定复用范围。状态可变的 fixture 若提升到 module/session scope，可能让测试互相污染；
默认 function scope 最隔离。autouse fixture 会形成隐藏依赖，只应用于真正全局的不变量或清理。

## 参数化减少重复但不隐藏含义

```python
@pytest.mark.parametrize(
    ("value", "expected"),
    [(0, False), (1, True), ("", False), ("x", True)],
)
def test_truthiness(value, expected):
    assert bool(value) is expected
```

参数化适合同一行为的输入表。若不同案例需要完全不同准备和断言，拆成具名测试更容易理解失败原因。

## 属性测试验证普遍性质

Hypothesis 会生成输入并收缩失败样例。适合的性质包括：

- 编码后解码回到原值；
- 排序后有序且元素数量不变；
- 合并两个有序序列后仍有序；
- 幂等操作执行多次结果不变；
- 优化实现与简单参考实现结果一致。

不要在属性测试中重写一份与生产实现同样复杂的“期望算法”，否则两边可能共享同一错误。

## 异步测试

异步服务测试应真正 `await` 被测方法，并验证超时、取消和资源清理。使用 `AsyncMock` 时同样要
关注接口 spec；对复杂状态仓储，内存 Fake 通常比一串异步返回值更易懂。

时间相关测试应尽量注入 clock、sleep 或超时参数，避免真实等待。并发测试要用 Event、Barrier 等
同步点制造确定性交错，不要依赖“sleep 10ms 应该正好发生竞争”。

## 契约测试与集成测试

多个实现满足同一 Protocol 时，可以复用一组契约测试，确保内存仓储和数据库仓储遵守相同语义。
集成测试则验证真实数据库、序列化、事务和框架装配，数量可以少于单元测试，但不能全部由 Mock
替代。

端到端测试最接近用户路径，也最慢、最难定位失败。一个健康组合通常是大量领域/服务测试、适量边界
集成测试和少量关键端到端路径，而不是机械追求固定金字塔比例。

## 常见误区

### 覆盖率高就代表测试好

覆盖率只说明代码被执行，不能证明断言有效、边界完整或失败路径被验证。

### Mock 越多隔离越彻底

过度 Mock 会让测试只验证自己的配置。先通过模块边界和依赖注入降低耦合，再选择最简单的替身。

### 单元测试不应接触任何真实对象

值对象、领域对象和纯计算应直接使用真实实现。需要替换的是慢、不稳定或有外部副作用的边界。

## 面试时怎么表述

> 我会先用依赖注入建立可替换边界，领域规则用状态断言，外部副作用才使用 Mock 交互断言。
> patch 必须替换被测代码实际查找依赖的位置，并用 spec 限制接口。测试层次分别覆盖规则、编排、
> HTTP 契约和真实集成，覆盖率只是辅助指标。
