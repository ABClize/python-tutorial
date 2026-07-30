# Python 集合、并集交集与推导式

集合只保留不重复的元素，特别适合成员判断、去重和集合运算。推导式则提供了一种从已有可迭代对象构造新容器的紧凑写法。本页还会用 enumerate() 和 zip() 处理索引与并行数据。

<p class="source-note">对应源码：<code>python/python_interview_practice/01_basic_types.py</code></p>

## 集合的创建和成员判断

set 保存不重复的可哈希元素：

```python
skills = {"Python", "SQL", "Python"}

print(sorted(skills))
print("Python" in skills)
```

运行结果：

```text
['Python', 'SQL']
True
```

集合的显示和遍历顺序不应作为业务规则。示例用 `sorted()` 只是为了得到稳定输出。

空集合必须写成 `set()`，因为 `{}` 表示空 dict：

```python
print(type(set()))
print(type({}))
```

运行结果：

```text
<class 'set'>
<class 'dict'>
```

常用修改方法：

```python
skills = {"Python"}

skills.add("SQL")
skills.update(["Git", "Linux"])
skills.discard("Java")

print(sorted(skills))
```

运行结果：

```text
['Git', 'Linux', 'Python', 'SQL']
```

`remove(value)` 在元素不存在时抛出 `KeyError`，`discard(value)` 则不报错。

## 集合运算

集合可以直接表示并集、交集、差集和包含关系：

```python
required = {"Python", "SQL"}
candidate = {"Python", "SQL", "Git"}

print(sorted(required | candidate))
print(sorted(required & candidate))
print(sorted(candidate - required))
print(required <= candidate)
```

运行结果：

```text
['Git', 'Python', 'SQL']
['Python', 'SQL']
['Git']
True
```

| 运算 | 写法 | 含义 |
| --- | --- | --- |
| 并集 | `left \| right` | 出现在任一集合 |
| 交集 | `left & right` | 同时出现在两个集合 |
| 差集 | `left - right` | 只出现在左集合 |
| 对称差集 | `left ^ right` | 只出现在其中一个集合 |
| 子集 | `left <= right` | 左侧是否全部包含在右侧 |
| 真子集 | `left < right` | 是子集且不相等 |

不可变集合 `frozenset` 可以作为 dict key 或另一个 set 的元素。

## `enumerate()` 和 `zip()`

遍历时同时需要位置和值，使用 `enumerate()`：

```python
names = ["小林", "小周"]

for position, name in enumerate(names, start=1):
    print(position, name)
```

运行结果：

```text
1 小林
2 小周
```

并行遍历多个可迭代对象，使用 `zip()`：

```python
names = ["小林", "小周"]
scores = [82, 91]

for name, score in zip(names, scores, strict=True):
    print(name, score)
```

运行结果：

```text
小林 82
小周 91
```

普通 `zip()` 在最短输入耗尽时结束。Python 3.10+ 的 `strict=True` 会在输入长度不一致时抛出
`ValueError`，适合本应一一对应的数据。

## 列表、字典和集合推导式

列表推导式把简单的遍历、过滤和变换写在一个表达式中：

```python
scores = [55, 82, 91]

passed = [score for score in scores if score >= 60]
bonus_scores = [min(score + 5, 100) for score in scores]

print(passed)
print(bonus_scores)
```

运行结果：

```text
[82, 91]
[60, 87, 96]
```

dict 和 set 也支持推导式：

```python
names = ["小林", "小周"]
scores = [82, 91]

score_by_name = {
    name: score
    for name, score in zip(names, scores, strict=True)
}
levels = {"通过" if score >= 60 else "未通过" for score in scores}

print(score_by_name)
print(levels)
```

运行结果：

```text
{'小林': 82, '小周': 91}
{'通过'}
```

推导式适合一眼可读的变换。多层循环、复杂分支、异常处理或副作用应使用普通 `for`。
