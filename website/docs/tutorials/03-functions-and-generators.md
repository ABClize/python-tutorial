# Python 函数、作用域与生成器

函数不只是“把几行代码包起来”。它有自己的参数和局部作用域，也可以像其他对象一样被赋值、传入另一个
函数或作为结果返回。在这个基础上，才会自然出现闭包、装饰器、迭代器和生成器。

这一章按照调用过程逐层展开：先学会定义和调用普通函数，再理解名字的查找范围，随后进入高阶函数与递归，
最后学习 Python 的迭代协议和按需产生数据的生成器。

<p class="source-note">对应源码：<code>python/python_interview_practice/02_functions_scope.py</code>、<code>python/python_interview_practice/04_iterators_generators.py</code></p>

## 本章内容

- [函数定义、调用与参数](./03-functions-and-generators/function-basics)
  讲清返回值、位置参数、关键字参数、默认参数和星号参数，帮助你读懂常见函数签名。
- [作用域与函数对象](./03-functions-and-generators/scope-and-function-objects)
  说明局部名字、外层名字和全局名字怎样查找，以及函数为什么可以作为普通对象传递。
- [闭包、装饰器与递归](./03-functions-and-generators/closures-decorators-recursion)
  从函数对象继续推导三种常见写法，解释它们保存状态、包装调用或重复调用自身的方式。
- [可迭代对象与迭代器](./03-functions-and-generators/iterables-and-iterators)
  拆开 `for` 循环背后的协议，区分“能被遍历”和“记录当前遍历位置”。
- [生成器与 itertools](./03-functions-and-generators/generators-and-itertools)
  观察 `yield` 暂停和恢复函数的过程，并使用惰性工具处理可能很长的数据序列。
