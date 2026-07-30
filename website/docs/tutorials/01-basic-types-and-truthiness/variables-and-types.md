# Python 变量、基本类型与类型转换

变量是程序中使用的名字。赋值把一个值交给变量名。值有自己的类型，不同类型支持的操作也不同。

<!-- 对应源码：python/python_interview_practice/01_basic_types.py -->

## 变量赋值

赋值使用等号 `=`，基本语法如下：

```python
变量名 = 值
```

等号右边先计算，得到的对象再交给左边的变量名。

### 实例

下面创建姓名、年龄和分数三个变量，再依次打印：

```python
name = "小林"
age = 20
score = 82.5

print(name)
print(age)
print(score)
```

运行结果：

```text
小林
20
82.5
```

这三次赋值分别让：

- `name` 指向字符串 `"小林"`；
- `age` 指向整数 `20`；
- `score` 指向浮点数 `82.5`。

输出来自三个变量当前指向的值。变量本身没有固定类型，类型属于对象。下面让同一个变量先后指向
整数和字符串：

```python
value = 82
print(type(value))

value = "82"
print(type(value))
```

运行结果：

```text
<class 'int'>
<class 'str'>
```

第一次赋值后，`value` 指向整数对象；第二次赋值后，它改为指向字符串对象。虽然这种写法合法，但同一
变量反复表示不同含义会降低代码可读性。

### 多个变量赋值

多个变量可以在一行中同时赋值：

```python
x, y = 10, 20
print(x, y)
```

运行结果：

```text
10 20
```

右边先组成两个值，左边再按位置接收。左右数量不一致会抛出 `ValueError`：

```python
x, y = 10, 20, 30
```

```text
ValueError: too many values to unpack (expected 2)
```

多个变量也可以指向同一个对象：

```python
a = b = []
```

这里不会创建两个列表。`a` 和 `b` 指向同一个列表，修改列表时两边都能看到变化。引用和复制会在
[可变对象、引用与拷贝](../02-mutability-and-copy)中详细说明。

## 变量命名

变量名可以包含字母、数字和下划线，但不能以数字开头。

```python
student_name = "小林"  # 合法
score2 = 90           # 合法
_temporary = 1        # 合法

# 2score = 90         # 非法：不能以数字开头
```

Python 区分大小写，`score` 和 `Score` 是两个不同的变量名。

`if`、`for`、`class` 等关键字不能作为变量名。可以使用 `keyword` 模块查看全部关键字：

```python
import keyword

print(keyword.iskeyword("if"))
print(keyword.iskeyword("score"))
```

运行结果：

```text
True
False
```

变量名通常使用小写字母和下划线，例如 `student_score`。不要使用 `list`、`str`、`sum` 等内置名称
作为变量名，否则会覆盖原来的内置对象。

## 注释与缩进

注释用来说明代码，运行时不会执行。井号 `#` 后面的内容是单行注释：

```python
score = 82  # 学生本次考试分数
```

多行说明通常使用连续的 `#`。三引号字符串可以作为模块、类或函数的文档字符串，但它不是通用的
“多行注释语法”。

Python 使用缩进表示代码块，一般使用四个空格：

```python
score = 82

if score >= 60:
    print("通过")
    print("可以继续学习下一章")

print("成绩处理完成")
```

运行结果：

```text
通过
可以继续学习下一章
成绩处理完成
```

两条缩进语句属于 `if` 代码块。最后一条语句没有缩进，因此不受 `if` 控制。

同一个代码块的缩进必须一致。混用不同数量的空格，或者混用 Tab 和空格，可能产生
`IndentationError` 或 `TabError`。

## 基本数据类型

类型决定一个值可以参加哪些操作。常用内置类型如下：

| 类型 | 示例 | 说明 |
| --- | --- | --- |
| `int` | `82`、`-3` | 整数 |
| `float` | `82.5`、`-0.25` | 浮点数 |
| `complex` | `3 + 4j` | 复数 |
| `bool` | `True`、`False` | 布尔值 |
| `str` | `"Python"` | 字符串 |
| `list` | `[1, 2, 3]` | 有序、可修改的序列 |
| `tuple` | `(1, 2, 3)` | 有序、不可修改的序列 |
| `set` | `{1, 2, 3}` | 不重复元素的集合 |
| `dict` | `{"name": "小林"}` | 键与值的映射 |
| `NoneType` | `None` | 表示没有值或结果缺失 |

容器类型会在[容器：列表、元组、字典与集合](../04-containers-and-sorting)中详细说明。

### 查看对象类型

`type()` 返回对象的实际类型。下面查看四个值的类型：

```python
print(type(82))
print(type(82.5))
print(type("Python"))
print(type(None))
```

运行结果：

```text
<class 'int'>
<class 'float'>
<class 'str'>
<class 'NoneType'>
```

`isinstance()` 判断对象是否属于指定类型。它返回 `True` 或 `False`：

```python
score = 82

print(isinstance(score, int))
print(isinstance(score, str))
print(isinstance(score, (int, float)))
```

运行结果：

```text
True
False
True
```

第三个判断表示：只要 `score` 是 `int` 或 `float` 中的一种，就返回 `True`。

`isinstance()` 会考虑继承关系，`type(value) is SomeType` 只检查实际类型是否完全相同。普通类型判断
通常优先使用 `isinstance()`。

