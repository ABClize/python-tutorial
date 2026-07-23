"""函数、参数、作用域、闭包和装饰器。"""

from functools import wraps


def parameters(name, age=18, *scores, city="Shanghai", **extra):
    """位置参数、默认参数、可变位置参数和关键字参数。"""
    return {
        "name": name,
        "age": age,
        "scores": scores,
        "city": city,
        "extra": extra,
    }


def scope_example():
    message = "外层变量"

    def inner():
        # 不赋值时，能读取外层作用域中的 message
        return message

    return inner()


def counter_factory():
    """闭包：函数记住了创建时所在作用域的 count。"""
    count = 0

    def increment(step=1):
        nonlocal count
        count += step
        return count

    return increment


def log_calls(func):
    """装饰器：在不修改原函数代码的前提下增加功能。"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__}: args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"返回值: {result}")
        return result

    return wrapper


@log_calls
def add(left, right):
    return left + right


def recursion_example(number):
    """递归：每次调用都必须更接近终止条件。"""
    if number <= 1:
        return 1
    return number * recursion_example(number - 1)


def main():
    print("参数:", parameters("Alice", 20, 88, 92, city="Beijing", hobby="reading"))
    print("作用域:", scope_example())

    counter = counter_factory()
    print("闭包计数:", counter(), counter(), counter(3))

    print("装饰器结果:", add(2, 5))
    print("5 的阶乘:", recursion_example(5))


if __name__ == "__main__":
    main()
