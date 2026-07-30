# Python 字符串

字符串是 Python 中表示文本的类型，类型名是 `str`。字符串可以读取、切片、查找、替换和格式化，
但不能原地修改。

<!-- 对应源码：python/python_interview_practice/01_basic_types.py -->

## 字符串

字符串是由 Unicode 字符组成的不可变序列。可以使用单引号、双引号或三引号创建字符串：

```python
single = 'Python'
double = "Python"
multiple = """第一行
第二行"""
```

单引号和双引号没有类型区别。选择一种能减少转义的写法即可：

```python
message = "I'm learning Python"
```

### 转义字符和原始字符串

反斜杠 `\` 用于表示换行、制表符等特殊字符。下面演示 `\n` 和 `\t`：

```python
print("第一行\n第二行")
print("制表符：\t结束")
```

运行结果：

```text
第一行
第二行
制表符：	结束
```

路径和正则表达式中经常使用原始字符串，前缀 `r` 会让大多数反斜杠保持原样：

```python
print(r"C:\new\test")
```

运行结果：

```text
C:\new\test
```

### 索引

索引用来读取一个字符。字符串下标从 `0` 开始，负数下标从末尾开始：

```python
text = "Python"

print(text[0])
print(text[1])
print(text[-1])
```

运行结果：

```text
P
y
n
```

长度为 6 的字符串，有效正向下标是 `0` 到 `5`。访问 `text[6]` 会抛出 `IndexError`。

### 切片

切片用来取得一段字符串。语法如下：

```python
字符串[start:stop:step]
```

`start` 是起始位置，`stop` 是结束位置但不包含在结果中，`step` 是步长。

```python
text = "Python"

print(text[1:4])
print(text[:2])
print(text[2:])
print(text[::2])
print(text[::-1])
```

运行结果：

```text
yth
Py
thon
Pto
nohtyP
```

切片超过字符串边界通常不会报错，而是返回实际能取得的部分。

### 常用字符串方法

下面的例子去除空白、转换大小写、替换文字，并按空白拆分字符串：

```python
text = "  python interview  "

print(repr(text.strip()))
print(repr(text.upper()))
print(repr(text.replace("interview", "practice")))
print(text.split())
```

运行结果：

```text
'python interview'
'  PYTHON INTERVIEW  '
'  python practice  '
['python', 'interview']
```

| 方法 | 说明 |
| --- | --- |
| `strip()` | 删除两端空白 |
| `lower()` | 转为小写 |
| `upper()` | 转为大写 |
| `replace(old, new)` | 替换内容 |
| `split(sep)` | 按分隔符拆成列表 |
| `join(items)` | 把多个字符串连接起来 |
| `startswith(prefix)` | 判断开头 |
| `endswith(suffix)` | 判断结尾 |

前四行分别显示四个方法的返回值。原字符串不会被这些方法直接修改。

字符串不可变，上表中的方法都不会原地修改字符串，而是返回新的结果。返回类型取决于具体方法：
例如 `upper()` 返回新字符串，`split()` 返回列表，`startswith()` 返回布尔值。下面以
`upper()` 为例：

```python
text = "python"
upper_text = text.upper()

print(text)
print(upper_text)
```

运行结果：

```text
python
PYTHON
```

### f-string

f-string 可以把变量或表达式放进字符串。字符串前要加字母 `f`：

```python
name = "小林"
score = 82

print(f"{name} 的分数是 {score}")
print(f"提高 5 分后是 {score + 5}")
```

运行结果：

```text
小林 的分数是 82
提高 5 分后是 87
```

第一行把 `name` 和 `score` 放入文本。第二行会先计算 `score + 5`，再把结果放入字符串。

### f-string 格式说明符

冒号后面可以写格式说明符：

```python
price = 12.5
ratio = 0.376
count = 7

print(f"{price:.2f}")
print(f"{ratio:.1%}")
print(f"{count:04d}")
print(f"{price:>8.2f}")
```

运行结果：

```text
12.50
37.6%
0007
   12.50
```

- `.2f` 把浮点数显示为两位小数；
- `.1%` 先乘以 `100`，再显示一位小数和百分号；
- `04d` 把整数显示为四位，不足部分在左侧补 `0`；
- `>8.2f` 使用宽度 `8` 并右对齐，同时保留两位小数。

格式说明符只改变显示结果，不会修改原来的数值。

## `print()` 的 `sep` 与 `end`

`print()` 默认用空格分隔多个值，并在结尾写入换行。`sep` 可以修改分隔符，`end` 可以修改结尾：

```python
print("2026", "07", "30", sep="-")
print("加载", end="...")
print("完成")
```

运行结果：

```text
2026-07-30
加载...完成
```

第一行使用 `-` 分隔三个值。第二次 `print()` 把结尾改为 `...`，没有换行，所以“完成”紧接在后面。
`sep` 和 `end` 都要作为关键字参数传入。

## `str`、`bytes` 与 UTF-8

`str` 保存 Unicode 文本，`bytes` 保存原始字节。文件、网络和系统接口最终传输的是字节，因此要在
文本与二进制边界做编码或解码。

`str.encode()` 把文本编码成字节，`bytes.decode()` 把字节解码成文本：

```python
text = "Python你好"
data = text.encode("utf-8")
decoded = data.decode("utf-8")

print(data)
print(decoded)
print(decoded == text)
```

运行结果：

```text
b'Python\xe4\xbd\xa0\xe5\xa5\xbd'
Python你好
True
```

UTF-8 用一个字节保存 ASCII 字符，用多个字节保存中文等其他字符。编码和解码使用同一字符编码时，
可以还原原文本。

### 编码不匹配

字节本身不记录“使用了哪种编码”。调用方必须知道正确编码：

```python
data = "你好".encode("utf-8")
data.decode("ascii")
```

运行会抛出 `UnicodeDecodeError`，因为这组 UTF-8 字节不是合法 ASCII。

使用错误但能够解码的编码，还可能得到乱码而不报错。处理文本文件时，应使用文本模式并明确
`encoding="utf-8"`；读取图片、压缩包等二进制数据时，应使用 `rb` 或 `wb` 模式并处理 `bytes`。
通常只在输入和输出边界编码或解码，程序内部统一使用 `str`。

## 正则表达式

正则表达式用模式查找或替换文本。Python 通过标准库 `re` 提供正则功能：

```python
import re


text = "订单 A-102 和 B-205 已创建"
pattern = r"[A-Z]-\d+"

first = re.search(pattern, text)
print(first.group() if first else None)
print(re.findall(pattern, text))
print(re.sub(pattern, "编号", text))
```

运行结果：

```text
A-102
['A-102', 'B-205']
订单 编号 和 编号 已创建
```

- `re.search()` 查找第一个匹配，找到时返回 `Match` 对象，找不到时返回 `None`；
- `re.findall()` 返回所有不重叠匹配；
- `re.sub()` 返回替换后的新字符串。

正则模式经常包含反斜杠。写成原始字符串 `r"[A-Z]-\d+"`，可以让 `\d` 原样交给正则表达式引擎，
表示一位数字。原始字符串只影响 Python 如何读取字符串，正则表达式仍会解释其中的 `\d`、`\s`
等模式。

简单的固定文本查找和替换优先使用 `in`、`str.find()`、`str.replace()`。只有规则确实需要模式匹配时，
再使用正则表达式。
