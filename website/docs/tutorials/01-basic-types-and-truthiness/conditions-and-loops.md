# Python 条件语句与循环

条件语句根据判断结果选择要执行的代码。循环让一段代码重复执行。Python 常用 `if` 处理分支，
用 `for` 或 `while` 处理重复操作。

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

下面的例子根据分数选择等级。程序只会执行第一个符合条件的分支。

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

输出是“通过”。判断过程如下：

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

下面的循环依次打印列表中的三个分数。

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

列表有三个元素，所以循环执行三次。每次执行循环体之前，下一个元素会赋值给 `score`。

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

下面的例子从 `3` 开始倒数。每轮循环都会修改下一轮要判断的条件。

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

前三行来自循环。每轮都会让 `countdown` 减少 `1`。当它变为 `0` 时，
`countdown > 0` 为 `False`，循环结束，程序继续打印“开始”。

如果循环体始终无法让条件变为假，就会产生无限循环。

## `break` 与 `continue`

`break` 立即结束整个循环。下面的例子找到第一个奇数后就停止：

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

数字 `7` 满足条件，程序打印结果并执行 `break`。后面的 `8` 不再处理。

`continue` 跳过本轮剩余代码，直接开始下一轮。下面的例子忽略负数：

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

处理 `-1` 时会执行 `continue`，所以这一轮的 `print(number)` 被跳过。
