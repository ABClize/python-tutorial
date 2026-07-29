# 可变对象、引用与拷贝

很多“列表怎么跟着变了”的问题，本质上不是列表语法问题，而是没有分清变量名、对象和引用。
只要先画出对象图，赋值、函数传参、浅拷贝和深拷贝就会变成同一套规则。

<p class="source-note">对应源码：<code>python/python_interview_practice/03_collections_copy.py</code></p>

## 变量保存的是引用

执行 `b = a` 时，Python 不会复制 `a` 指向的对象，而是让名字 `b` 指向同一个对象。
可以把变量理解为贴在对象上的标签，而不是装着对象的盒子。

```python
a = [1, 2]
b = a

b.append(3)

print(a)       # [1, 2, 3]
print(a is b)  # True
```

`append()` 修改了共享列表本身，所以通过 `a` 或 `b` 观察到的内容都会变化。相反，重新绑定
`b = [4, 5]` 只会移动 `b` 这个名字，不会修改原列表。

## 浅拷贝只复制一层

嵌套容器需要分别观察外层和内层对象。下面的交互图使用同一份初始数据，分别执行直接赋值、
浅拷贝和深拷贝。

```python
import copy

original = [[1, 2], [3, 4]]
copied = original.copy()          # 浅拷贝
# copied = copy.deepcopy(original)  # 深拷贝

original[0].append(99)
```

<MutabilityDiagram />

### 如何读这张图

每一个矩形代表一个真实对象，箭头代表“指向”。浅拷贝会创建新的外层列表，但新列表中的元素
仍是对原有内层列表的引用。因此：

- `original is copied` 为 `False`，因为外层对象不同；
- `original[0] is copied[0]` 为 `True`，因为第一个内层对象仍被共享；
- 修改 `original[0]` 会影响两边，替换 `original[0]` 则只改变一边的外层引用。

深拷贝会递归复制对象图，但也不是“任何对象都无条件复制”。不可变对象可能被复用，自定义类型
还能通过 `__deepcopy__` 定义行为。面试中说“深拷贝递归复制可复制的子对象”比“全部复制”
更准确。

## 函数参数也是一次赋值

函数调用会把实参指向的对象绑定给形参。Python 既不是传统意义上的“按值复制对象”，也不是
允许函数重新绑定调用方变量的“按引用传递”；更准确的说法是 **对象引用按值传递**。

```python
def update(items: list[int]) -> None:
    items.append(3)  # 修改共享对象
    items = [9, 9]   # 只重新绑定局部名字


numbers = [1, 2]
update(numbers)
print(numbers)  # [1, 2, 3]
```

`append()` 沿着引用找到列表并修改它；后面的赋值只让局部变量 `items` 指向新列表，因此调用者的
`numbers` 不会变成 `[9, 9]`。

## 可变性、可哈希与对象身份

可变与可哈希不是完全相反的定义，但内置可变容器通常不可哈希，因为作为 dict key 或 set 元素时，
哈希值必须在生命周期内保持稳定。

| 对象 | 通常可变 | 通常可哈希 |
| --- | --- | --- |
| `int`、`str`、`bytes` | 否 | 是 |
| `tuple` | 否 | 元素都可哈希时才是 |
| `list`、`dict`、`set` | 是 | 否 |
| `frozenset` | 否 | 元素可哈希时是 |

自定义类默认按身份哈希；一旦定义基于内容的 `__eq__`，Python 通常会禁用默认哈希，避免“值相等但
哈希不一致”。只有相等依赖的字段不可变时，才适合实现 `__hash__`。

## 复制协议与自定义对象

`copy.copy()` 会调用对象的 `__copy__`，`copy.deepcopy()` 会使用 `__deepcopy__`，并通过 memo
记录已经复制的对象。这既能保留对象图中的共享关系，也能避免循环引用导致无限递归。

```python
import copy

original = []
original.append(original)

cloned = copy.deepcopy(original)
cloned is cloned[0]  # True：循环结构被正确保留
```

深拷贝数据库连接、锁、文件句柄或包含外部资源的对象通常没有合理语义。此类类型应禁止复制，或提供
明确的“导出值对象 / 重建资源”接口。

## 复制与序列化不是同一件事

深拷贝在当前进程中重建对象图；JSON 等序列化把有限类型转换为跨进程或跨语言数据。序列化通常会
丢失对象身份、共享引用、方法和部分精度，因此不能把 `json.loads(json.dumps(obj))` 当通用深拷贝。

## 可变默认参数为何危险

默认参数在 `def` 语句执行时计算一次，而不是每次调用时重新创建。

```python
def collect(value: int, bucket: list[int] = []) -> list[int]:
    bucket.append(value)
    return bucket


collect(1)  # [1]
collect(2)  # [1, 2]，复用了同一个默认列表
```

通常用 `None` 作为“未提供”的哨兵，在函数内部创建新对象：

```python
def collect(value: int, bucket: list[int] | None = None) -> list[int]:
    if bucket is None:
        bucket = []
    bucket.append(value)
    return bucket
```

同样的问题也会出现在 dataclass 字段中。应使用 `field(default_factory=list)`，而不是让多个实例
共享同一个列表。

## 常见误区

### `==` 和 `is` 可以互换

`==` 比较值是否相等，`is` 比较是否为同一个对象。业务值比较通常用 `==`；`is` 主要用于
`None`、单例哨兵或明确的对象身份判断。

### 切片就是深拷贝

`items[:]` 和 `list(items)` 都只创建新的外层列表，语义仍是浅拷贝。只要元素本身是可变对象，
内部共享关系就仍然存在。

### 元组一定不可变

元组不能替换自己的元素引用，但元素指向的对象仍可能可变。例如 `([1],)` 中的列表仍能
`append()`。不可变的是元组结构，不是它能触达的整张对象图。

## 面试时怎么表述

可以先给出结论，再画对象图解释：

> Python 变量绑定的是对象引用。直接赋值只复制引用；浅拷贝创建新的外层容器，但复用元素引用；
> 深拷贝递归构造独立的可复制子对象。判断修改是否传播，要看被修改的那个对象是否仍被共享。

最后补一句工程取舍：深拷贝成本高，也可能掩盖所有权问题；如果数据结构允许，优先使用不可变值、
显式构造新对象，或清楚定义谁拥有修改权。
