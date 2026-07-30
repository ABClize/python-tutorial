# 异常、参数化与 fixture

函数除了返回正常结果，也可能按规定抛出异常。`pytest.raises()` 用来检查异常。参数化让同一个测试
运行多组数据。fixture 是 pytest 提供测试数据和清理资源的机制。

<p class="source-note">对应源码：<code>python/tests/</code></p>

## 验证异常

使用 `pytest.raises()`：

```python
import pytest


def test_negative_price_is_rejected() -> None:
    with pytest.raises(ValueError):
        calculate_discount(price=-1, vip=True)
```

同时检查稳定消息：

```python
def test_negative_price_explains_constraint() -> None:
    with pytest.raises(
        ValueError,
        match="价格不能小于 0",
    ):
        calculate_discount(price=-1, vip=True)
```

`match` 使用正则表达式。消息包含 `(`、`[` 等特殊字符时，可以用 `re.escape()`：

```python
import re

with pytest.raises(ValueError, match=re.escape("范围为 [0, 100]")):
    validate_score(101)
```

需要读取异常对象：

```python
def test_negative_price_contains_original_value() -> None:
    with pytest.raises(ValueError) as error:
        calculate_discount(price=-1, vip=True)

    assert "价格" in str(error.value)
```

`raises` 代码块应只包含预期抛出异常的调用。块内语句过多时，其他语句抛出同类型异常也可能让测试误
通过。

## 参数化测试

同一规则有多组输入输出时，使用 `pytest.mark.parametrize`：

```python
import pytest


@pytest.mark.parametrize(
    ("price", "vip", "expected"),
    [
        (100, True, 80),
        (100, False, 100),
        (0, True, 0),
    ],
)
def test_discount_rules(
    price: int,
    vip: bool,
    expected: int,
) -> None:
    assert calculate_discount(price, vip) == expected
```

每行数据是独立用例。可以为参数设置可读 id：

```python
@pytest.mark.parametrize(
    ("price", "vip", "expected"),
    [
        pytest.param(100, True, 80, id="vip"),
        pytest.param(100, False, 100, id="regular"),
        pytest.param(0, True, 0, id="zero-price"),
    ],
)
def test_discount_rules_with_ids(
    price: int,
    vip: bool,
    expected: int,
) -> None:
    assert calculate_discount(price, vip) == expected
```

只有数据不同、测试结构相同的场景适合参数化。准备过程和业务含义完全不同时，独立测试更容易阅读。

## fixture 注入测试数据

fixture 是由 pytest 创建并按参数名注入的对象：

```python
import pytest


@pytest.fixture
def sample_prices() -> list[int]:
    return [100, 200, 300]


def test_price_count(sample_prices: list[int]) -> None:
    assert len(sample_prices) == 3
```

适合放入 fixture 的内容包括重复数据、临时路径、应用客户端、数据库会话和需要关闭的资源。只用一次的
简单数据直接写在测试中更清楚。

## 使用 yield 清理

下面的 fixture 在测试前创建资源，并在测试结束后执行清理：

```python
from collections.abc import Iterator
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest


@pytest.fixture
def report_directory() -> Iterator[Path]:
    with TemporaryDirectory() as directory:
        yield Path(directory)


def test_report_is_written(report_directory: Path) -> None:
    path = report_directory / "report.txt"
    path.write_text("完成", encoding="utf-8")

    assert path.read_text(encoding="utf-8") == "完成"
```

`yield` 前是准备，`yield` 后是清理。测试断言失败时，fixture 的清理部分仍会执行。

## tmp_path

pytest 内置的 `tmp_path` 为每个测试提供独立临时目录：

```python
from pathlib import Path


def test_score_file(tmp_path: Path) -> None:
    path = tmp_path / "scores.txt"
    path.write_text("82\n91\n", encoding="utf-8")

    assert path.read_text(encoding="utf-8").splitlines() == [
        "82",
        "91",
    ]
```

测试不需要手工清理这个目录。

## fixture 作用域

默认作用域是 `function`，每个测试重新创建：

```python
@pytest.fixture(scope="module")
def shared_resource():
    ...
```

还可以使用 `class`、`module`、`package` 和 `session`。扩大作用域可以减少昂贵初始化，但也增加状态
共享。会被测试修改的业务数据通常保持 `function` 级隔离。
