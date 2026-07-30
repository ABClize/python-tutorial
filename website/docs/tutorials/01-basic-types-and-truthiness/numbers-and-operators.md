# Python 数值与运算符

Python 使用运算符完成计算和判断。算术运算符处理数字，比较运算符得到 `True` 或 `False`，
逻辑运算符组合多个条件。

<!-- 对应源码：python/python_interview_practice/01_basic_types.py -->

## 数值运算

Python 常用算术运算符如下：

| 运算符 | 说明 | 示例 | 结果 |
| --- | --- | --- | --- |
| `+` | 加法 | `7 + 2` | `9` |
| `-` | 减法 | `7 - 2` | `5` |
| `*` | 乘法 | `7 * 2` | `14` |
| `/` | 除法 | `7 / 2` | `3.5` |
| `//` | 向下取整除法 | `7 // 2` | `3` |
| `%` | 取余 | `7 % 2` | `1` |
| `**` | 乘方 | `7 ** 2` | `49` |

### 实例

下面用整数 `7` 和 `2` 演示五种常见运算。

```python
left = 7
right = 2

print(left + right)
print(left / right)
print(left // right)
print(left % right)
print(left ** right)
```

运行结果：

```text
9
3.5
3
1
49
```

输出依次是加法、普通除法、向下取整除法、取余和乘方的结果。`/` 总是返回浮点数。

`//` 表示向下取整，不是简单删除小数部分。负数最容易看出区别：

```python
print(-7 / 2)
print(-7 // 2)
```

运行结果：

```text
-3.5
-4
```

普通除法得到 `-3.5`。向下取整要取不大于 `-3.5` 的最大整数，所以结果是 `-4`。

### 复合赋值

复合赋值把计算和赋值写在一起。下面两种写法在整数计算中效果相同：

```python
count = count + 1
count += 1
```

`+=`、`-=`、`*=` 等称为复合赋值运算符。对于列表等可变对象，复合赋值可能原地修改对象；对于整数、
字符串等不可变对象，它会产生新对象并重新绑定变量。

## 比较运算

比较运算用于判断两个值的大小或是否相等，结果是布尔值 `True` 或 `False`：

| 运算符 | 说明 |
| --- | --- |
| `==` | 值相等 |
| `!=` | 值不相等 |
| `<`、`<=` | 小于、小于等于 |
| `>`、`>=` | 大于、大于等于 |

下面检查分数是否等于 `82`、是否不等于 `60`，以及是否位于 `0` 到 `100` 之间：

```python
score = 82

print(score == 82)
print(score != 60)
print(score >= 60)
print(0 <= score <= 100)
```

运行结果：

```text
True
True
True
True
```

四个条件都成立，所以四行都是 `True`。

`0 <= score <= 100` 是链式比较，等价于：

```python
0 <= score and score <= 100
```

## 逻辑运算

`and`、`or` 和 `not` 用于组合条件。下面假设用户已经成年并且持有票券：

```python
age = 20
has_ticket = True

print(age >= 18 and has_ticket)
print(age < 18 or not has_ticket)
print(not has_ticket)
```

运行结果：

```text
True
False
False
```

- `and`：两边都为真时条件成立；
- `or`：至少一边为真时条件成立；
- `not`：把真值结果反转。

`and` 和 `or` 会短路。`and` 左边为假时不再计算右边；`or` 左边为真时不再计算右边：

```python
value = 0

print(value != 0 and 10 / value > 1)
```

运行结果：

```text
False
```

`value != 0` 是 `False`。`and` 已经可以确定整个表达式为假，所以右边的 `10 / value`
没有执行，也就不会发生除零错误。

## 数值类型注意事项

### `bool` 是 `int` 的子类

下面的例子直接查看 `bool` 与 `int` 的类型关系：

```python
print(isinstance(True, int))
print(True == 1)
print(True + 1)
```

运行结果：

```text
True
True
2
```

这是 Python 的类型关系，不表示业务中的布尔值和数量可以混用。需要严格排除布尔值时，应单独判断
`isinstance(value, bool)`。

### 浮点数是近似值

下面计算两个常见小数，并把结果与 `0.3` 比较：

```python
print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)
```

运行结果：

```text
0.30000000000000004
False
```

第一行不是精确的 `0.3`，所以第二行得到 `False`。许多十进制小数无法用有限的二进制位精确表示。
近似数值比较可以使用 `math.isclose()`：

```python
import math

print(math.isclose(0.1 + 0.2, 0.3))
```

运行结果：

```text
True
```

金额等需要十进制规则的场景可以使用 `decimal.Decimal`，并从字符串构造：

```python
from decimal import Decimal

print(Decimal("0.1") + Decimal("0.2"))
```

运行结果：

```text
0.3
```

### Python 整数没有固定宽度

Python 的 `int` 会根据数值大小使用更多内存，不会像固定宽度整数那样直接溢出。超大整数仍会增加
内存和计算成本，因此不能无限制处理来自外部的超长数字。
