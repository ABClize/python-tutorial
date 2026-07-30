# Python datetime 与时区

`datetime` 模块用于表示日期、时间和时间间隔。它能处理跨日、闰年和时间加减。需要跨时区转换时，
还要配合 `zoneinfo` 使用。

<!-- 章节源码：python/python_interview_practice/12_standard_library_patterns.py；相关标准库：datetime、zoneinfo -->

## 日期、时间与时长

标准库中最常用的四种类型如下：

| 类型 | 表示内容 |
| --- | --- |
| `date` | 年、月、日 |
| `time` | 一天中的时间 |
| `datetime` | 日期和时间 |
| `timedelta` | 两个时间点之间的时长 |

下面的示例从 UTC 时间 9:00 开始，加上 90 分钟：

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

## 不带和带时区信息的 datetime

没有时区信息的 datetime 通常称为 naive datetime：

```python
from datetime import datetime

value = datetime(2026, 7, 30, 9, 0)
print(value.tzinfo)
```

运行结果：

```text
None
```

带有可用时区信息、能够确定 UTC 偏移量的 datetime 称为 aware datetime。仅让 `tzinfo` 不为
`None` 还不够，它的 `utcoffset()` 也必须能返回偏移量。跨系统保存时间点时通常使用 UTC aware
datetime，展示时再转换到用户时区。

## zoneinfo 转换时区

下面把 UTC 时间转换为上海时间：

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

`strftime()` 把时间格式化成字符串，`strptime()` 按指定格式解析字符串。接口接收时间时，要写清楚
允许的格式和时区。

## 使用注意事项

- 不要直接比较不带时区信息的 datetime（naive）和带时区信息的 datetime（aware）。
- 跨系统时间点通常使用 UTC，展示时转换时区。
- 时长使用 `timedelta`，不要把秒数和时间点混在一起。
