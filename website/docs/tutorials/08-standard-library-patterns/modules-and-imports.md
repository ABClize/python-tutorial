# Python 模块、包与 import

模块用于组织 Python 代码。把相关的函数、类和常量放进模块与包，可以避免所有代码堆在一个文件中，
也能让不同文件复用同一份实现。

<p class="source-note">对应源码：<code>python/python_interview_practice/12_standard_library_patterns.py</code></p>

## 模块与 import

一个 `.py` 文件就是一个 Python 模块。假设 `price.py` 包含：

```python
TAX_RATE = 0.06


def add_tax(price: float) -> float:
    return price * (1 + TAX_RATE)
```

导入整个模块：

```python
import price

print(price.TAX_RATE)
print(price.add_tax(100))
```

运行结果：

```text
0.06
106.0
```

`import price` 把模块对象绑定到变量 `price`，模块成员通过 `price.add_tax` 访问，来源清楚。

只导入指定名字：

```python
from price import add_tax

print(add_tax(100))
```

常见形式：

```python
import pathlib
import datetime as dt
from collections import Counter
from pathlib import Path
```

避免 `from module import *`。它会把大量名字加入当前命名空间，来源不清楚，也可能覆盖已有名字。

## 模块何时执行

模块顶层语句会在当前进程第一次导入时执行，后续导入通常复用 `sys.modules` 中的模块对象。

只希望直接运行文件时执行的代码放进入口判断：

```python
def main() -> None:
    print("直接运行当前文件")


if __name__ == "__main__":
    main()
```

直接运行时 `__name__` 是 `"__main__"`；作为模块导入时，`__name__` 是模块名。

## 包与导入路径

包把多个模块组织到同一个命名空间：

```text
shop/
├── __init__.py
├── price.py
└── order.py
```

包外通常使用绝对导入：

```python
from shop.price import add_tax
```

包内部可以使用相对导入：

```python
from .price import add_tax
```

应用代码优先使用清晰的绝对导入；相对导入适合表达同一个包内部的关系。导入失败时，应先检查运行入口、
当前工作目录、包结构和 `sys.path`，不要在业务代码中随意追加绝对路径。
