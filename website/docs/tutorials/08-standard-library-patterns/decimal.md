# Python Decimal 精确十进制计算

十进制数包含精度和舍入规则。需要按照十进制规则计算金额等数据时，`Decimal` 可以避免二进制浮点
近似值带来的误差。

<p class="source-note">章节源码：<code>python/python_interview_practice/12_standard_library_patterns.py</code>；相关标准库：<code>decimal</code></p>

## float 的十进制误差

```python
print(0.1 + 0.2)
```

运行结果：

```text
0.30000000000000004
```

float 使用二进制浮点数，很多十进制小数不能精确表示。这不是 Python 特有问题。

## Decimal 精确十进制计算

```python
from decimal import Decimal

price = Decimal("19.90")
quantity = 3
total = price * quantity

print(total)
print(Decimal("0.1") + Decimal("0.2"))
```

运行结果：

```text
59.70
0.3
```

通常从字符串构造 Decimal，避免先经过 float：

```python
from decimal import Decimal

print(Decimal("0.1"))
print(Decimal(0.1))
```

第二行会显示 float `0.1` 的完整二进制近似值。

## 指定舍入规则

```python
from decimal import Decimal, ROUND_HALF_UP

amount = Decimal("10.005")
rounded = amount.quantize(
    Decimal("0.01"),
    rounding=ROUND_HALF_UP,
)

print(rounded)
```

运行结果：

```text
10.01
```

`quantize()` 指定目标小数位。Decimal 提供计算工具，但不会替业务决定币种、保留位数和舍入方式。

## 使用注意事项

- Decimal 通常从字符串或整数构造。
- 不要混合 Decimal 和 float 计算。
- 金额模型还需要明确币种、最小单位和舍入规则。
