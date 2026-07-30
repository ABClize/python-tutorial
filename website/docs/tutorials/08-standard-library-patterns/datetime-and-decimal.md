# Python datetime、时区与 Decimal

日期时间和十进制数看似是普通数值，实际包含时区、日历、精度和舍入等规则。使用专用类型可以避免手工
切割字符串和二进制浮点误差。

<p class="source-note">章节源码：<code>python/python_interview_practice/12_standard_library_patterns.py</code>；相关标准库：<code>datetime</code>、<code>zoneinfo</code>、<code>decimal</code></p>

## 日期、时间与时长

标准库中的常用类型：

| 类型 | 表示内容 |
| --- | --- |
| `date` | 年、月、日 |
| `time` | 一天中的时间 |
| `datetime` | 日期和时间 |
| `timedelta` | 两个时间点之间的时长 |

```python
from datetime import UTC, datetime, timedelta

started_at = datetime(2026, 7, 30, 9, 0, tzinfo=UTC)
finished_at = started_at + timedelta(minutes=90)

print(finished_at.isoformat())
print(finished_at - started_at)
```

运行结果：

```text
2026-07-30T10:30:00+00:00
1:30:00
```

不要用字符串加减模拟日期运算。跨日、闰年和月份长度应由 datetime 处理。

## naive 与 aware datetime

没有时区信息的 datetime 称为 naive datetime：

```python
from datetime import datetime

value = datetime(2026, 7, 30, 9, 0)
print(value.tzinfo)
```

运行结果：

```text
None
```

带 `tzinfo` 的称为 aware datetime。跨系统保存时间点时通常使用 UTC aware datetime，展示时转换到
用户时区。

## zoneinfo 转换时区

```python
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

utc_time = datetime(2026, 7, 30, 1, 0, tzinfo=UTC)
shanghai_time = utc_time.astimezone(ZoneInfo("Asia/Shanghai"))

print(shanghai_time.isoformat())
```

运行结果：

```text
2026-07-30T09:00:00+08:00
```

不要通过直接修改小时数转换时区。夏令时和历史时区规则应交给 `zoneinfo`。

## 解析与格式化

ISO 8601 格式适合程序交换：

```python
from datetime import datetime

value = datetime.fromisoformat("2026-07-30T09:00:00+08:00")

print(value.isoformat())
print(value.strftime("%Y年%m月%d日 %H:%M"))
```

运行结果：

```text
2026-07-30T09:00:00+08:00
2026年07月30日 09:00
```

`strftime()` 用于展示，`strptime()` 按指定格式解析。输入来自接口时，应明确接受哪些格式和时区。

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

- 不要直接比较 naive 和 aware datetime。
- 跨系统时间点通常使用 UTC，展示时转换时区。
- 时长使用 `timedelta`，不要把秒数和时间点混在一起。
- Decimal 通常从字符串或整数构造。
- 不要混合 Decimal 和 float 计算。
- 金额模型还需要明确币种、最小单位和舍入规则。