## 常用内置函数

内置函数不需要导入，可以直接调用。下面这些函数经常用于数字、字符串和容器：

| 函数 | 作用 |
| --- | --- |
| `len(value)` | 返回字符串或容器中的元素数量 |
| `sum(values)` | 计算一组数值的总和 |
| `min(values)` | 返回最小值 |
| `max(values)` | 返回最大值 |
| `abs(number)` | 返回绝对值 |
| `round(number, digits)` | 按指定小数位数舍入 |
| `any(values)` | 只要有一个元素为真，就返回 `True` |
| `all(values)` | 所有元素都为真时，返回 `True` |

下面对同一组数字做统计和舍入：

```python
numbers = [-3, 7, 2]

print(len(numbers))
print(sum(numbers))
print(min(numbers))
print(max(numbers))
print(abs(numbers[0]))
print(round(3.14159, 2))
```

运行结果：

```text
3
6
-3
7
3
3.14
```

`len()` 得到元素数量。`sum()` 把三个数相加。`min()` 和 `max()` 分别取最小值与最大值。
`abs(-3)` 得到 `3`，`round(3.14159, 2)` 保留两位小数。

`round()` 遇到正好位于两个结果中间的值时，会选择偶数一侧：

```python
print(round(2.5))
print(round(3.5))
```

运行结果：

```text
2
4
```

浮点数本身是近似值，因此部分小数的舍入结果可能与十进制直觉不同。金额计算通常使用
`decimal.Decimal`。

### `any()` 与 `all()`

`any()` 常用于判断“是否至少有一个满足条件”，`all()` 常用于判断“是否全部满足条件”：

> 进阶预览：下面的 `score >= 90 for score in scores` 是生成器表达式，可以先把它读作
> “逐个检查 `scores` 中的分数”。生成器表达式将在
> [生成器与 itertools](../03-functions-and-generators/generators-and-itertools#生成器表达式)中详细说明。

```python
scores = [82, 91, 55]

print(any(score >= 90 for score in scores))
print(all(score >= 60 for score in scores))
print(any([]))
print(all([]))
```

运行结果：

```text
True
False
False
True
```

列表中有一个分数不低于 `90`，所以第一行是 `True`。并非所有分数都及格，所以第二行是 `False`。
`any()` 只有遇到真值元素才返回 `True`，空列表中没有这样的元素，所以 `any([])` 为 `False`。
`all()` 只有遇到假值元素才返回 `False`，空列表中也没有这样的元素，所以 `all([])` 为 `True`。

### `map()` 与 `filter()`

`map()` 对每个元素调用函数，`filter()` 只保留让判断函数返回真值的元素：

> 进阶预览：下面会先定义两个函数，并在后面用到推导式。如果这些写法还不熟悉，可以先关注
> `map()` 是“逐个转换”、`filter()` 是“按条件筛选”；函数和推导式分别见
> [函数定义、调用与参数](../03-functions-and-generators/function-basics)和
> [集合、并集交集与推导式](../04-containers-and-sorting/sets-and-comprehensions)。

```python
def square(number: int) -> int:
    return number * number


def is_even(number: int) -> bool:
    return number % 2 == 0


numbers = [1, 2, 3, 4]

print(list(map(square, numbers)))
print(list(filter(is_even, numbers)))
```

运行结果：

```text
[1, 4, 9, 16]
[2, 4]
```

`map()` 和 `filter()` 返回迭代器，示例使用 `list()` 一次取出全部结果。

简单的转换或筛选通常使用推导式，更容易直接看出规则：

```python
squares = [number * number for number in numbers]
even_numbers = [number for number in numbers if number % 2 == 0]
```

已经有 `square`、`is_even` 这类命名函数时，`map()` 和 `filter()` 也很清楚。只为它们临时编写复杂
`lambda` 时，推导式通常更容易阅读。

## 类型转换

类型转换会根据已有值创建另一种类型的值。常用类型可以通过对应的类型函数转换：

```python
print(int("82"))
print(float("82.5"))
print(str(82))
print(list("ABC"))
```

运行结果：

```text
82
82.5
82
['A', 'B', 'C']
```

结果中的第三行看起来仍然是 `82`，但它已经是字符串。可以使用 `repr()` 看得更清楚：

```python
text = str(82)
print(repr(text))
print(type(text))
```

运行结果：

```text
'82'
<class 'str'>
```

转换要求原始内容符合目标类型的格式：

```python
int("八十二")
```

```text
ValueError: invalid literal for int() with base 10: '八十二'
```

### `input()` 返回字符串

`input()` 用于读取键盘输入。无论用户输入数字还是文字，返回值都是 `str`。

```python
age_text = input("请输入年龄：")

print(repr(age_text))
print(type(age_text))
```

假设输入 `20`，运行结果为：

```text
请输入年龄：20
'20'
<class 'str'>
```

需要数值计算时应先转换：

```python
age_text = input("请输入年龄：").strip()
age = int(age_text)

print(age + 1)
```

假设输入 `20`，运行结果为：

```text
请输入年龄：20
21
```

`strip()` 去掉输入两端的空白，`int()` 再把数字文本转换为整数。无效输入的处理方式参见
[异常与上下文管理器](../06-exceptions-and-context-managers)。
