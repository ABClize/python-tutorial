# 容器、推导式与排序

选择容器不是语法偏好，而是在表达数据的约束：是否有顺序、是否允许重复、怎样查找、是否需要
可变。先说清这些约束，再选择 list、tuple、dict 或 set。

<p class="source-note">对应源码：<code>python/python_interview_practice/03_collections_copy.py</code>、<code>python/interview_exercises/collections.py</code></p>

## 先会创建、读取和修改

四种容器都能一次保存多个值，但访问方式不同：序列按位置访问，映射按 key 访问，集合主要判断
成员是否存在。

```python
names = ["Alice", "Bob"]
point = (10, 20)
scores = {"Alice": 90, "Bob": 82}
skills = {"python", "sql"}

names.append("Carol")
scores["Carol"] = 88
skills.add("git")

print(names[0])              # Alice
print(point[1])              # 20
print(scores.get("David"))   # None
print("python" in skills)    # True
```

读取 dict 时，`scores["David"]` 会抛出 `KeyError`，`scores.get("David")` 则返回 `None`。
如果 `None` 本身也是合法值，可传入哨兵对象，避免把“key 不存在”和“值就是 None”混在一起。

常用删除操作也有不同语义：

| 操作 | 行为 |
| --- | --- |
| `items.pop()` | 删除并返回最后一个 list 元素 |
| `items.pop(index)` | 删除并返回指定位置元素 |
| `mapping.pop(key)` | 删除并返回指定 key 的值 |
| `discard(value)` | 从 set 删除，元素不存在也不报错 |
| `remove(value)` | 删除指定值，不存在时抛异常 |

## 遍历时同时拿到位置和多个序列

不要为了得到下标手写 `range(len(items))`。`enumerate()` 同时提供位置和值，`zip()` 把多个序列按
位置配对，dict 则通过 `items()` 同时得到 key 和 value：

```python
names = ["Alice", "Bob"]
scores = [90, 82]

for rank, (name, score) in enumerate(zip(names, scores), start=1):
    print(rank, name, score)

for name, score in {"Alice": 90, "Bob": 82}.items():
    print(f"{name}: {score}")
```

`zip()` 默认在最短输入耗尽时停止。若长度不一致就属于数据错误，可以在 Python 3.10+ 使用
`zip(left, right, strict=True)`，让它立即抛出 `ValueError`。

## 四种核心容器

| 容器 | 顺序 | 重复 | 典型查找 | 适合表达 |
| --- | --- | --- | --- | --- |
| `list` | 有 | 允许 | 按下标 O(1)，按值 O(n) | 可变序列 |
| `tuple` | 有 | 允许 | 与 list 类似 | 固定结构或不可变序列 |
| `dict` | 保持插入顺序 | key 唯一 | key 平均 O(1) | 映射关系 |
| `set` | 不承诺业务顺序 | 不允许 | 元素平均 O(1) | 去重与集合运算 |

所谓 O(1) 是平均复杂度，不是任何情况下的绝对承诺。哈希容器还要求 key 或元素可哈希，通常意味
着其哈希值在存活期间不能改变。

### dict 的视图是动态的

`mapping.keys()`、`values()` 和 `items()` 返回视图，不是立即复制的 list。字典变化后，视图会
反映新状态；迭代期间修改字典大小通常会抛出 `RuntimeError`。

```python
scores = {"alice": 90}
names = scores.keys()
scores["bob"] = 82

list(names)  # ["alice", "bob"]
```

需要稳定快照时显式 `list(mapping.items())` 或复制 dict。只改已有 key 对应的 value 与增删 key
的迭代风险也不同，但在并发或复杂逻辑中仍应避免边迭代边修改。

## 修改与创建新容器

```python
numbers = [3, 1, 4]

numbers.append(1)        # 原地修改，返回 None
ordered = sorted(numbers)  # 创建新列表
numbers.sort()           # 原地排序，返回 None
```

