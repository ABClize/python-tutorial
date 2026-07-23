"""常见 Python 面试算法题：优先理解思路与复杂度。"""


def two_sum(numbers, target):
    """哈希表：时间 O(n)，空间 O(n)。"""
    seen = {}
    for index, number in enumerate(numbers):
        complement = target - number
        if complement in seen:
            return [seen[complement], index]
        seen[number] = index
    return []


def is_palindrome(text):
    """忽略非字母数字字符和大小写。"""
    chars = [char.lower() for char in text if char.isalnum()]
    return chars == chars[::-1]


def binary_search(numbers, target):
    """有序数组二分查找：时间 O(log n)。"""
    left, right = 0, len(numbers) - 1
    while left <= right:
        middle = (left + right) // 2
        if numbers[middle] == target:
            return middle
        if numbers[middle] < target:
            left = middle + 1
        else:
            right = middle - 1
    return -1


def valid_brackets(text):
    """栈：左括号入栈，右括号必须匹配栈顶。"""
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for char in text:
        if char in "([{":
            stack.append(char)
        elif char in pairs:
            if not stack or stack.pop() != pairs[char]:
                return False
    return not stack


def fibonacci_dynamic(number):
    """动态规划：避免递归的重复计算，时间 O(n)。"""
    if number < 2:
        return number
    previous, current = 0, 1
    for _ in range(2, number + 1):
        previous, current = current, previous + current
    return current


def main():
    print("两数之和:", two_sum([2, 7, 11, 15], 9))
    print("回文判断:", is_palindrome("A man, a plan, a canal: Panama"))
    print("二分查找:", binary_search([1, 3, 5, 7, 9, 11], 7))
    print("有效括号:", valid_brackets("{[()]()}"), valid_brackets("([)]"))
    print("第 10 个斐波那契数:", fibonacci_dynamic(10))


if __name__ == "__main__":
    main()
