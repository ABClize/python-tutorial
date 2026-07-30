# Python 条件语句与循环

顺序执行只能让程序从上到下做同一件事。条件语句让程序按情况选择路径，循环则让同一段代码重复执行。本页通过 if、for、while、break 和 continue 说明控制流程是怎样改变程序执行顺序的。

<p class="source-note">对应源码：<code>python/python_interview_practice/01_basic_types.py</code></p>

## 条件语句

条件语句根据判断结果选择要执行的代码块。

基本语法：

```python
if 条件:
    条件成立时执行的代码
elif 另一个条件:
    另一个条件成立时执行的代码
else:
    所有条件都不成立时执行的代码
```

`elif` 和 `else` 都可以省略。

### 实例

```python
score = 82

if score >= 90:
    level = "优秀"
elif score >= 60:
    level = "通过"
else:
    level = "未通过"

print(level)
```

运行结果：

```text
通过
```

判断从上到下进行：

1. `82 >= 90` 为 `False`，跳过第一个代码块；
2. `82 >= 60` 为 `True`，执行第二个代码块；
3. 已经找到成立的分支，后面的 `else` 不再执行。

条件顺序会影响结果。范围更严格的条件通常放在前面。如果先判断 `score >= 60`，分数 `95` 会直接进入
“通过”分支，无法再到达“优秀”分支。

## `for` 循环

`for` 循环依次读取可迭代对象中的元素。

基本语法：

```python
for 变量 in 可迭代对象:
    循环体
```

### 遍历列表

```python
scores = [82, 91, 55]

for score in scores:
    print(score)
```

运行结果：

```text
82
91
55
```

循环执行三次。每次执行前，列表中的下一个元素会赋值给 `score`。

### 使用 `range()`

`range(stop)` 产生从 `0` 开始、到 `stop` 之前结束的整数：

```python
for number in range(3):
    print(number)
```

运行结果：

```text
0
1
2
```

`range(1, 6, 2)` 分别表示起始值、结束值和步长：

```python
print(list(range(1, 6, 2)))
```

运行结果：

```text
[1, 3, 5]
```

结束值 `6` 不包含在结果中。

## `while` 循环

`while` 在条件为真时重复执行代码块。

基本语法：

```python
while 条件:
    循环体
```

### 实例

```python
countdown = 3

while countdown > 0:
    print(countdown)
    countdown -= 1

print("开始")
```

运行结果：

```text
3
2
1
开始
```

每轮循环都会让 `countdown` 减少 1。当它变为 `0` 时，条件 `countdown > 0` 为 `False`，循环结束。

如果循环体始终无法让条件变为假，就会产生无限循环。

## `break` 与 `continue`

`break` 立即结束整个循环：

```python
for number in [2, 4, 7, 8]:
    if number % 2 != 0:
        print("找到奇数：", number)
        break
```

运行结果：

```text
找到奇数： 7
```

`continue` 跳过本轮剩余代码，直接开始下一轮：

```python
for number in [2, -1, 3]:
    if number < 0:
        continue
    print(number)
```

运行结果：

```text
2
3
```
