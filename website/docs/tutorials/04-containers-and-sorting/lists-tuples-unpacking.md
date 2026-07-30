# Python 列表、元组与序列解包

列表和元组都能按顺序保存多个值，但列表可以修改，元组不能修改。掌握索引、切片、增删元素和序列解包后，才能在后面的字典、集合与函数参数中熟练组织数据。

<p class="source-note">对应源码：<code>python/python_interview_practice/01_basic_types.py</code></p>

## 列表的创建和访问

list 是有序、可变序列，使用方括号创建：

```python
languages = ["Python", "Java", "Go"]

print(languages[0])
print(languages[-1])
print(languages[1:3])
```

运行结果：

```text
Python
Go
['Java', 'Go']
```

索引从 `0` 开始，负数索引从末尾开始。访问不存在的索引会抛出 `IndexError`。

切片语法是 `sequence[start:stop:step]`，其中 `stop` 不包含在结果内：

```python
numbers = [0, 1, 2, 3, 4, 5]

print(numbers[:3])
print(numbers[::2])
print(numbers[::-1])
```

运行结果：

```text
[0, 1, 2]
[0, 2, 4]
[5, 4, 3, 2, 1, 0]
```

切片会创建新的外层 list，但元素仍是原对象的引用。嵌套列表的复制行为见
[可变对象、引用与拷贝](../02-mutability-and-copy)。

## 修改列表

列表支持按索引赋值和切片赋值：

```python
numbers = [1, 2, 3, 4]

numbers[0] = 10
numbers[1:3] = [20, 30, 40]

print(numbers)
```

运行结果：

```text
[10, 20, 30, 40, 4]
```

切片赋值可以改变列表长度。常用列表方法如下：

| 方法 | 作用 |
| --- | --- |
| `append(value)` | 在末尾添加一个元素 |
| `extend(values)` | 在末尾依次添加多个元素 |
| `insert(index, value)` | 在指定位置插入元素 |
| `pop(index)` | 删除并返回指定位置的元素 |
| `remove(value)` | 删除第一个相等的元素 |
| `clear()` | 删除全部元素 |
| `index(value)` | 返回第一个相等元素的索引 |
| `count(value)` | 统计相等元素的数量 |

```python
names = ["小林", "小周"]

names.append("小陈")
names.extend(["小吴", "小郑"])
removed = names.pop(1)

print(names)
print(removed)
```

运行结果：

```text
['小林', '小陈', '小吴', '小郑']
小周
```

`append()` 把参数作为一个元素加入，`extend()` 则遍历参数并逐个加入：

```python
values = [1, 2]
values.append([3, 4])
print(values)

values = [1, 2]
values.extend([3, 4])
print(values)
```

运行结果：

```text
[1, 2, [3, 4]]
[1, 2, 3, 4]
```

`append()`、`extend()`、`sort()` 等原地修改方法通常返回 `None`。不要写
`names = names.append("小陈")`，否则变量会被重新绑定为 `None`。

## 元组

tuple 是有序序列，创建后不能替换、添加或删除自己的元素：

```python
point = (120.1, 30.2)

print(point[0])
print(point[-1])
```

运行结果：

```text
120.1
30.2
```

单元素 tuple 必须保留逗号：

```python
print(type(("Python",)))
print(type(("Python")))
```

运行结果：

```text
<class 'tuple'>
<class 'str'>
```

圆括号经常可以省略，真正创建 tuple 的是逗号：

```python
result = 82, "通过"
print(result)
```

运行结果：

```text
(82, '通过')
```

tuple 不允许替换元素，但元素本身可能是可变对象：

```python
record = ("小林", ["Python"])
record[1].append("SQL")

print(record)
```

运行结果：

```text
('小林', ['Python', 'SQL'])
```

因此，“tuple 不可变”指 tuple 保存的元素引用不能被替换，不代表引用指向的所有对象都会变成不可变。

## 序列解包

list 和 tuple 都支持解包：

```python
name, score = ("小林", 82)
print(name)
print(score)
```

运行结果：

```text
小林
82
```

左右数量不一致时会抛出 `ValueError`。使用星号可以收集剩余元素：

```python
first, *middle, last = [10, 20, 30, 40, 50]

print(first)
print(middle)
print(last)
```

运行结果：

```text
10
[20, 30, 40]
50
```

交换变量也使用了解包：

```python
left = 1
right = 2
left, right = right, left

print(left, right)
```

运行结果：

```text
2 1
```
