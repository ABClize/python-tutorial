"""Python 面试基础示例：运行 `python3.11 python_interview_examples.py` 查看结果。"""

import copy


def copy_example():
    """浅拷贝与深拷贝。"""
    original = [[1, 2], [3, 4]]
    shallow = original.copy()  # 只复制最外层列表
    deep = copy.deepcopy(original)  # 递归复制所有嵌套对象

    original[0].append(99)
    print("原列表:", original)
    print("浅拷贝:", shallow)  # 内层列表仍然是同一个对象，能看到 99
    print("深拷贝:", deep)  # 内层列表独立，不会看到 99


def mutable_default_argument_example():
    """高频陷阱：不要把 [] 直接作为函数默认值。"""

    def append_bad(value, items=[]):  # noqa: B006 - 故意演示反例
        items.append(value)
        return items

    def append_good(value, items=None):
        if items is None:
            items = []
        items.append(value)
        return items

    print("错误写法:", append_bad("a"), append_bad("b"))
    print("正确写法:", append_good("a"), append_good("b"))


def generator_example():
    """yield 暂停函数；生成器按需产生值，适合大数据量。"""

    def squares(limit):
        for number in range(limit):
            yield number * number

    result = squares(4)
    print("生成器对象:", result)
    print("生成器转列表:", list(result))


def comprehension_example():
    """列表推导式与字典推导式。"""
    numbers = [1, 2, 3, 4, 5]
    even_squares = [number**2 for number in numbers if number % 2 == 0]
    square_map = {number: number**2 for number in numbers}
    print("偶数平方:", even_squares)
    print("平方字典:", square_map)


class Animal:
    """类、继承与方法重写。"""

    def speak(self):
        return "动物发出声音"


class Dog(Animal):
    def speak(self):
        return "汪汪"


def object_oriented_example():
    pet = Dog()
    print("继承后的方法:", pet.speak())
    print("Dog 是 Animal 吗:", isinstance(pet, Animal))


def main():
    print("\n--- 1. 浅拷贝和深拷贝 ---")
    copy_example()
    print("\n--- 2. 可变默认参数 ---")
    mutable_default_argument_example()
    print("\n--- 3. 生成器 ---")
    generator_example()
    print("\n--- 4. 推导式 ---")
    comprehension_example()
    print("\n--- 5. 面向对象 ---")
    object_oriented_example()


if __name__ == "__main__":
    main()
