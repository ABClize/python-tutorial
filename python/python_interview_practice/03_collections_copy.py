"""容器操作、排序，以及浅拷贝与深拷贝。"""

import copy
from collections import Counter, defaultdict, deque
from typing import TypedDict


class StudentRecord(TypedDict):
    name: str
    score: int


def copy_examples():
    original = [[1, 2], [3, 4]]
    assignment = original
    shallow = original.copy()
    deep = copy.deepcopy(original)

    original[0].append(99)
    print("赋值:", assignment)
    print("浅拷贝:", shallow)
    print("深拷贝:", deep)
    print("最外层 id:", id(original), id(shallow), id(deep))
    print("内层 id:", id(original[0]), id(shallow[0]), id(deep[0]))


def collections_examples():
    words = ["python", "java", "python", "go", "python", "go"]
    print("Counter:", Counter(words))

    groups = defaultdict(list)
    for word in words:
        groups[len(word)].append(word)
    print("defaultdict:", dict(groups))

    queue = deque(["first", "second"])
    queue.append("third")
    print("队列弹出:", queue.popleft(), list(queue))


def sorting_examples():
    students: list[StudentRecord] = [
        {"name": "Alice", "score": 88},
        {"name": "Bob", "score": 95},
        {"name": "Carol", "score": 88},
    ]
    by_score = sorted(students, key=lambda student: (-student["score"], student["name"]))
    print("按分数降序、姓名升序:", by_score)


def remove_duplicates_keep_order(items):
    """面试常见：去重且保持首次出现的顺序。"""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def main():
    print("--- 拷贝 ---")
    copy_examples()
    print("\n--- collections ---")
    collections_examples()
    print("\n--- 排序 ---")
    sorting_examples()
    print("\n--- 去重 ---")
    print(remove_duplicates_keep_order([3, 1, 3, 2, 1, 4, 2]))


if __name__ == "__main__":
    main()
