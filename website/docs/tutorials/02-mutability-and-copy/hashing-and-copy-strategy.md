# Python 哈希规则与复制策略

哈希值是 Python 为对象计算的整数，用于快速查找字典键和集合元素。字典键和集合元素必须可哈希。
复制对象时，则要根据数据是否需要独立来选择复制方式。

<p class="source-note">对应源码：<code>python/python_interview_practice/03_collections_copy.py</code></p>

## 可变对象与哈希

字典的 key 和集合的元素必须可哈希。哈希值用于快速定位对象，并且在对象作为 key 或集合成员期间必须
保持稳定。

内置可变容器通常不可哈希。下面尝试把列表作为字典键：

```python
skills = ["Python", "SQL"]
mapping = {skills: "小林"}
```

运行结果：

```text
TypeError: unhashable type: 'list'
```

程序抛出 `TypeError`。列表内容可以修改，哈希值无法保持稳定，所以不能直接作为字典 key。
内容固定且所有元素都可哈希时，可以使用元组：

```python
skills = ("Python", "SQL")
mapping = {skills: "小林"}

print(mapping[("Python", "SQL")])
```

运行结果：

```text
小林
```

上面的元组可以作为键，并能用内容相同的元组查到“小林”。

元组本身不可变，但只有所有元素都可哈希时，整个元组才可哈希：

```python
value = ([1, 2],)
hash(value)
```

```text
TypeError: unhashable type: 'list'
```

元组中包含列表，因此整个元组仍然不可哈希。

## 选择复制方式

| 需要的结果 | 做法 |
| --- | --- |
| 多个变量操作同一个对象 | 直接赋值 |
| 只让外层容器独立 | 浅拷贝 |
| 嵌套的普通数据也需要独立 | 深拷贝 |
| 只修改少数字段 | 显式构造新对象 |
| 对象包含文件、连接或锁 | 重新建立资源，不直接深拷贝 |

深拷贝会遍历对象及其子对象。数据越复杂，时间和内存成本越高。复制前先确定哪些部分必须独立，
不要默认对所有数据做深拷贝。

## 复制协议

`copy.copy()` 和 `copy.deepcopy()` 会使用对象支持的复制协议：

- `copy.copy(obj)` 可以调用 `obj.__copy__()`；
- `copy.deepcopy(obj)` 可以调用 `obj.__deepcopy__(memo)`。

自定义对象持有数据库连接、文件句柄、线程锁等外部资源时，通常没有合理的通用复制方式。此类对象可以
禁止复制，或者只提供“导出普通数据”和“根据数据重新创建”的接口。

## 复制与序列化

复制在当前 Python 进程中构造对象或对象图。序列化把有限类型转换为可以存储或传输的数据格式。

下面的代码把对象转成 JSON，再读回来。它不能作为通用深拷贝：

```python
import json

copied = json.loads(json.dumps(original))
```

JSON 往返会丢失：

- Python 自定义类型；
- 对象方法；
- tuple、set 等非 JSON 原生类型的原始语义；
- 对象之间的共享引用和循环引用；
- 部分数值和日期类型。

需要复制 Python 对象时使用明确的复制方式；需要跨系统传输数据时使用序列化，并为数据格式定义契约。

## 注意事项

- `items[:]`、`list(items)` 和 `items.copy()` 都是列表浅拷贝；
- `dict.copy()` 只复制最外层字典；
- `copy.deepcopy()` 不保证外部资源能够被合理复制；
- 判断修改是否传播时，应检查真正被修改的对象是否仍然共享；
- 不要为了避免思考对象所有权而对所有参数执行深拷贝。
