# Python 变量、基本类型与控制语句

Python 程序由数据和操作数据的语句组成。刚开始学习时，最容易混在一起的是几个看似简单的问题：
变量到底保存了什么，整数和字符串为什么不能随意混用，条件为什么有时不写 `True` 也能成立，以及循环
在什么情况下会结束。

这一章从能直接运行的小例子开始，先建立变量、对象和类型的基本认识，再学习数值、字符串、条件与循环。
阅读时可以把示例复制到 Python 解释器中，先猜输出，再实际运行。

<p class="source-note">对应源码：<code>python/python_interview_practice/01_basic_types.py</code></p>

## 本章内容

- [变量、基本类型与类型转换](./01-basic-types-and-truthiness/variables-and-types)
  解决“变量是什么、常见值有哪些类型、`input()` 得到的数据为什么不能直接参与数值运算”等问题。
- [数值与运算符](./01-basic-types-and-truthiness/numbers-and-operators)
  讲清算术、比较、逻辑运算的结果，以及浮点数误差、布尔值和整数之间容易忽略的关系。
- [条件语句与循环](./01-basic-types-and-truthiness/conditions-and-loops)
  说明程序怎样选择分支、重复执行，并在合适的时机跳过本轮或提前结束循环。
- [字符串](./01-basic-types-and-truthiness/strings)
  从索引和切片讲到查找、替换、拆分与 f-string，建立处理文本所需的基础。
- [真值、相等与对象身份](./01-basic-types-and-truthiness/truthiness-and-identity)
  区分真值判断、值相等和“是否为同一个对象”，并通过可视化观察不同值的判断结果。
