# Python 列表、元组、字典、集合与排序

容器用来保存多个值。列表和元组按位置保存值，字典按键查找值，集合只保留不重复的元素。
不同容器支持的操作和查找速度不同。

本章先讲四种基础容器，再讲推导式、排序、保序去重以及 `collections` 中的常用工具。

<!-- 对应源码：python/python_interview_practice/01_basic_types.py、python/python_interview_practice/03_collections_copy.py、python/interview_exercises/collections.py -->

## 本章内容

- [列表、元组与序列解包](./04-containers-and-sorting/lists-tuples-unpacking)
  学习有序数据的读取、修改和解包。
- [字典](./04-containers-and-sorting/dictionaries)
  从创建、读取、更新和遍历入手，解释键的哈希要求以及缺失键的处理方式。
- [集合、并集交集与推导式](./04-containers-and-sorting/sets-and-comprehensions)
  处理成员判断、去重和集合运算，并用推导式从已有数据构造新容器。
- [排序与保序去重](./04-containers-and-sorting/sorting-and-deduplication)
  区分原地排序与新列表排序，并学习稳定排序和保序去重。
- [collections 工具与容器复杂度](./04-containers-and-sorting/collections-and-complexity)
  使用 `Counter`、`defaultdict` 和 `deque`，并根据常见操作的时间成本选择容器。
