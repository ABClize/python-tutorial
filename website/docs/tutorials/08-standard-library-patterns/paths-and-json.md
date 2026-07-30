# Python pathlib、JSON 与 CSV 文件读写

`pathlib` 用于创建、拼接和读写文件路径。`json` 用于把 Python 基础数据转换成 JSON 文本，也可以
把 JSON 文本解析成 Python 对象。`csv` 用于读写按行排列的表格文本。

<!-- 对应源码：python/python_interview_practice/12_standard_library_patterns.py -->

## pathlib 路径对象

`pathlib` 用对象表示路径，`/` 运算符负责拼接。下面构造一个表示 `data/report.txt` 的纯路径对象
（不会实际创建文件），再读取它的文件名、后缀和父目录：

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

下面在临时目录中创建 `output` 子目录，然后写入并读取文本：

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
| `resolve()` | 得到解析后的绝对路径，并处理 `.`、`..` 和符号链接 |
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

`dumps()` 把 Python 对象转换成 JSON 字符串，`loads()` 再把字符串解析回来：

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

`dump()` 和 `load()` 直接操作文件对象。下面把两条学习记录写入临时 JSON 文件，再读回来：

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

外部 JSON 成功解码只说明语法有效，不代表字段完整、类型正确或数值范围合理。使用数据前仍要检查。

## 使用 DictWriter 写入 CSV

CSV 的第一行通常是列名，后面每一行是一条记录。`csv.DictWriter` 可以按字典字段写入。下面把两条
学习记录写进临时文件：

```python
import csv
from pathlib import Path
from tempfile import TemporaryDirectory

records = [
    {"topic": "Python", "hours": 3},
    {"topic": "SQL", "hours": 2},
]

with TemporaryDirectory() as directory:
    path = Path(directory) / "study.csv"

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["topic", "hours"],
        )
        writer.writeheader()
        writer.writerows(records)

    with path.open(
        newline="",
        encoding="utf-8",
    ) as file:
        loaded_rows = list(csv.DictReader(file))

print(loaded_rows)
```

`fieldnames` 决定列名和列顺序。`writeheader()` 写入表头，`writerows()` 写入多条记录。字段中含有
逗号、引号或换行时，`csv` 模块会按 CSV 规则添加引号，不要自己用 `",".join(...)` 拼接。

## 使用 DictReader 读取 CSV

上面的代码接着使用 `csv.DictReader` 读取文件。它默认使用第一行作为字典的键。

运行结果：

```text
[{'topic': 'Python', 'hours': '3'}, {'topic': 'SQL', 'hours': '2'}]
```

CSV 文件保存的是文本。虽然写入前的 `hours` 是整数，读取后得到的 `"3"` 和 `"2"` 仍然是字符串。
需要计算时，要自己转换类型：

```python
converted_rows = [
    {
        "topic": row["topic"],
        "hours": int(row["hours"]),
    }
    for row in loaded_rows
]

print(converted_rows)
```

运行结果：

```text
[{'topic': 'Python', 'hours': 3}, {'topic': 'SQL', 'hours': 2}]
```

外部 CSV 可能有空值、缺列或非法数字。调用 `int()` 前，应根据数据要求检查并处理这些情况。

## 为什么要写 newline="" 和 encoding

使用 `csv` 模块打开文件时，推荐这样写：

```python
with path.open(
    "w",
    newline="",
    encoding="utf-8",
) as file:
    ...
```

`newline=""` 把换行处理交给 `csv` 模块，避免文本层再次修改换行，也能正确处理带换行的字段。
`encoding="utf-8"` 明确文件编码，包含中文时不会依赖操作系统默认编码。读和写应使用相同编码。

## 路径、JSON 与 CSV 注意事项

- 文本文件显式指定编码。
- 不要假定当前工作目录总在某个位置，应用应通过配置指定数据根目录。
- `write_text()` 会覆盖文件，重要数据需要考虑临时文件和原子替换。
- 用户提供的路径要防止越过允许目录。
- JSON 不是 Python 对象序列化格式，不保存方法和共享引用。
- 解码外部 JSON 后仍要执行运行时校验。
- 读写 CSV 时使用 `newline=""`，不要手工拼接带逗号的字段。
- CSV 读取结果默认是文本，数字、日期和布尔值需要显式转换和校验。
