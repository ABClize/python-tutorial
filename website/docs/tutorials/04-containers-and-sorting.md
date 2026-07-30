# Python 列表、元组、字典、集合与排序

一个程序通常要同时处理很多数据。列表和元组按位置保存值，字典按 key 查找值，集合强调成员是否存在且
不重复。它们看起来都能“装数据”，但适合解决的问题、修改方式和查找成本并不相同。

这一章先掌握四种基础容器，再学习推导式、排序、保序去重和 `collections` 标准库工具。重点不是记住
所有方法，而是根据数据关系选择合适的结构。

<p class="source-note">对应源码：<code>python/python_interview_practice/01_basic_types.py</code>、<code>python/python_interview_practice/03_collections_copy.py</code>、<code>python/interview_exercises/collections.py</code></p>

## 本章内容

- [列表、元组与序列解包](./04-containers-and-sorting/lists-tuples-unpacking)
  说明有序数据怎样读取和修改，以及如何一次把序列中的多个值绑定到变量。
- [字典](./04-containers-and-sorting/dictionaries)
  从创建、读取、更新和遍历入手，解释 key 的哈希要求以及缺失 key 的处理方式。
- [集合、并集交集与推导式](./04-containers-and-sorting/sets-and-comprehensions)
  处理成员判断、去重和集合运算，并用推导式从已有数据构造新容器。
- [排序与保序去重](./04-containers-and-sorting/sorting-and-deduplication)
  区分原地排序与返回新列表，学习复杂排序依据、稳定排序和保留首次出现顺序的去重方法。
- [collections 工具与容器复杂度](./04-containers-and-sorting/collections-and-complexity)
  使用 `Counter`、`defaultdict` 和 `deque`，并根据常见操作的时间成本选择容器。
