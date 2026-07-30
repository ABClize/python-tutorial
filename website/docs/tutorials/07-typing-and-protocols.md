# Python 类型标注、泛型与 Protocol

类型标注用于说明函数参数、返回值和容器元素应该是什么类型。编辑器和静态检查器可以根据这些标注提前
发现一部分错误。类型标注不会改变 Python 的运行方式，也不会自动检查接口或配置文件中的外部数据。

本章先讲函数、容器和联合类型的常用写法，再讲 `Enum`、`TypedDict`、泛型、`Protocol`、
`Callable`、重载和型变。

<!-- 对应源码：python/python_interview_practice/11_typing_protocols.py -->

## 本章内容

- [类型标注基础](./07-typing-and-protocols/typing-basics)：
  标注函数、容器和联合类型，并比较 `Any` 与 `object`。
- [Enum、Literal、类型别名与 TypedDict](./07-typing-and-protocols/literal-and-typeddict)：
  区分静态有限值与运行时枚举，并描述业务标识和具有固定 key 的字典结构。
- [TypeVar、Generic 与 Self](./07-typing-and-protocols/generics)：
  让输入和输出保持同一种类型，并给自定义容器标注元素类型。
- [Protocol、Callable 与 ParamSpec](./07-typing-and-protocols/protocols-and-callables)：
  按对象拥有的方法定义接口，并为函数参数和装饰器保留类型信息。
- [重载、型变与运行时标注](./07-typing-and-protocols/advanced-typing)：
  在确有需要时使用 overload 和型变，并安全读取运行时类型提示。
