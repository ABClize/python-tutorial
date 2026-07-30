# Python 函数参数与可变默认值

调用函数时，传入的对象会交给形参名使用。Python 不会自动复制这个对象。因此，函数可以修改传入的
列表，可变默认参数也可能在多次调用之间保留内容。

<!-- 对应源码：python/python_interview_practice/03_collections_copy.py -->

## 函数参数与对象引用

函数调用时，实参所指向的对象会绑定给形参。形参和实参可以指向同一个对象。

### 修改形参所指向的对象

下面把列表传给函数。函数使用 `append()` 修改这个列表：

```python
def add_skill(skills: list[str]) -> None:
    skills.append("Git")


my_skills = ["Python", "SQL"]
add_skill(my_skills)

print(my_skills)
```

运行结果：

```text
['Python', 'SQL', 'Git']
```

输出中的列表多了 `"Git"`。调用过程如下：

1. 形参 `skills` 指向 `my_skills` 所指向的列表；
2. `skills.append("Git")` 修改这个共享列表；
3. 函数返回后，通过 `my_skills` 可以看到修改结果。

### 重新给形参赋值

下面的函数没有修改列表，而是让局部变量 `skills` 指向一个新列表：

```python
def replace_skills(skills: list[str]) -> None:
    skills = ["Java"]
    print("函数内：", skills)


my_skills = ["Python"]
replace_skills(my_skills)

print("函数外：", my_skills)
```

运行结果：

```text
函数内： ['Java']
函数外： ['Python']
```

函数内打印新列表 `["Java"]`，函数外仍打印原列表 `["Python"]`。`skills = ["Java"]`
只改变局部变量 `skills` 的指向，不会改变调用方变量 `my_skills`。

这种参数传递方式常称为“对象引用按值传递”或“共享传参”：

- 函数能够修改形参所指向的可变对象；
- 函数不能通过重新绑定形参来改变调用方变量的指向。

## 可变默认参数

函数默认参数在执行 `def` 语句时计算一次，不是在每次调用时重新计算。下面把空列表直接写成默认值：

```python
def collect(value: int, bucket: list[int] = []) -> list[int]:
    bucket.append(value)
    return bucket


print(collect(1))
print(collect(2))
print(collect(3))
```

运行结果：

```text
[1]
[1, 2]
[1, 2, 3]
```

三个调用使用同一个默认列表。第一次加入 `1`，第二次继续加入 `2`，第三次再加入 `3`，所以列表不断
变长。这通常不是调用者想要的结果。

### 使用 `None` 创建新列表

常用写法是把默认值设为 `None`，再在函数体内创建列表：

```python
def collect(
    value: int,
    bucket: list[int] | None = None,
) -> list[int]:
    if bucket is None:
        bucket = []
    bucket.append(value)
    return bucket


print(collect(1))
print(collect(2))
```

运行结果：

```text
[1]
[2]
```

两个调用分别得到 `[1]` 和 `[2]`。每次没有传入 `bucket` 时，函数体都会创建一个新列表。

### dataclass 的可变默认值

`dataclass` 的列表字段也不能直接使用一个共享空列表，应使用 `default_factory`：

```python
from dataclasses import dataclass, field


@dataclass
class Student:
    name: str
    skills: list[str] = field(default_factory=list)
```

`default_factory=list` 会在每次创建 `Student` 实例时调用 `list()`，不同实例不会共享默认列表。
