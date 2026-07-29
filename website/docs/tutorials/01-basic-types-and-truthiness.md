# 基础类型、比较与真值

Python 的基础类型并不难，真正容易出错的是把“值相等”“对象相同”“条件为真”混为一谈。
这一篇先建立三层判断：对象是什么类型、两个表达式是否得到相等的值、一个值放进条件时如何解释。

<p class="source-note">对应源码：<code>python/python_interview_practice/01_basic_types.py</code></p>

## 先看懂一段 Python 程序

Python 用缩进表示代码块，不使用大括号。冒号后的下一层通常缩进四个空格；同一代码块必须保持
一致缩进。

```python
name = "小林"  # 变量名指向一个字符串对象
score_text = "82"
score = int(score_text)

if score >= 60:
    result = "通过"
else:
    result = "未通过"

print(f"{name}：{result}，得分 {score}")
```

```text
小林：通过，得分 82
```

`#` 后是单行注释；`name`、`score` 是变量名；`if`、`else` 是关键字，不能作为变量名。Python
变量不需要预先声明类型，但对象始终有类型，`int("82")` 是把输入文本显式转换为整数。

交互输入 `input()` 的结果永远是字符串，即使用户输入 `82` 也是 `"82"`。因此先转换、再校验，
比直接把原始文本放进业务判断更可靠：

```python
raw_age = input("请输入年龄：").strip()
age = int(raw_age)
print(age + 1)
```

真实程序还要捕获无效数字，这会在[异常与上下文管理器](./06-exceptions-and-context-managers)中展开。

## 条件和循环把真值变成控制流

`if` / `elif` / `else` 从上到下选择第一个成立的分支。比较运算可以链式书写：

```python
temperature = 26

if temperature < 10:
    suggestion = "穿外套"
elif 10 <= temperature < 25:
    suggestion = "天气舒适"
else:
    suggestion = "注意防晒"
```

`for` 适合遍历可迭代对象，`while` 适合“条件成立就继续”。`break` 结束整个循环，`continue`
跳过本轮剩余代码：

```python
values = [3, -1, 0, 7]
positive_total = 0

for value in values:
    if value < 0:
        continue
    if value == 0:
        break
    positive_total += value

print(positive_total)  # 3
```

这里的控制流最终都依赖真值判断。先理解“条件怎样选择路径”，再看下一节“对象怎样决定真假”，
两部分就能接起来。

## 值、类型和对象身份

每个 Python 对象都有类型、值和身份。`type()` 观察类型，`==` 比较值，`is` 比较是否为同一对象。

```python
first = [1, 2]
second = [1, 2]
alias = first

first == second  # True：内容相等
first is second  # False：两个独立列表
first is alias   # True：指向同一个列表
```

业务数据通常比较值；对象身份主要用于 `None`、单例哨兵或明确的共享对象判断。不要用小整数或短
字符串的缓存现象推导业务规则。

## 条件表达式如何判断真假

`if value:` 会调用对象的真值规则。内置类型中，`None`、数值零和空容器通常是假值；非空容器和
非零数字通常是真值。

<TruthinessExplorer />

自定义对象可以实现 `__bool__()`；如果没有，Python 会尝试 `__len__()`，长度为零时视为假。
再没有这两个方法时，实例默认是真值。

```python
class Cart:
    def __init__(self, items: list[str]) -> None:
        self.items = items

    def __len__(self) -> int:
        return len(self.items)


if Cart([]):
    print("不会执行")
```

### 真值判断不是类型转换

`bool("False")` 仍是 `True`，因为它是非空字符串。读取环境变量、表单或 JSON 文本时，必须先
按照协议解析内容，不能直接用 `bool(text)` 解释用户输入。

## 字符串是不可变序列

字符串支持索引、切片和迭代，但不能原地修改字符。看似“修改”的方法都会返回新字符串。

```python
text = "  python interview  "

cleaned = text.strip().upper()
words = text.split()
reversed_text = text[::-1]
```

这种不可变性使字符串可以安全地作为字典键，也意味着循环中反复 `result += piece` 可能创建许多
中间对象。大量片段拼接通常优先 `"".join(pieces)`。

## Unicode、str 与 bytes

Python 3 的 `str` 保存 Unicode 文本，`bytes` 保存原始字节。网络、文件和加密边界最终处理的
通常是 bytes，因此必须明确编码和解码方向：

```python
text = "你好，Python"
payload = text.encode("utf-8")   # str -> bytes
restored = payload.decode("utf-8")  # bytes -> str
```

字符数量不等于字节数量：`len(text)` 统计 Unicode code point，`len(payload)` 统计字节。用户
眼中的一个字形还可能由多个 code point 组成，例如组合重音和部分 emoji。需要用户感知的文本截断
时，不能简单假定切片长度等于屏幕字符数。

文件读写应显式指定 `encoding="utf-8"`。解码失败时需要根据协议决定拒绝、替换还是记录原始字节，
不要在不知来源的情况下反复尝试多个编码并静默兜底。

## 数字与布尔值

`bool` 是 `int` 的子类，因此 `True == 1`。这是一项语言兼容设计，不代表业务上布尔值和数量
可以随意混用。需要排除布尔值时，要显式判断：

```python
def require_count(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("count 必须是整数")
    return value
```

浮点数使用二进制表示，部分十进制小数不能精确表示：

```python
0.1 + 0.2 == 0.3  # False
```

近似计算用 `math.isclose()`；金额等十进制精度场景考虑 `decimal.Decimal`，并从字符串构造。

### 整数没有固定宽度，但仍有资源成本

Python `int` 可以按需扩展，不会像固定宽度整数那样直接溢出，但位数越大，运算和内存成本越高。
从不可信输入解析超长整数、计算巨大指数或阶乘，仍可能造成 CPU 和内存压力。

## 解包让数据结构显式

序列解包会检查元素数量，星号目标可以接收剩余元素。

```python
point = (10, 20)
x, y = point

first, *middle, last = [3, 1, 4, 1, 5]
```

解包适合表达固定结构，但如果字段越来越多、含义不清，应换成 dataclass、NamedTuple 或领域对象。

## 切片的三个位置

切片写作 `sequence[start:stop:step]`，stop 不包含在结果中。省略边界时，正向和反向步长的默认值
不同：

```python
values = [0, 1, 2, 3, 4, 5]

values[1:5:2]  # [1, 3]
values[::-1]   # [5, 4, 3, 2, 1, 0]
values[-3:]    # [3, 4, 5]
```

list 切片会创建浅拷贝，字符串切片会创建新字符串；NumPy 等第三方对象可能返回共享底层存储的
视图，所以切片语义由类型协议决定。

## 常见误区

### `is` 是更快的 `==`

两者语义不同，不能因为性能替换。`is` 不会比较内容。

### 所有空白字符串都是假值

`"   "` 非空，所以是真值。若业务上空白等于未填写，应先执行 `text.strip()`。

### 浮点结果可以直接精确比较

只在值本来就能精确表示或由同一路径产生时才可能安全。一般数值算法使用容差，金融计算使用
十进制模型。

## 面试时怎么表述

> Python 的条件判断使用对象真值协议：优先 `__bool__`，其次 `__len__`，否则实例默认为真。
> `==` 比较值，`is` 比较对象身份，所以判断 `None` 用 `is None`，普通业务值用 `==`。

回答基础类型问题时，不要只背“哪些是假值”，还要说明这套协议如何扩展到自定义对象。
