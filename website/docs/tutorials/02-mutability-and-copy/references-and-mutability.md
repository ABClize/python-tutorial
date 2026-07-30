# Python 引用、可变对象与不可变对象

变量名通过引用指向对象。给另一个变量赋值时，复制的通常是引用，不是对象本身。可变对象可以原地修改，
不可变对象不能原地修改。

<p class="source-note">对应源码：<code>python/python_interview_practice/03_collections_copy.py</code></p>

## 对象引用

下面的代码只创建一个列表，然后让两个变量引用它：

```python
original = ["Python", "SQL"]
copied = original
```

两个变量都指向同一个列表：

```text
original ─┐
          ├──> ["Python", "SQL"]
copied ───┘
```

可以使用 `is` 检查两个变量是否指向同一个对象：

```python
original = ["Python", "SQL"]
copied = original

print(original is copied)
```

运行结果：

```text
True
```

结果是 `True`，说明两边指向同一个对象。`copied = original` 复制了对象引用，没有创建新列表。

### `id()` 查看对象身份

`id()` 返回对象在本次运行期间的身份标识：

```python
original = [1, 2]
copied = original

print(id(original) == id(copied))
```

运行结果：

```text
True
```

同一个对象只有一个身份标识。不同进程或不同运行中的具体 id 数值没有可比较意义，业务代码通常也不应
依赖这些数值。

## 修改对象与重新赋值

修改对象和重新给变量赋值是两种不同的操作。

### 修改共享对象

下面先让两个变量引用同一个列表，再通过 `copied` 追加元素：

```python
original = [1, 2]
copied = original

copied.append(3)

print(original)
print(copied)
```

运行结果：

```text
[1, 2, 3]
[1, 2, 3]
```

执行过程：

1. `original` 指向列表 `[1, 2]`；
2. `copied = original` 让 `copied` 指向同一个列表；
3. `copied.append(3)` 修改这个列表；
4. 通过任意一个变量读取时，看到的都是修改后的对象。

### 重新给变量赋值

下面把 `copied` 重新赋值为一个新列表：

```python
original = [1, 2]
copied = original

copied = [9, 9]

print(original)
print(copied)
```

运行结果：

```text
[1, 2]
[9, 9]
```

`copied = [9, 9]` 创建新列表并让 `copied` 指向它。这个操作没有修改原来的 `[1, 2]`：

```text
original ──> [1, 2]
copied   ──> [9, 9]
```

两个变量现在指向不同列表，所以输出也不同。判断操作是否影响其他变量时，先看它是在修改对象，
还是只在改变某个变量的指向。

## 可变对象与不可变对象

可变对象创建后可以原地修改，不可变对象创建后不能修改自身内容。

| 类型 | 是否可变 | 常见操作 |
| --- | --- | --- |
| `list` | 可变 | `append()`、`extend()`、元素赋值 |
| `dict` | 可变 | 增加、修改或删除键值对 |
| `set` | 可变 | `add()`、`remove()` |
| `bytearray` | 可变 | 修改字节 |
| `int`、`float`、`bool` | 不可变 | 运算后产生新对象 |
| `str`、`bytes` | 不可变 | 方法返回新对象 |
| `tuple` | 结构不可变 | 不能替换元组元素 |
| `frozenset` | 不可变 | 不能增加或删除元素 |

### 不可变字符串

字符串是不可变对象。`upper()` 会返回新字符串，不会修改原字符串：

```python
text = "python"
alias = text

text = text.upper()

print(text)
print(alias)
```

运行结果：

```text
PYTHON
python
```

`upper()` 没有修改原字符串，而是返回新字符串 `"PYTHON"`。随后 `text` 改为指向新字符串，
`alias` 仍然指向原来的 `"python"`。

下面的写法会报错：

```python
text = "python"
text[0] = "P"
```

```text
TypeError: 'str' object does not support item assignment
```

字符串不能原地替换字符。需要修改时，应构造一个新字符串：

```python
text = "python"
text = "P" + text[1:]

print(text)
```

运行结果：

```text
Python
```

### 元组中的可变对象

元组不能替换元素，但元组中的元素本身可能是可变对象。下面的第二个元素是列表：

```python
record = ("小林", ["Python"])
record[1].append("SQL")

print(record)
```

运行结果：

```text
('小林', ['Python', 'SQL'])
```

输出中的元组仍有两个元素。变化的是第二个元素所指向的列表，不是元组结构。
