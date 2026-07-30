# 异步测试与 unittest

异步测试用于检查 `async def` 定义的协程函数。测试必须 `await` 被测协程，并在结束前处理子任务、
异常和资源清理。pytest 也能运行大多数标准库 `unittest.TestCase`。

<!-- 对应源码：python/python_interview_practice/14_testing_and_mocking.py、python/tests/backend/ -->

## pytest-asyncio

项目配置：

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

因此异步测试可以直接写成：

```python
async def fetch_value() -> int:
    return 42


async def test_async_result() -> None:
    result = await fetch_value()

    assert result == 42
```

没有 auto 模式时，通常显式标记：

```python
import pytest


@pytest.mark.asyncio
async def test_async_result_explicit() -> None:
    result = await fetch_value()
    assert result == 42
```

两种写法都会等待 `fetch_value()` 完成。`asyncio_mode = "auto"` 只是省去了
`@pytest.mark.asyncio` 标记。

## AsyncMock

异步依赖必须返回可等待对象：

```python
from unittest.mock import AsyncMock


async def load_name(client, user_id: int) -> str:
    payload = await client.fetch_user(user_id)
    return payload["name"]


async def test_load_name() -> None:
    client = AsyncMock()
    client.fetch_user.return_value = {"name": "小林"}

    result = await load_name(client, 7)

    assert result == "小林"
    client.fetch_user.assert_awaited_once_with(7)
```

异步测试还需要检查可观察的生命周期行为：

- timeout 是否中断等待；
- 取消是否继续传播；
- 兄弟任务失败时其他任务是否收尾；
- Semaphore 并发上限是否生效；
- 测试后是否残留 Task 或连接。

不要只验证内部 await 次数。实现可以重构，但对外的超时、取消和资源语义应保持稳定。

## unittest.TestCase

下面的例子使用 `TestCase` 检查加法结果和异常：

```python
import unittest


class DiscountTests(unittest.TestCase):
    def test_vip_discount(self) -> None:
        self.assertEqual(
            calculate_discount(
                price=100,
                vip=True,
            ),
            80,
        )


if __name__ == "__main__":
    unittest.main()
```

pytest 可以收集并运行大多数 `unittest.TestCase`：

| unittest | pytest 风格 |
| --- | --- |
| `self.assertEqual(actual, expected)` | `assert actual == expected` |
| `self.assertTrue(value)` | `assert value` |
| `self.assertIsNone(value)` | `assert value is None` |
| `self.assertRaises(Error)` | `pytest.raises(Error)` |

仓库的 `14_testing_and_mocking.py` 用 unittest 组织九个测试，Mock 和 patch 仍来自标准库
`unittest.mock`。其他测试统一由 pytest 运行。

## 加载数字开头的教学模块

`08_algorithms.py` 不能直接写进 import 语句：

```python
# 语法无效：
# import python_interview_practice.08_algorithms
```

项目测试按文件路径加载：

```python
import importlib.util
from pathlib import Path

module_path = (
    Path(__file__).resolve().parents[1]
    / "python_interview_practice"
    / "08_algorithms.py"
)
spec = importlib.util.spec_from_file_location(
    "interview_algorithms",
    module_path,
)

if spec is None or spec.loader is None:
    raise ImportError(f"无法加载模块: {module_path}")

algorithms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(algorithms)
```

`"interview_algorithms"` 是本次加载使用的合法模块名。普通应用模块不建议以数字开头；这里用编号保持
课程文件的排列顺序。
