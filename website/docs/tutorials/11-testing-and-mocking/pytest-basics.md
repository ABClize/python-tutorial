# pytest 基础

pytest 是 Python 的测试运行器。它会查找测试文件，执行测试函数，并显示失败位置。普通测试不需要
继承专用基类，写一个函数并使用 Python 自带的 `assert` 即可。

<p class="source-note">对应源码：<code>python/tests/</code></p>

## 安装和运行

项目的测试依赖位于 `python/pyproject.toml`。在 `python/` 目录执行：

```bash
uv sync --group dev
uv run pytest
```

常用命令：

```bash
# 显示每个测试名称
uv run pytest -v

# 运行一个文件
uv run pytest tests/test_algorithms.py -v

# 运行一个测试类
uv run pytest tests/test_algorithms.py::BinarySearchTests -v

# 运行一个测试方法
uv run pytest \
  tests/test_algorithms.py::BinarySearchTests::test_empty_sequence_returns_minus_one -v

# 按名称筛选
uv run pytest -k "binary_search and not duplicate" -v

# 第一次失败后停止
uv run pytest -x

# 减少正常输出
uv run pytest -q
```

项目配置把 `tests/` 设为测试目录，并将 `python/` 工程根目录加入模块搜索路径。

## pytest 怎样发现测试

pytest 默认识别：

- 文件名为 `test_*.py` 或 `*_test.py`；
- 函数名以 `test_` 开头；
- 普通测试类名以 `Test` 开头，并且没有自定义 `__init__`；
- `unittest.TestCase` 子类中的测试方法。

例如：

```text
python/
├── price.py
└── tests/
    └── test_price.py
```

`test_price.py`：

```python
from price import calculate_discount


def test_vip_receives_twenty_percent_discount() -> None:
    result = calculate_discount(price=100, vip=True)

    assert result == 80
```

测试名应说明条件和结果。`test_works()` 发生失败时，无法从名字判断哪条规则出了问题。

## 第一个测试

被测函数：

```python
def calculate_discount(price: int, vip: bool) -> int:
    if price < 0:
        raise ValueError("价格不能小于 0")
    return int(price * 0.8) if vip else price
```

测试正常分支：

```python
def test_vip_receives_twenty_percent_discount() -> None:
    result = calculate_discount(price=100, vip=True)

    assert result == 80
```

测试通常包含三个逻辑阶段：

1. Arrange：准备输入和依赖；
2. Act：执行被测行为；
3. Assert：检查可观察结果。

简单测试不需要机械添加三段注释，用空行保持层次即可。

## 一个测试关注一个行为

“一个行为”不等于“只能写一个 assert”。结账成功可能同时产生收据、扣款和通知，它们都是同一场景的
直接结果，可以在一个测试中一起验证。

结账成功、库存不足和参数非法是三个不同场景。把它们写进同一个测试会产生大量条件分支，也会让失败
原因难以定位。

## assert 失败信息

pytest 会重写测试模块中的 `assert`，显示表达式两边的差异：

```python
def test_discount_result() -> None:
    result = calculate_discount(price=100, vip=True)

    assert result == 90
```

失败信息包含：

```text
E       assert 80 == 90
```

比较列表、字典和字符串时，pytest 还会展示差异位置。通常直接断言业务结果即可：

```python
assert receipt.total_cents == 9_000
assert response.status_code == 201
assert payload == {"status": "created"}
```

被测表达式有成本或还要继续检查时，先保存结果：

```python
result = expensive_operation()

assert result == expected
```

自定义断言消息适合补充表达式无法体现的业务背景，不应替代清晰的测试名。
