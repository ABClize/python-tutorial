# Python 条件语句与循环

条件语句根据判断结果选择要执行的代码。循环让一段代码重复执行。Python 常用 `if` 处理分支，
用 `for` 或 `while` 处理重复操作。

<!-- 对应源码：python/python_interview_practice/01_basic_types.py -->

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

## `pass` 占位

`pass` 是空操作。Python 执行到它时，什么也不做。语法要求必须写一条语句，但暂时没有代码可执行时，
可以使用 `pass` 占位。

下面的例子也说明 `pass` 与 `continue` 不同：

```python
for status in ["ready", "skip"]:
    if status == "skip":
        pass
    print(status)
```

运行结果：

```text
ready
skip
```

处理 `"skip"` 时虽然执行了 `pass`，后面的 `print(status)` 仍会继续执行。要跳过本轮剩余代码，
应使用 `continue`。

## 循环的 `else`

`for` 和 `while` 都可以带 `else`。循环正常结束时执行 `else`；如果循环被 `break` 提前结束，
则不执行 `else`。

下面查找列表中的奇数：

```python
for number in [2, 4, 6]:
    if number % 2 != 0:
        print("找到奇数：", number)
        break
else:
    print("没有找到奇数")
```

运行结果：

```text
没有找到奇数
```

列表中的数都是偶数，循环没有执行 `break`，所以最后进入 `else`。如果列表中出现奇数，
程序会执行 `break`，并跳过 `else`。

循环 `else` 常用于“查找失败后处理”。不要把它理解成与循环体中某个 `if` 配对的分支，关键要看
循环是否被 `break` 中止。

## `match` 与 `case`

`match` 根据值的结构选择分支。Python 会从上到下尝试各个 `case`，只执行第一个匹配成功并且
守卫条件（guard）成立的分支。

### 字面量、`|` 和 `_`

字面量模式直接匹配固定值。竖线 `|` 表示“匹配其中任意一个”，下划线 `_` 匹配其他所有情况，
但不会绑定变量：

```python
status = 404

match status:
    case 200:
        message = "成功"
    case 400 | 404:
        message = "请求错误"
    case _:
        message = "其他状态"

print(message)
```

运行结果：

```text
请求错误
```

`404` 不匹配第一个 `case`，但能匹配 `400 | 404`，因此程序不再尝试后面的 `_`。
不带守卫条件的 `_` 会匹配任何值，所以必须放在最后。

### 序列模式和守卫条件

序列模式可以像解包一样匹配 list 或 tuple，并把元素绑定到变量。守卫条件是写在模式后面的
`if` 条件，模式和守卫条件都成立时才执行该分支：

```python
command = ["move", 3, 5]

match command:
    case ["move", x, y] if x >= 0 and y >= 0:
        result = f"移动到 ({x}, {y})"
    case ["move", x, y]:
        result = f"坐标不能为负数：({x}, {y})"
    case ["quit"]:
        result = "退出"
    case _:
        result = "未知命令"

print(result)
```

运行结果：

```text
移动到 (3, 5)
```

第一个元素必须是字面量 `"move"`。后两个元素分别绑定给 `x` 和 `y`。两个坐标都不小于 `0`，
守卫条件成立，所以执行第一个分支。

### 裸名字会捕获值

`case` 中的裸名字不是常量比较，而是捕获模式。它会匹配当前值，并把值绑定到这个名字：

```python
value = "failed"

match value:
    case captured:
        print(captured)
```

运行结果：

```text
failed
```

上面的 `captured` 会接收 `value` 的值，因此这个分支总能匹配。假设已经定义
`READY = "ready"`，写 `case READY:` 仍会捕获值，不会与字符串 `"ready"` 比较。

比较固定值时应直接写 `case "ready":`。未加守卫条件的捕获模式总能匹配，也必须放在最后；
在它后面继续写其他 `case` 会产生 `SyntaxError`。
