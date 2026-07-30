# Python 类型标注、泛型与 Protocol

Python 的类型标注把函数参数、返回值和容器元素的预期类型写进代码，供编辑器、静态检查器和代码读者
使用。类型标注不会改变 Python 的动态运行方式，也不能代替外部数据校验。

这一章从常用标注开始，再介绍 TypedDict、泛型、Protocol、Callable 和需要明确类型关系时才会用到的
高级工具。

<p class="source-note">对应源码：<code>python/python_interview_practice/11_typing_protocols.py</code></p>

## 本章内容

- [类型标注基础](./07-typing-and-protocols/typing-basics)：
  标注函数、容器、联合类型和抽象接口，并理解 `Any` 与 `object` 的区别。
- [Literal、类型别名与 TypedDict](./07-typing-and-protocols/literal-and-typeddict)：
  描述有限选项、业务标识和具有固定 key 的字典结构。
- [TypeVar、Generic 与 Self](./07-typing-and-protocols/generics)：
  表达输入输出之间的类型关系，并让自定义容器保留元素类型。
- [Protocol、Callable 与 ParamSpec](./07-typing-and-protocols/protocols-and-callables)：
  按对象能力定义接口，为依赖注入、高阶函数和装饰器保留类型信息。
- [重载、型变与运行时标注](./07-typing-and-protocols/advanced-typing)：
  在确有需要时使用 overload 和型变，并安全读取运行时类型提示。
