# Python 变量、基本类型与控制语句

Python 程序要保存数据，也要根据数据执行操作。变量用来给数据命名，类型决定数据可以参加哪些操作，
条件和循环则控制代码的执行顺序。

本章先讲变量和常用类型，再讲数值、字符串、条件与循环。示例都可以直接运行。学习时可以先猜输出，
再用 Python 验证。

<!-- 对应源码：python/python_interview_practice/01_basic_types.py -->

## 本章内容

- [变量、基本类型与类型转换](./01-basic-types-and-truthiness/variables-and-types)
  学习变量赋值、常见内置类型、类型转换，以及 `len()`、`sum()`、`map()` 等内置函数。
- [数值与运算符](./01-basic-types-and-truthiness/numbers-and-operators)
  学习算术、比较和逻辑运算，并认识浮点数误差以及 `bool` 与 `int` 的关系。
- [条件语句与循环](./01-basic-types-and-truthiness/conditions-and-loops)
  学习 `if`、`for`、`while`、循环 `else` 和 `match`，并使用 `pass`、`break`、`continue`
  控制执行过程。
- [字符串](./01-basic-types-and-truthiness/strings)
  学习索引、切片、f-string、文本编码、字节和正则表达式。
- [真值、相等与对象身份](./01-basic-types-and-truthiness/truthiness-and-identity)
  区分真值判断、值相等和“是否为同一个对象”，并通过可视化观察不同值的判断结果。
