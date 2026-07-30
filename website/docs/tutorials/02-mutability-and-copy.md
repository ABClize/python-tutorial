# Python 可变对象、引用与拷贝

Python 变量保存的是对象的引用。两个变量可以引用同一个对象，所以通过其中一个变量修改对象时，
另一个变量也能看到变化。

复制对象时，还要区分浅拷贝和深拷贝。本章从引用和可变性讲起，再说明函数参数、默认值、哈希和复制方式。

<!-- 对应源码：python/python_interview_practice/03_collections_copy.py -->

## 本章内容

- [引用、可变对象与不可变对象](./02-mutability-and-copy/references-and-mutability)
  学习变量怎样引用对象，以及修改对象与重新赋值的区别。
- [浅拷贝与深拷贝](./02-mutability-and-copy/shallow-and-deep-copy)
  用嵌套列表和引用图查看两种拷贝创建了哪些对象。
- [函数参数与可变默认值](./02-mutability-and-copy/function-arguments-and-defaults)
  解释实参如何绑定到形参，以及为什么列表默认值会在多次函数调用之间被复用。
- [哈希规则与复制策略](./02-mutability-and-copy/hashing-and-copy-strategy)
  学习可哈希对象的规则，并选择直接赋值、浅拷贝、深拷贝或序列化。
