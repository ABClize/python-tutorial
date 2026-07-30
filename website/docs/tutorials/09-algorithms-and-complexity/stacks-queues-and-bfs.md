# 栈、队列与广度优先搜索

数据结构决定了数据以什么顺序被取出。栈是“后进先出”，队列是“先进先出”。括号匹配需要回到最近
尚未闭合的括号，适合用栈；按距离由近到远访问节点，适合用队列。

<p class="source-note">对应源码：<code>python/python_interview_practice/08_algorithms.py</code></p>

## 栈：后进先出

Python 没有单独的内置 `Stack` 类型，通常直接使用列表：

```python
stack: list[str] = []

stack.append("A")
stack.append("B")

print(stack.pop())
print(stack.pop())
```

运行结果：

```text
B
A
```

`append()` 把元素放到末尾，`pop()` 从末尾取出。两者的摊销时间复杂度都是 O(1)。

不要频繁用 `list.pop(0)` 实现队列。删除第一项后，后面的所有引用都要向前移动，单次操作是 O(n)。

## 用栈检查括号

左括号出现时暂时不能确定它和谁匹配，需要保存起来。右括号出现时，它必须匹配最近保存的左括号，
这正好符合后进先出的顺序。

```python
def valid_brackets(text: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []

    for char in text:
        if char in "([{":
            stack.append(char)
        elif char in pairs and (not stack or stack.pop() != pairs[char]):
            return False

    return not stack


print(valid_brackets("{[()]()}"))
print(valid_brackets("([)]"))
print(valid_brackets("(()"))
```

运行结果：

```text
True
False
False
```

处理规则如下：

1. 遇到左括号就入栈；
2. 遇到右括号时，栈不能为空；
3. 弹出的最近一个左括号必须与当前右括号匹配；
4. 扫描结束后，栈必须为空。

`"([)]"` 在读到 `)` 时，栈顶是 `[`，立即返回 `False`。`"(()"` 虽然扫描过程中没有错配，
但最后仍有一个 `(` 留在栈中，所以也不是有效括号。

每个字符最多入栈和出栈一次，时间复杂度为 O(n)。最坏情况下栈保存全部左括号，空间复杂度为
O(n)。

## 队列：先进先出

队列需要高效地从左侧取出元素，标准库的 `collections.deque` 更合适：

```python
from collections import deque

queue = deque(["A", "B"])
queue.append("C")

print(queue.popleft())
print(queue.popleft())
```

运行结果：

```text
A
B
```

`append()` 在右端加入，`popleft()` 从左端取出，两者都是 O(1)。

## 广度优先搜索为什么使用队列

广度优先搜索，简称 BFS，会先访问离起点一步的节点，再访问两步、三步的节点。队列能保留“先发现
的节点先处理”的顺序。

下面用字典表示一个无向图：

```python
from collections import deque


def breadth_first_order(
    graph: dict[str, list[str]],
    start: str,
) -> list[str]:
    queue = deque([start])
    visited = {start}
    order: list[str] = []

    while queue:
        node = queue.popleft()
        order.append(node)

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order


graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "E"],
    "D": ["B"],
    "E": ["C"],
}

print(breadth_first_order(graph, "A"))
```

运行结果：

```text
['A', 'B', 'C', 'D', 'E']
```

`visited` 在节点入队时就更新，而不是等节点出队后再更新。否则同一个节点可能被多个相邻节点重复
加入队列。

如果图有 `V` 个顶点、`E` 条边，邻接表形式的 BFS 会访问每个顶点一次并检查每条边，时间复杂度为
O(V + E)，队列和 `visited` 的额外空间为 O(V)。

## 用 BFS 求无权图的最短步数

队列还能同时保存当前距离：

```python
from collections import deque


def shortest_steps(
    graph: dict[str, list[str]],
    start: str,
    target: str,
) -> int:
    queue = deque([(start, 0)])
    visited = {start}

    while queue:
        node, distance = queue.popleft()
        if node == target:
            return distance

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, distance + 1))

    return -1


graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "E"],
    "D": ["B", "E"],
    "E": ["C", "D"],
}

print(shortest_steps(graph, "A", "E"))
```

运行结果：

```text
2
```

BFS 第一次到达某个节点时，所经过的边数最少。这个结论适用于每条边代价相同的图；如果边有不同
权重，就不能直接用普通 BFS 计算最小总权重。

## 选择栈还是队列

| 需求 | 数据结构 | 原因 |
| --- | --- | --- |
| 回到最近未处理的位置 | 栈 | 后进先出 |
| 括号匹配、撤销操作 | 栈 | 最新状态先处理 |
| 按到达顺序处理任务 | 队列 | 先进先出 |
| 按层遍历、无权最短步数 | 队列 | 先处理距离较近的节点 |

选择数据结构时，先问“下一次应该取出哪一项”，通常比从算法名称反推更直观。
