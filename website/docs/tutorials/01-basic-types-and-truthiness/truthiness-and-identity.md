# Python 真值、相等与对象身份

Python 可以把任何对象当作真或假来判断，这叫真值判断。`==` 用来比较值，`is` 用来判断两边是否为
同一个对象。这三种判断不能混用。

<p class="source-note">对应源码：<code>python/python_interview_practice/01_basic_types.py</code></p>

## 真值判断

`if` 和 `while` 不要求条件一定是 `True` 或 `False`。Python 会把对象转换为真值。

常见假值：

- `None`；
- `False`；
- 数字零，如 `0`、`0.0`、`0j`；
- 空字符串 `""`；
- 空容器，如 `[]`、`()`、`{}`、`set()`。

其他大多数对象都是真值。

<TruthinessExplorer />

### 实例

下面把几种常见值传给 `bool()`，直接查看它们的真值：

```python
values = [0, 1, "", "0", [], [0], None]

for value in values:
    print(repr(value), bool(value))
```

运行结果：

```text
0 False
1 True
'' False
'0' True
[] False
[0] True
None False
```

`0` 是数字零，所以为假。`"0"` 是包含一个字符的非空字符串，所以为真。`[0]` 是包含一个元素的
非空列表，也为真。Python 只看字符串或容器是否为空，不会根据内部内容猜测真假。

判断字符串是否只包含空白时，应先调用 `strip()`：

```python
text = "   "

print(bool(text))
print(bool(text.strip()))
```

运行结果：

```text
True
False
```

### 自定义对象的真值

Python 优先调用对象的 `__bool__()`。没有 `__bool__()` 时，会尝试调用 `__len__()`；长度为 `0` 时
为假。如果两个方法都没有，自定义对象默认为真。

```python
class Cart:
    def __init__(self, items: list[str]) -> None:
        self.items = items

    def __len__(self) -> int:
        return len(self.items)


print(bool(Cart([])))
print(bool(Cart(["Python 图书"])))
```

运行结果：

```text
False
True
```

`bool("False")` 仍然是 `True`，因为它是非空字符串。读取配置或表单中的 `"false"` 时，必须按照
协议明确解析，不能直接使用 `bool(text)`。

## `==` 与 `is`

`==` 比较两个对象的值是否相等。`is` 判断两个表达式是否得到同一个对象。下面创建两个内容相同的
列表，再创建一个别名：

```python
first = [1, 2]
second = [1, 2]
alias = first

print(first == second)
print(first is second)
print(first is alias)
```

运行结果：

```text
True
False
True
```

`first` 和 `second` 是两个内容相同的列表，所以 `==` 为 `True`，`is` 为 `False`。`alias` 直接指向
`first` 所指向的列表，所以 `first is alias` 为 `True`。

普通数值和字符串比较使用 `==`。判断空值使用：

```python
if value is None:
    ...
```

不要使用 `is` 比较普通整数和字符串。解释器可能复用某些对象，但这种内部优化不应成为业务判断依据。
