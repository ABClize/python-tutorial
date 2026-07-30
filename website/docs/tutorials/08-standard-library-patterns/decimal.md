# Python 数值标准库：Decimal、math、random 与 statistics

写程序时经常会遇到四类数值问题：金额要精确到分、数字要开平方或取整、程序要随机抽取一个值、
一组数据要计算平均数或中位数。Python 标准库已经为这些需求准备了对应工具：

- `decimal` 处理需要精确表示和明确舍入规则的十进制小数；
- `math` 提供平方根、取整和浮点数比较等数学函数；
- `random` 生成伪随机数，适合模拟、抽样和普通随机选择；
- `statistics` 计算平均数、中位数等常用统计量。

这些模块都不需要另外安装。

<!-- 章节源码：python/python_interview_practice/12_standard_library_patterns.py；相关标准库：decimal、math、random、statistics、secrets -->

## Decimal：需要精确十进制计算时使用

### float 为什么会出现小数误差

先看一个常见的浮点数结果：

```python
print(0.1 + 0.2)
```

运行结果：

```text
0.30000000000000004
```

`float` 使用二进制保存小数，很多十进制小数不能被精确表示。因此，计算结果可能带有一个很小的
误差。这不是 Python 的计算出了问题，也不是 Python 特有的问题。

科学计算和大多数普通计算可以继续使用 `float`。但是金额、税率等数据需要按十进制规则精确计算时，
通常应使用 `Decimal`。

### 从字符串创建 Decimal

下面把金额写成字符串，再交给 `Decimal`：

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

`Decimal("19.90")` 会准确保存 `19.90`，所以乘以 3 后仍能得到预期的 `59.70`。

通常应从字符串或整数创建 `Decimal`，不要先写成 `float`：

```python
from decimal import Decimal

print(Decimal("0.1"))
print(Decimal(0.1))
```

第二行接收到的已经是近似的 `float`，因此会显示一个很长的十进制数。`Decimal` 只能准确接收传入的
值，不能把已经产生的浮点误差自动消除。

### 使用 quantize 指定小数位和舍入规则

下面把 `10.005` 按四舍五入规则保留两位小数：

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

`Decimal("0.01")` 表示结果要保留两位小数，`ROUND_HALF_UP` 表示常见的“四舍五入”。不同业务可能
采用不同规则，不能只调用 `round()` 就假定所有金额都处理正确。

还要注意，`Decimal` 不能直接和 `float` 混合运算：

```python
from decimal import Decimal

price = Decimal("19.90")
print(price + 0.1)
```

运行时会抛出 `TypeError`。同一段精确计算中的数字应统一使用 `Decimal`。

## math：常用数学函数

`math` 模块提供许多基础数学函数。下面先看四个常用函数：

```python
import math

print(math.sqrt(81))
print(math.ceil(3.2))
print(math.floor(3.8))
print(math.isclose(0.1 + 0.2, 0.3))
```

运行结果：

```text
9.0
4
3
True
```

这四个函数的作用分别是：

- `math.sqrt(81)` 计算平方根，结果是 `9.0`；
- `math.ceil(3.2)` 向正无穷方向取整，所以结果是 `4`；
- `math.floor(3.8)` 向负无穷方向取整，所以结果是 `3`；
- `math.isclose(a, b)` 判断两个浮点数是否足够接近。

“向上”和“向下”不是简单地去掉小数。负数更容易看出区别：

```python
import math

print(math.ceil(-3.8))
print(math.floor(-3.2))
```

运行结果：

```text
-3
-4
```

### 比较浮点数时使用 isclose

前面已经看到 `0.1 + 0.2` 不会正好等于 `0.3`，因此不宜直接用 `==` 判断计算结果：

```python
import math

result = 0.1 + 0.2

print(result == 0.3)
print(math.isclose(result, 0.3))
```

运行结果：

```text
False
True
```

`isclose()` 会在允许的误差范围内比较两个数。多数普通场景可以先使用默认误差；对测量值、金额或
科学计算设定误差时，还要根据业务含义明确 `rel_tol` 和 `abs_tol`。

## random：生成伪随机数

`random` 可以生成随机整数、随机选择元素或从一组数据中抽样。为了让下面的运行结果每次都相同，
先创建一个使用固定种子的局部随机数生成器：

```python
import random

generator = random.Random(2026)

print(generator.randint(1, 6))
print(generator.choice(["红", "蓝", "绿"]))
print(generator.sample(range(1, 11), k=3))
```

运行结果：

```text
1
蓝
[9, 10, 2]
```

- `randint(1, 6)` 生成 1 到 6 之间的整数，两个端点都可能取到；
- `choice(values)` 从序列中选择一个元素；
- `sample(values, k=3)` 不重复地抽取 3 个元素，并返回一个新列表。

`random.Random(2026)` 会创建一个独立的随机数生成器。相同 Python 环境、相同种子和相同调用顺序
会产生相同结果，因此很适合教程、测试和可重复的模拟。实际程序如果每次都需要不同结果，就不应把
种子固定成同一个值。

### random 不适合生成密码和令牌

`random` 生成的是伪随机数。知道种子或观察到足够多结果后，后续值可能被预测，所以不要用它生成
密码、验证码、重置链接或访问令牌。安全场景应使用 `secrets`：

```python
import secrets

token = secrets.token_urlsafe(24)
print(token)
```

这里的输出每次都不同，因此不列出固定结果。

## statistics：计算平均数和中位数

`statistics` 适合处理规模不大的普通数值数据。下面计算一组成绩的平均数和中位数：

```python
from statistics import mean, median

scores = [60, 70, 80, 90, 100]

print(mean(scores))
print(median(scores))
print(median([10, 20, 30, 100]))
```

运行结果：

```text
80
80
25.0
```

`mean()` 把所有值相加再除以数量。`median()` 先按大小排列，再取中间位置的值；数据数量为偶数时，
取中间两个值的平均数。

平均数容易受到极端值影响。例如 `[10, 20, 30, 100]` 的平均数是 `40`，中位数却是 `25.0`。
描述工资、响应时间等可能存在极端值的数据时，中位数往往更能表示“典型水平”。选哪个指标要看数据
和问题，不能只看哪个数字更好看。

### 空数据会抛出 StatisticsError

没有任何数据时，平均数和中位数都没有定义。`mean([])` 和 `median([])` 会抛出
`StatisticsError`：

```python
from statistics import StatisticsError, mean

scores: list[int] = []

try:
    print(mean(scores))
except StatisticsError:
    print("没有数据，无法计算平均数")
```

运行结果：

```text
没有数据，无法计算平均数
```

如果空列表是正常情况，应在计算前检查列表是否为空，或者像上面一样捕获
`StatisticsError`。不要随意把空数据的平均数设成 0，因为“没有数据”和“平均值确实为 0”含义不同。

## 使用注意事项

- 精确十进制计算使用 `Decimal`，并从字符串或整数创建数值。
- 平方根、取整和浮点数近似比较使用 `math`。
- 普通模拟和抽样可以使用 `random`；密码和安全令牌使用 `secrets`。
- 平均数和中位数可以使用 `statistics`，计算前要考虑空数据和极端值。
- 金额还要同时记录币种、最小单位和舍入规则，`Decimal` 不会替业务做这些决定。
