# 测试层次与项目实践

单元测试检查一个函数或类。集成测试检查多个组件能否配合。API 测试通过 HTTP 调用接口。属性测试会
生成多组输入，检查某条规则是否一直成立。不同测试层次解决不同问题。

<!-- 对应源码：python/tests/、python/tests/backend/ -->

## 测试层次

| 层次 | 主要验证 | 常见依赖 | 特点 |
| --- | --- | --- | --- |
| 单元测试 | 函数、类和业务规则 | Fake、Stub、Mock | 快，定位清楚 |
| 集成测试 | 数据库、文件和框架装配 | 真实局部组件 | 覆盖连接边界 |
| API 测试 | HTTP 请求、校验和响应 | 测试应用与客户端 | 验证接口契约 |
| 端到端测试 | 完整用户流程 | 接近真实系统 | 慢，维护成本高 |

全部依赖都 Mock 会漏掉真实集成错误；所有测试都启动完整系统又会慢且难定位。应根据风险组合层次。

## FastAPI 接口测试

下面使用 `TestClient` 调用应用的健康检查接口：

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def test_health() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

API 测试还应检查错误结构、认证、请求头、幂等性和依赖覆盖。应用有 lifespan 资源时，应把
`TestClient` 放进上下文管理器。这样启动和关闭代码都会执行：

```python
with TestClient(app) as client:
    response = client.get("/health")
```

离开 `with` 代码块时，测试客户端会执行应用的关闭流程。

## Hypothesis 属性测试

普通样例检查已知输入，属性测试让工具生成大量输入：

```python
from hypothesis import given
from hypothesis import strategies as st


@given(st.lists(st.integers()))
def test_sort_preserves_length(values: list[int]) -> None:
    assert len(sorted(values)) == len(values)
```

项目的 `tests/test_properties.py` 检查合并有序列表、展平、二分查找、括号和回文等不变量。Hypothesis
发现失败后会缩小输入，尽量给出更小的反例。

属性测试不替代有名字的业务样例。错误消息、权限和关键边界仍适合用明确示例表达。

## 覆盖率

下面的命令运行测试，并统计哪些源码行被执行：

```bash
uv run pytest --cov --cov-report=term-missing
```

覆盖率可以显示执行过的语句、分支和缺失行，但高覆盖率不说明：

- 断言是否有意义；
- 边界条件是否正确；
- 错误结果是否被识别；
- 并发和时间行为是否稳定；
- 测试是否耦合内部实现。

覆盖率用于发现明显空白，不是唯一质量目标。

## 不稳定测试

| 原因 | 处理方式 |
| --- | --- |
| 当前时间 | 注入时钟或冻结时间边界 |
| 随机数 | 固定种子或注入随机源 |
| 测试顺序 | 每次重新创建状态 |
| 真实网络 | Fake、Mock 或受控集成环境 |
| 固定端口或文件名 | 系统分配端口、`tmp_path` |
| 并发时序断言 | 等待明确事件，不猜测 sleep |
| 浮点精确比较 | `pytest.approx()` 或领域误差 |
| 缓存残留 | 测试前后清理缓存 |

```python
import pytest


def test_floating_point_result() -> None:
    assert 0.1 + 0.2 == pytest.approx(0.3)
```

不要靠增加重试次数掩盖不稳定测试，应找出没有控制的时间、状态或外部依赖。

## 选择可观察行为

优先覆盖：

- 公开输入输出；
- 边界和失败分支；
- 金额、权限和幂等性等高风险规则；
- 外部副作用是否发生以及参数是否正确；
- 过去出现过的缺陷；
- 超时、取消和资源清理；
- 模块之间的契约。

通常不直接测试私有实现的每一行，也不验证 Python 已保证的基础行为。重构内部实现后仍能通过的测试，
通常更接近行为契约。

## 项目命令

在 `python/` 目录执行：

```bash
# 全部测试
uv run pytest -v

# 算法与练习
uv run pytest \
  tests/test_algorithms.py \
  tests/test_practice_questions.py \
  tests/test_properties.py -v

# FastAPI 后端
uv run pytest tests/backend -v

# 覆盖率
uv run pytest --cov --cov-report=term-missing

# 运行标准库 Mock 示例
uv run python python_interview_practice/14_testing_and_mocking.py
```

失败时先单独运行第一个失败节点。若多个失败来自同一初始化错误，先修复根因。
