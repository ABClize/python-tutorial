# Python 浅拷贝与深拷贝

浅拷贝只创建新的外层对象，内部元素仍可能与原对象共享。深拷贝会继续复制内部的可变对象。
嵌套列表最容易看出两者的区别。

<!-- 对应源码：python/python_interview_practice/03_collections_copy.py -->

## 浅拷贝

浅拷贝会创建一个新的外层对象，外层对象中的元素引用仍然来自原对象。

列表浅拷贝的常用写法：

```python
copied = original.copy()
copied = list(original)
copied = original[:]
```

通用的浅拷贝函数：

```python
import copy

copied = copy.copy(original)
```

### 一层列表

下面复制一个只包含字符串的列表，再向副本追加元素：

```python
original = ["Python", "SQL"]
copied = original.copy()

copied.append("Git")

print(original)
print(copied)
print(original is copied)
```

运行结果：

```text
['Python', 'SQL']
['Python', 'SQL', 'Git']
False
```

`original.copy()` 创建了新的外层列表：

```text
original ──> ["Python", "SQL"]
copied   ──> ["Python", "SQL", "Git"]
```

两个列表的内容不同，`original is copied` 也是 `False`。向 `copied` 追加元素只修改新列表，
不会修改 `original`。

如果列表元素都是整数、字符串等不可变对象，浅拷贝通常已经能够满足独立修改外层列表的需要。

## 嵌套对象的浅拷贝

嵌套列表包含外层列表和内层列表。下面检查浅拷贝后的对象身份：

```python
original = [["Python", "SQL"], ["Git"]]
copied = original.copy()

print(original is copied)
print(original[0] is copied[0])
print(original[1] is copied[1])
```

运行结果：

```text
False
True
True
```

结果说明：

- `original` 和 `copied` 是两个不同的外层列表；
- 两个外层列表的第一个元素指向同一个内层列表；
- 两个外层列表的第二个元素也指向同一个内层列表。

对象关系如下：

```text
original ──> outer list A ─┬──> ["Python", "SQL"]
                           └──> ["Git"]

copied   ──> outer list B ─┬──> ["Python", "SQL"]
                           └──> ["Git"]
```

因为内层列表仍然共享，所以修改内层列表时，两边都会看到变化：

```python
original = [["Python", "SQL"], ["Git"]]
copied = original.copy()

original[0].append("FastAPI")

print(original)
print(copied)
```

运行结果：

```text
[['Python', 'SQL', 'FastAPI'], ['Git']]
[['Python', 'SQL', 'FastAPI'], ['Git']]
```

`original[0]` 和 `copied[0]` 是同一个列表，`append()` 修改的正是这个共享对象。

### 替换元素不会传播

如果替换外层列表中的一个元素，另一个外层列表不会跟着替换：

```python
original = [["Python", "SQL"], ["Git"]]
copied = original.copy()

original[0] = ["Java"]

print(original)
print(copied)
```

运行结果：

```text
[['Java'], ['Git']]
[['Python', 'SQL'], ['Git']]
```

`original[0] = ["Java"]` 修改的是 `original` 这个外层列表中的元素引用。`copied` 是另一个外层列表，
它的第一个元素仍然指向原来的 `["Python", "SQL"]`。

### 引用关系图

图中的每个矩形表示一个对象，箭头表示对象引用。切换复制方式后，可以比较外层对象和内层对象是否仍然
共享。

<MutabilityDiagram />

浅拷贝模式中：

- `original` 和 `copied` 分别指向两个外层列表；
- 两个外层列表都指向相同的两个内层列表；
- 修改 `original[0]` 指向的内层列表时，`copied[0]` 也会读取到修改结果。

## 深拷贝

深拷贝会递归复制对象及其包含的子对象。通常使用 `copy.deepcopy()`：

```python
import copy

copied = copy.deepcopy(original)
```

### 实例

下面深拷贝嵌套列表，再修改原对象中的第一个内层列表：

```python
import copy

original = [["Python", "SQL"], ["Git"]]
copied = copy.deepcopy(original)

original[0].append("FastAPI")

print(original)
print(copied)
print(original[0] is copied[0])
```

运行结果：

```text
[['Python', 'SQL', 'FastAPI'], ['Git']]
[['Python', 'SQL'], ['Git']]
False
```

原对象中多了 `"FastAPI"`，副本没有变化，两个内层列表也不是同一个对象。深拷贝创建了新的外层列表，
也创建了新的内层列表。

### 深拷贝不是简单复制所有对象

`deepcopy()` 会根据对象类型决定怎样复制：

- 可变容器通常会创建新对象，并递归处理其中的元素；
- 不可变对象可能直接复用；
- 已经复制过的对象会记录在 memo 中；
- 自定义类可以通过 `__deepcopy__()` 定义复制行为。

memo 用于避免重复复制同一个对象，并处理循环引用：

```python
import copy

original = []
original.append(original)

copied = copy.deepcopy(original)

print(copied is copied[0])
print(copied is original)
```

运行结果：

```text
True
False
```

`original` 是一个包含自身引用的列表。深拷贝后的 `copied` 也保持这个循环结构，但它和
`original` 是两个不同对象。
