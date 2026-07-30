# Python 字符串

字符串是 Python 中表示文本的类型，类型名是 `str`。字符串可以读取、切片、查找、替换和格式化，
但不能原地修改。

<p class="source-note">对应源码：<code>python/python_interview_practice/01_basic_types.py</code></p>

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

字符串不可变，这些方法都会返回新字符串：

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