很多 bug 来自没有分清“原地修改”与“返回新值”。可变容器的方法如 `append()`、`extend()`、
`sort()` 通常返回 `None`，避免误以为它们产生独立结果。

## dict 合并与集合代数

Python 3.9+ 可以用 `left | right` 创建合并后的 dict，右侧同名 key 覆盖左侧；`left |= right`
原地更新。它是浅合并，不会递归合并嵌套配置。

集合运算直接表达关系：

```python
required = {"python", "sql"}
candidate = {"python", "git", "sql"}

required <= candidate      # 是否包含全部必需技能
required & candidate       # 交集
candidate - required       # 候选人的额外技能
required ^ candidate       # 只出现在一边的元素
```

用集合表达成员关系通常比多层循环更清晰，但集合会去重，不能用于需要保留频次的场景。

## 推导式是一种变换

推导式最适合表达“遍历 → 可选过滤 → 映射”：

```python
squares = [number * number for number in range(10) if number % 2 == 0]
score_by_name = {name: score + 5 for name, score in scores.items()}
unique_lengths = {len(word) for word in words}
```

如果推导式包含多个复杂条件、副作用或超过两层循环，普通 `for` 往往更容易调试。生成器表达式
`(expression for item in source)` 则用于惰性消费。

推导式有自己的局部作用域，循环变量不会泄漏到外部。闭包在推导式或循环中捕获变量时仍采用晚绑定：
函数调用时读取当前 cell，而不是创建函数时自动冻结当轮值；需要冻结时可用默认参数或工厂函数。

## 排序的核心是 key

Python 排序稳定：key 相同时保留原相对顺序。复杂记录通常用 `key` 描述排序依据，而不是修改对象
的比较协议。

```python
students = [
    {"name": "Alice", "score": 88},
    {"name": "Bob", "score": 95},
    {"name": "Carol", "score": 88},
]

ordered = sorted(students, key=lambda item: (-item["score"], item["name"]))
```

key 函数对每个元素计算一次，再比较 key。多字段排序可以返回 tuple；降序数字常取负数，或分多次
利用稳定排序完成。

排序要求不同 key 之间可比较。混合 `None`、数字和字符串时，应先把缺失值映射为明确的排序 key，
不要依赖 Python 2 时代的跨类型比较。若只要最小值、最大值或少量 Top-K，`min()`、`max()` 和
`heapq.nsmallest()` 往往不需要完整排序。

## 去重时先确认是否保序

只需要集合语义时使用 `set(items)`。需要保留首次出现顺序，可以借助 dict 保持插入顺序：

```python
def unique_in_order(items):
    return list(dict.fromkeys(items))
```

该写法要求元素可哈希。不可哈希对象或需要自定义等价规则时，应显式维护“已见 key”集合。

## 选择容器的思考顺序

<div class="concept-map">
  <div class="concept-step"><small>需要按 key 查找？</small><strong>dict</strong></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>只关心成员与去重？</small><strong>set</strong></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>固定结构、不修改？</small><strong>tuple</strong></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>其余有序序列</small><strong>list</strong></div>
</div>

这不是机械决策树。例如有序映射仍是 dict，队列可能更适合 `collections.deque`。关键是先描述
访问模式，再选实现。

## 常见误区

### set 可以稳定保持输入顺序

不要把某次运行观察到的顺序当成接口契约。需要保序去重时显式使用对应算法。

### `list.remove()` 按下标删除

`remove(value)` 删除第一个相等值；`pop(index)` 按下标删除并返回；`del items[index]` 只删除。

### dict 查找永远比 list 快

大数据下哈希查询增长率更好，但 dict 有哈希和内存成本。小规模、顺序扫描或需要重复值时，
list 可能更合适。

## 面试时怎么表述

> 我会根据数据约束选择容器：list 表达有序可变序列，tuple 表达固定结构，dict 表达 key 到 value
> 的映射，set 表达唯一成员集合。哈希容器查询平均 O(1)，但要求 key 可哈希；排序是 O(n log n)，
> 应优先用稳定排序和 key 函数描述规则。
