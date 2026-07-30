# Python 字典

字典使用 key 保存和查找 value，类型名是 `dict`。它适合保存姓名到分数、配置名到配置值等对应数据。

<!-- 对应源码：python/python_interview_practice/01_basic_types.py -->

## 字典的创建和读取

dict 保存 key 到 value 的映射。下面创建一名学生的数据，再按 key 读取：

```python
student = {
    "name": "小林",
    "score": 82,
    "city": "杭州",
}

print(student["name"])
print(student.get("score"))
```

运行结果：

```text
小林
82
```

两个读取结果分别是“小林”和 `82`。方括号和 `get()` 在 key 不存在时行为不同：

```python
student = {"name": "小林"}

print(student.get("city"))
print(student.get("city", "未知"))
```

运行结果：

```text
None
未知
```

`student["city"]` 会抛出 `KeyError`，适合 key 必须存在的场景。`get()` 返回默认值，适合 key
允许缺失的场景。不要仅为避免异常而把所有读取都改成 `get()`，否则必要字段缺失也可能被掩盖。

## 增加、修改和删除字典元素

增加和修改都使用方括号。下面增加城市、修改分数，再删除城市：

```python
student = {"name": "小林", "score": 82}

student["city"] = "杭州"
student["score"] = 90
removed = student.pop("city")

print(student)
print(removed)
```

运行结果：

```text
{'name': '小林', 'score': 90}
杭州
```

输出中的字典已经没有 `city`，分数改为 `90`。`pop()` 返回被删除的值“杭州”。

`setdefault()` 只在 key 不存在时设置默认值，并返回当前 value：

```python
groups: dict[str, list[str]] = {}

groups.setdefault("Python", []).append("小林")
groups.setdefault("Python", []).append("小周")

print(groups)
```

运行结果：

```text
{'Python': ['小林', '小周']}
```

两个字典可以使用 `|` 合并，右侧同名 key 覆盖左侧。下面用自定义超时时间覆盖默认值：

```python
defaults = {"timeout": 30, "retries": 2}
custom = {"timeout": 10}

print(defaults | custom)
```

运行结果：

```text
{'timeout': 10, 'retries': 2}
```

`update()` 和 `|=` 会原地修改原字典。

## 遍历字典

直接遍历 dict 得到 key。下面依次打印两个学生姓名：

```python
scores = {"小林": 82, "小周": 91}

for name in scores:
    print(name)
```

运行结果：

```text
小林
小周
```

需要 value 或 key-value 对时，分别使用 `values()` 和 `items()`。下面同时读取姓名和分数：

```python
scores = {"小林": 82, "小周": 91}

for name, score in scores.items():
    print(name, score)
```

运行结果：

```text
小林 82
小周 91
```

dict 自 Python 3.7 起语言层面保证保持插入顺序。修改已有 key 不会改变它的位置；删除后重新插入会把
它放到末尾。

遍历字典时不要直接改变字典大小。需要删除多个元素时，可以先复制 key。下面删除不及格的学生：

```python
scores = {"小林": 82, "小周": 40, "小陈": 91}

for name in list(scores):
    if scores[name] < 60:
        del scores[name]

print(scores)
```

运行结果：

```text
{'小林': 82, '小陈': 91}
```

## 字典的 key 必须可哈希

dict 的 key 需要具有稳定的哈希值。常见可哈希对象有 str、int、bytes、frozenset，以及全部元素都
可哈希的 tuple。下面使用经纬度元组作为 key：

```python
locations = {
    (120.1, 30.2): "杭州",
    (121.5, 31.2): "上海",
}

print(locations[(120.1, 30.2)])
```

运行结果：

```text
杭州
```

list、dict、set 可变，不能作为 dict key。对象能否作为 key 不只取决于“语法上看起来不可变”，还要
保证 `__eq__()` 与 `__hash__()` 的契约一致。
