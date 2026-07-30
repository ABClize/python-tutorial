# Python 函数、作用域与生成器

函数是一段有名字、可以重复调用的代码。函数可以接收参数、返回结果，并拥有自己的局部变量。
在 Python 中，函数本身也是对象，可以赋值、传参或作为返回值。

本章先讲普通函数和作用域，再讲闭包、装饰器、递归、迭代器与生成器。

<!-- 对应源码：python/python_interview_practice/02_functions_scope.py、python/python_interview_practice/04_iterators_generators.py -->

## 本章内容

- [函数定义、调用与参数](./03-functions-and-generators/function-basics)
  学习返回值、位置参数、关键字参数、默认参数和星号参数。
- [作用域与函数对象](./03-functions-and-generators/scope-and-function-objects)
  说明局部名字、外层名字和全局名字怎样查找，以及函数为什么可以作为普通对象传递。
- [闭包、装饰器与递归](./03-functions-and-generators/closures-decorators-recursion)
  学习保存外层变量、包装函数调用以及函数调用自身的写法。
- [可迭代对象与迭代器](./03-functions-and-generators/iterables-and-iterators)
  学习 `for` 循环使用的迭代协议，并区分可迭代对象和迭代器。
- [生成器与 itertools](./03-functions-and-generators/generators-and-itertools)
  观察 `yield` 暂停和恢复函数的过程，并使用惰性工具处理可能很长的数据序列。
