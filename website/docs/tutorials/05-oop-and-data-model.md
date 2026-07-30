# Python 面向对象与数据模型

面向对象把相关数据和操作放在一个对象中。类规定对象有哪些属性和方法，实例是根据类创建的具体对象。
Python 数据模型还规定了对象怎样参与打印、比较、运算和属性访问。

本章先讲类、实例、封装、组合与继承，再讲 `dataclass`、特殊方法、描述符和属性查找顺序。

<p class="source-note">对应源码：<code>python/python_interview_practice/05_oop_magic_methods.py</code>、<code>python/python_interview_practice/10_data_model_descriptors.py</code></p>

## 本章内容

- [类、实例与方法](./05-oop-and-data-model/classes-instances-methods)
  学习创建类和实例，并区分实例属性、类属性和三种常见方法。
- [封装、property 与组合](./05-oop-and-data-model/encapsulation-properties-composition)
  说明怎样保护对象状态、在赋值时校验数据，以及通过持有其他对象复用能力。
- [继承、MRO 与抽象基类](./05-oop-and-data-model/inheritance-mro-abc)
  解释方法重写、多重继承的查找顺序、`super()` 的真实含义和抽象接口。
- [dataclass 与特殊方法](./05-oop-and-data-model/dataclasses-and-special-methods)
  减少数据类样板代码，并让自定义对象接入打印、长度、比较和运算等 Python 语法。
- [描述符、属性查找与 __slots__](./05-oop-and-data-model/descriptors-attribute-lookup-slots)
  学习属性查找顺序、数据描述符、非数据描述符和 `__slots__`。
