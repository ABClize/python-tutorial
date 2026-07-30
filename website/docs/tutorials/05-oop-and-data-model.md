# Python 面向对象与数据模型

面向对象把相关的数据和操作放进同一个对象。类负责描述对象怎样创建、保存哪些状态、提供哪些行为；Python
数据模型又规定了自定义对象怎样参与打印、比较、运算、属性访问等语言行为。

这一章先从类和实例的基本关系开始，再学习封装、组合与继承。后半部分进入 `dataclass`、特殊方法、
描述符和属性查找顺序，帮助你理解常见语法背后的调用过程。

<p class="source-note">对应源码：<code>python/python_interview_practice/05_oop_magic_methods.py</code>、<code>python/python_interview_practice/10_data_model_descriptors.py</code></p>

## 本章内容

- [类、实例与方法](./05-oop-and-data-model/classes-instances-methods)
  建立类与实例的基本认识，区分实例属性、类属性和三种常见方法。
- [封装、property 与组合](./05-oop-and-data-model/encapsulation-properties-composition)
  说明怎样保护对象状态、在赋值时校验数据，以及通过持有其他对象复用能力。
- [继承、MRO 与抽象基类](./05-oop-and-data-model/inheritance-mro-abc)
  解释方法重写、多重继承的查找顺序、`super()` 的真实含义和抽象接口。
- [dataclass 与特殊方法](./05-oop-and-data-model/dataclasses-and-special-methods)
  减少数据类样板代码，并让自定义对象接入打印、长度、比较和运算等 Python 语法。
- [描述符、属性查找与 __slots__](./05-oop-and-data-model/descriptors-attribute-lookup-slots)
  按顺序拆解属性访问，区分数据描述符与非数据描述符，并说明 `__slots__` 的作用和限制。
