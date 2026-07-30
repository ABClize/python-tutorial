# Python 可变对象、引用与拷贝

把一个列表赋给另一个变量后，修改其中一边，另一边为什么也变了？调用 `copy()` 后，外层列表明明已经
不同，内层列表为什么仍会一起变化？这些现象不是 Python 随机做出的选择，而是由对象、引用和可变性共同
决定的。

这一章先画清变量与对象的关系，再比较赋值、浅拷贝和深拷贝。理解这些规则后，函数参数、默认值、字典键
和自定义复制行为都会变得容易解释。

<p class="source-note">对应源码：<code>python/python_interview_practice/03_collections_copy.py</code></p>

## 本章内容

- [引用、可变对象与不可变对象](./02-mutability-and-copy/references-and-mutability)
  解决“变量与对象是什么关系、修改对象和重新赋值有什么不同”这两个基础问题。
- [浅拷贝与深拷贝](./02-mutability-and-copy/shallow-and-deep-copy)
  用嵌套列表和引用图说明两种拷贝分别创建了哪些新对象，修改会传播到哪里。
- [函数参数与可变默认值](./02-mutability-and-copy/function-arguments-and-defaults)
  解释实参如何绑定到形参，以及为什么列表默认值会在多次函数调用之间被复用。
- [哈希规则与复制策略](./02-mutability-and-copy/hashing-and-copy-strategy)
  说明哪些对象能作为字典键，并给出赋值、浅拷贝、深拷贝和序列化之间的选择方法。
