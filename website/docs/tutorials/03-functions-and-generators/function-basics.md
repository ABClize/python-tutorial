# Python 函数定义、调用与参数

函数把一段可以重复使用的操作命名起来。要正确调用函数，需要理解返回值、位置参数、关键字参数、默认参数，以及星号参数怎样收集额外输入。本页先把这些基础规则逐一讲清楚。

<p class="source-note">对应源码：<code>python/python_interview_practice/02_functions_scope.py</code></p>

## 定义和调用函数

使用 `def` 定义函数：

```python
def calculate_price(price: float, discount: float) -> float:
    result = price * discount
    return round(result, 2)


final_price = calculate_price(100, 0.8)
print(final_price)
```

运行结果：

```text
80.0
```

函数定义由四部分组成：

- `def` 表示开始定义函数；
- `calculate_price` 是函数名；
- 圆括号中的 `price` 和 `discount` 是形参；
- 缩进代码是函数体，`return` 把结果返回给调用方。

定义函数时不会执行函数体。只有运行 `calculate_price(100, 0.8)` 时，Python 才会把 `100` 和
`0.8` 分别绑定到两个形参，然后执行函数体。

函数应先定义再调用。函数名遵循变量命名规则，通常使用小写字母和下划线，例如
`calculate_price()`、`find_user()`。

## 返回值与 `None`

`return` 会立即结束当前函数，并把后面的值交给调用方：

```python
def classify_score(score: int) -> str:
    if score >= 60:
        return "通过"
    return "未通过"


print(classify_score(82))
print(classify_score(40))
```

运行结果：

```text
通过
未通过
```

函数没有执行到显式的 `return` 时，返回值是 `None`：

```python
def show_message(message: str) -> None:
    print(message)


result = show_message("保存成功")
print(result)
```

运行结果：

```text
保存成功
None
```

打印和返回是两件事：

- `print()` 把内容写到标准输出，主要供人阅读；
- `return` 把数据交给调用方，返回值可以继续计算、保存或测试。

一个函数可以返回多个值：

```python
def minimum_and_maximum(values: list[int]) -> tuple[int, int]:
    return min(values), max(values)


smallest, largest = minimum_and_maximum([8, 3, 12, 5])
print(smallest, largest)
```

运行结果：

```text
3 12
```

这里实际返回的是 tuple，左侧使用序列解包分别取得两个元素。

## 位置参数和关键字参数

调用函数时，实参可以按位置传递，也可以写出参数名：

```python
def create_user(name: str, age: int, city: str) -> dict[str, object]:
    return {"name": name, "age": age, "city": city}


print(create_user("小林", 20, "杭州"))
print(create_user(city="上海", name="小周", age=22))
```

运行结果：

```text
{'name': '小林', 'age': 20, 'city': '杭州'}
{'name': '小周', 'age': 22, 'city': '上海'}
```

位置参数依赖顺序。关键字参数显式写出名称，顺序可以调整。一个调用中可以先写位置参数，再写关键字
参数，但不能把位置参数放在关键字参数之后。

关键字参数适合布尔开关、多个同类型参数以及需要强调含义的调用：

```python
def connect(host: str, port: int, use_ssl: bool) -> str:
    return f"{host}:{port}, SSL={use_ssl}"


print(connect("example.com", 443, use_ssl=True))
```

运行结果：

```text
example.com:443, SSL=True
```

## 默认参数

形参可以提供默认值：

```python
def greet(name: str, greeting: str = "你好") -> str:
    return f"{greeting}，{name}"


print(greet("小林"))
print(greet("小周", "早上好"))
```

运行结果：

```text
你好，小林
早上好，小周
```

没有默认值的参数必须放在有默认值的参数之前。默认值在执行 `def` 时只计算一次，因此不要直接使用
list、dict、set 等可变对象作为默认值：

```python
def add_tag(tag: str, tags: list[str] | None = None) -> list[str]:
    if tags is None:
        tags = []
    tags.append(tag)
    return tags


print(add_tag("Python"))
print(add_tag("SQL"))
```

运行结果：

```text
['Python']
['SQL']
```

相关原因见[函数参数与可变默认值](../02-mutability-and-copy/function-arguments-and-defaults#可变默认参数)。

## 仅限位置和仅限关键字的参数

参数列表中的 `/` 和 `*` 可以限制调用方式：

```python
def format_user(
    user_id: int,
    /,
    name: str,
    *,
    active: bool = True,
) -> str:
    return f"{user_id}: {name}, active={active}"


print(format_user(1001, "小林", active=False))
```

运行结果：

```text
1001: 小林, active=False
```

- `/` 前面的 `user_id` 只能按位置传入；
- `/` 与 `*` 之间的 `name` 可按位置或关键字传入；
- `*` 后面的 `active` 只能按关键字传入。

仅限关键字参数可以避免 `format_user(1001, "小林", False)` 这种含义不够直观的调用。仅限位置参数
常见于内置函数和需要保留参数名变更自由的公共接口。

## `*args` 和 `**kwargs`

`*args` 收集多余的位置参数，函数内得到 tuple：

```python
def total(*prices: float) -> float:
    return sum(prices)


print(total(10, 20, 30))
print(total())
```

运行结果：

```text
60
0
```

`**kwargs` 收集多余的关键字参数，函数内得到 dict：

```python
def build_profile(name: str, **details: str) -> dict[str, str]:
    return {"name": name, **details}


profile = build_profile("小林", city="杭州", skill="Python")
print(profile)
```

运行结果：

```text
{'name': '小林', 'city': '杭州', 'skill': 'Python'}
```

已有的序列和字典也可以在调用时解包：

```python
def area(width: int, height: int) -> int:
    return width * height


size = (4, 5)
options = {"width": 6, "height": 3}

print(area(*size))
print(area(**options))
```

运行结果：

```text
20
18
```

`*args` 和 `**kwargs` 适合装饰器、转发调用和参数数量确实可变的接口。参数集合固定时，显式形参更容易
阅读，也更容易获得编辑器和类型检查器的帮助。
