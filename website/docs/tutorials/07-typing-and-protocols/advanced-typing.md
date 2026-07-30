# Python 重载、型变与运行时标注

基础类型标注能够覆盖大多数业务代码。函数的返回类型确实由输入类型决定，或者设计泛型生产者和消费者
时，才需要 overload 和型变等工具。

<p class="source-note">对应源码：<code>python/python_interview_practice/11_typing_protocols.py</code></p>

## overload 描述输入与返回关系

下面的 `strip_value()` 保留输入的 str 或 bytes 类型：

```python
from typing import overload


@overload
def strip_value(value: str) -> str: ...


@overload
def strip_value(value: bytes) -> bytes: ...


def strip_value(value: str | bytes) -> str | bytes:
    return value.strip()


text_result = strip_value("  Python  ")
bytes_result = strip_value(b"  Python  ")

print(text_result)
print(bytes_result)
```

运行结果：

```text
Python
b'Python'
```

检查器知道 `text_result` 是 str，`bytes_result` 是 bytes。`@overload` 声明只供静态检查器读取，
最后必须提供一个实际运行的实现。

如果不同输入最终都返回同一类型，通常直接使用联合参数：

```python
def parse_integer(value: str | bytes) -> int:
    return int(value)
```

overload 不会创建多个运行时函数，也不适合隐藏职责完全不同的业务分支。

## 协变、逆变与不变

泛型类型参数的变化规则取决于接口如何使用值：

- 只产生值的只读接口通常可以协变；
- 只接收值的消费者接口通常可以逆变；
- 同时读取和写入的可变容器通常不变。

`list[Dog]` 不能当作 `list[Animal]`：

```python
class Animal:
    pass


class Dog(Animal):
    pass


class Cat(Animal):
    pass
```

如果允许把 `list[Dog]` 传给接收 `list[Animal]` 的函数，该函数就可能追加 Cat，破坏原列表只包含
Dog 的约定。

只读取时可以把参数标注为 `Sequence[Animal]`。设计自定义生产者和消费者 Protocol 时，再考虑
`covariant=True` 或 `contravariant=True`。

## 逆变消费者示例

```python
from typing import Protocol, TypeVar

T_contra = TypeVar("T_contra", contravariant=True)


class Serializer(Protocol[T_contra]):
    def serialize(self, value: T_contra) -> str: ...


class ObjectSerializer:
    def serialize(self, value: object) -> str:
        return str(value)


def dump_integer(
    value: int,
    serializer: Serializer[int],
) -> str:
    return serializer.serialize(value)


print(dump_integer(42, ObjectSerializer()))
```

运行结果：

```text
42
```

能够序列化任意 object 的消费者，也能用于只要求序列化 int 的位置。型变规则通常由库和接口作者处理，
普通调用代码不需要频繁声明。

## 运行时读取类型标注

函数和类的标注通常保存在 `__annotations__` 中。需要解析延迟标注和前向引用时，应使用
`typing.get_type_hints()`：

```python
from typing import get_type_hints


def greet(name: str) -> str:
    return f"你好，{name}"


print(get_type_hints(greet))
```

运行结果：

```text
{'name': <class 'str'>, 'return': <class 'str'>}
```

框架会读取类型提示生成文档、注入依赖或执行验证。解析类型提示可能需要导入模块和求值名称，不应把它
当作高频业务循环中的零成本操作。

## cast 只影响静态检查

`typing.cast()` 不会转换运行时对象：

```python
from typing import cast

value: object = "Python"
text = cast(str, value)

print(text)
print(text is value)
```

运行结果：

```text
Python
True
```

cast 表示“开发者确认这里是指定类型”。它不会检查判断是否正确，滥用会把真实不确定性隐藏起来。能够
使用 `isinstance()`、Protocol 或更准确的数据模型表达时，应优先使用这些方式。

## 高级标注注意事项

- overload 用于真实的调用签名关系，不用于给同一返回类型增加形式。
- 可变容器通常不变，避免通过型变破坏元素约束。
- `@runtime_checkable` 只做有限成员检查。
- `get_type_hints()` 解析标注，不能代替外部数据校验。
- cast 不进行运行时转换或检查。
- 标注比实现更难理解时，应先检查公共接口是否过于复杂。
