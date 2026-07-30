# Python 模块、命令行参数与 uv

一个 `.py` 文件就是一个模块。包是由多个模块组成的目录。使用模块和包，可以把函数、类和常量分开
保存，并在其他文件中通过 `import` 复用。Python 也可以直接运行脚本，或者用 `-m` 按模块名运行。
需要接收命令行参数时，可以使用标准库 `argparse`。

<!-- 对应源码：python/python_interview_practice/12_standard_library_patterns.py -->

## 模块与 import

先创建一个 `price.py` 文件，内容如下：

```python
TAX_RATE = 0.06


def add_tax(price: float) -> float:
    return price * (1 + TAX_RATE)
```

然后在另一个文件中导入整个模块：

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

应用代码优先使用清晰的绝对导入；同一个包内部也可以使用相对导入。导入失败时，先检查运行入口、当前
工作目录、包结构和 `sys.path`，不要在业务代码中随意追加绝对路径。

## 直接运行脚本与使用 python -m

直接运行脚本时，命令后面写文件路径：

```bash
python tools/report.py
```

解释器读取这个文件，并把脚本所在目录放到模块搜索路径的开头。脚本中的 `__name__` 是
`"__main__"`。

使用 `-m` 时，命令后面写模块名，不写 `.py`：

```bash
python -m shop.report
```

解释器会按照正常的导入规则在 `sys.path` 中查找 `shop.report`，然后把它作为入口模块运行。
此时 `__name__` 同样是 `"__main__"`。包内模块使用相对导入时，通常应从包的上级目录执行
`python -m package.module`，这样 Python 能识别完整包名。

本项目可以在 `python/` 目录运行标准库示例：

```bash
uv run python python_interview_practice/12_standard_library_patterns.py
uv run python -m python_interview_practice.12_standard_library_patterns
```

两条命令都会执行文件末尾的 `main()`。第一条按路径打开文件，第二条通过导入机制定位模块。

## argparse 读取命令行参数

`argparse` 用于定义命令行参数、生成帮助信息并检查输入。下面的程序接收一个位置参数 `topic`，还接收
可选参数 `--hours` 和 `--verbose`：

```python
import argparse

parser = argparse.ArgumentParser(
    prog="study-report",
    description="生成学习记录",
)
parser.add_argument("topic", help="学习主题")
parser.add_argument(
    "-n",
    "--hours",
    type=int,
    default=1,
    help="学习小时数",
)
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="显示详细信息",
)

arguments = parser.parse_args()
print(
    arguments.topic,
    arguments.hours,
    arguments.verbose,
)
```

假设文件名为 `report.py`，可以这样运行：

```bash
python report.py Python --hours 3 --verbose
```

运行结果：

```text
Python 3 True
```

各参数的作用如下：

- `topic` 没有 `-` 前缀，是位置参数。调用时通常必须按位置提供。
- `-n` 和 `--hours` 是同一个可选参数的短名称和长名称。
- `type=int` 在解析时把文本 `"3"` 转成整数 `3`。无法转换时，`argparse` 会显示用法和错误。
- `default=1` 表示没有传入 `--hours` 时使用 `1`。
- `action="store_true"` 表示出现 `--verbose` 时得到 `True`，没有出现时得到 `False`。

不传参数或只想查看说明时，可以运行：

```bash
python report.py --help
```

`parse_args()` 默认读取当前进程的 `sys.argv[1:]`。测试和教程示例也可以传入固定列表：

```python
arguments = parser.parse_args(
    ["Python", "--hours", "3", "--verbose"]
)
```

本项目源码使用固定列表演示，因此直接运行时输出不会受编辑器、测试工具或额外命令行参数影响。真正的
命令行程序通常使用不带参数的 `parse_args()`。

## 虚拟环境是什么

虚拟环境为一个项目提供独立的 Python 可执行文件和第三方包目录。项目 A 安装的包和版本不会直接改变
项目 B 的环境，也不会写入系统 Python。

虚拟环境不是容器或安全沙箱。它主要解决依赖隔离问题，不能限制文件、网络或进程权限。

本项目的虚拟环境位于 `python/.venv/`。这个目录可以重新创建，不应提交到 Git。

## 本项目的 uv 工作流

本项目使用 uv 管理依赖和虚拟环境。相关文件如下：

| 文件或目录 | 作用 |
| --- | --- |
| `pyproject.toml` | 保存项目元数据、Python 版本要求、直接依赖和工具配置 |
| `uv.lock` | 保存解析后的确切版本与平台条件，应提交到 Git，不要手工修改 |
| `.venv/` | 当前机器上的项目虚拟环境，由 uv 创建和同步 |

在 `python/` 目录执行：

```bash
uv sync --group dev
```

`uv sync` 会根据 `pyproject.toml` 和 `uv.lock` 准备 `.venv`。环境不存在时会创建，依赖变化时会同步。

新增运行依赖使用：

```bash
uv add requests
```

`uv add` 会更新 `pyproject.toml`，重新解析 `uv.lock`，并同步项目环境。不要只手工修改 `.venv`
中的包，否则其他机器无法根据项目文件重建相同环境。

运行项目命令时使用 `uv run`：

```bash
uv run python run_all.py
uv run pytest -v
uv run ruff check .
```

`uv run` 会在项目 `.venv` 中执行命令，并在运行前检查锁文件和环境是否需要更新。因此使用这套工作流
时，不要求先手动执行 `source .venv/bin/activate`。手动激活只是另一种可选用法。
