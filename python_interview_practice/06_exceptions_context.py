"""异常处理、自定义异常和上下文管理器。"""

from contextlib import contextmanager
from io import StringIO


class InvalidAgeError(ValueError):
    """业务含义更明确的自定义异常。"""


def validate_age(age):
    if not isinstance(age, int):
        raise TypeError("年龄必须是整数")
    if not 0 <= age <= 150:
        raise InvalidAgeError("年龄应在 0 到 150 之间")
    return age


@contextmanager
def managed_resource(name):
    print(f"获取资源: {name}")
    try:
        yield {"name": name, "status": "ready"}
    finally:
        print(f"释放资源: {name}")


def main():
    for age in [20, -1, "18"]:
        try:
            print("合法年龄:", validate_age(age))
        except (InvalidAgeError, TypeError) as error:
            print(f"处理异常 ({type(error).__name__}):", error)
        else:
            print("没有异常时执行 else")
        finally:
            print("无论如何都会执行 finally")

    with managed_resource("database connection") as resource:
        print("使用资源:", resource)

    # StringIO 是内存中的“文件”，可以安全演示 with 的自动关闭。
    with StringIO() as buffer:
        buffer.write("hello\npython")
        print("内存文件内容:", buffer.getvalue())


if __name__ == "__main__":
    main()
