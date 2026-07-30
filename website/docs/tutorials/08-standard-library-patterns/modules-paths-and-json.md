# Python 模块、pathlib 与 JSON

模块用于组织 Python 代码，`pathlib` 用对象表示文件系统路径，`json` 负责基础数据的编码和解码。
这三类工具经常一起出现在配置读取、文件处理和接口数据交换中。

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

## pathlib 路径对象

`pathlib` 用对象表示路径，`/` 运算符负责拼接：

```python
from pathlib import PurePosixPath

report_path = PurePosixPath("data") / "report.txt"

print(report_path.as_posix())
print(report_path.name)
print(report_path.stem)
print(report_path.suffix)
print(report_path.parent.as_posix())
```

运行结果：

```text
data/report.txt
report.txt
report
.txt
data
```

这里使用 `PurePosixPath` 和 `as_posix()` 只为了让教程输出在不同平台保持一致。真实文件操作使用
`Path`，它会遵循当前操作系统的路径规则。

## 创建目录与读写文本

```python
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as directory:
    output_dir = Path(directory) / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "report.txt"
    report_path.write_text(
        "Python: 3 小时\nSQL: 2 小时\n",
        encoding="utf-8",
    )
    lines = report_path.read_text(encoding="utf-8").splitlines()

print(lines)
```

运行结果：

```text
['Python: 3 小时', 'SQL: 2 小时']
```

`parents=True` 会一起创建缺少的父目录，`exist_ok=True` 表示目录已存在时不报错。`write_text()`
默认覆盖文件；追加内容需要使用 `path.open("a")`。

常用路径操作：

| 方法或属性 | 作用 |
| --- | --- |
| `exists()` | 路径是否存在 |
| `is_file()` / `is_dir()` | 判断文件或目录 |
| `mkdir()` | 创建目录 |
| `iterdir()` | 遍历直接子项 |
| `glob()` / `rglob()` | 按模式查找 |
| `read_text()` / `write_text()` | 一次性读写文本 |
| `open()` | 以文件对象方式打开 |
| `resolve()` | 得到规范化绝对路径 |
| `relative_to()` | 计算相对路径 |

大文件不要一次全部读入内存：

```python
from pathlib import Path

path = Path("large.log")
with path.open(encoding="utf-8") as file:
    for line in file:
        process(line.rstrip("\n"))
```

## JSON 类型对应

JSON 适合在程序、配置文件和 HTTP 接口之间传递基础数据：

| Python | JSON |
| --- | --- |
| `dict` | object |
| `list`、`tuple` | array |
| `str` | string |
| `int`、`float` | number |
| `True`、`False` | true、false |
| `None` | null |

## dumps 与 loads

```python
import json

record = {
    "topic": "Python",
    "hours": 3,
    "completed": True,
    "note": None,
}

text = json.dumps(record, ensure_ascii=False, indent=2)
print(text)

loaded = json.loads(text)
print(loaded["topic"])
```

运行结果：

```text
{
  "topic": "Python",
  "hours": 3,
  "completed": true,
  "note": null
}
Python
```

`ensure_ascii=False` 让中文直接写入结果，`indent=2` 生成便于阅读的缩进。

## dump 与 load

```python
import json
from pathlib import Path
from tempfile import TemporaryDirectory

records = [
    {"topic": "Python", "hours": 3},
    {"topic": "SQL", "hours": 2},
]

with TemporaryDirectory() as directory:
    path = Path(directory) / "records.json"

    with path.open("w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)

    with path.open(encoding="utf-8") as file:
        loaded = json.load(file)

print(loaded[0]["topic"])
```

运行结果：

```text
Python
```

JSON 不会自动保存 `datetime`、`Decimal`、`Path` 或自定义类。编码前需要转换为字符串、数字、列表和
字典，解码后也不会自动恢复原类型。

外部 JSON 成功解码只说明语法有效，不代表字段完整、类型正确或数值范围合理，业务边界仍需验证。

## 路径与 JSON 注意事项

- 文本文件显式指定编码。
- 不要依赖当前工作目录恰好位于某处，应用应明确配置数据根目录。
- `write_text()` 会覆盖文件，重要数据需要考虑临时文件和原子替换。
- 用户提供的路径要防止越过允许目录。
- JSON 不是 Python 对象序列化格式，不保存方法和共享引用。
- 解码外部 JSON 后仍要执行运行时校验。
