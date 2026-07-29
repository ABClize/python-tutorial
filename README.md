# Python 面试学习实验室

这是一个可以直接运行、断点调试、自动测试和使用 Jupyter 分步实验的 Python
面试学习项目。目标不是背答案，而是形成以下循环：

> 预测输出 → 运行代码 → 断点观察 → 修改条件 → 自动测试 → 口头解释

## 快速开始

项目使用 Python 3.11 和 `uv` 管理环境：

```bash
uv sync --group dev
uv run python run_all.py
uv run pytest -v
uv run uvicorn backend_interview.main:app --reload
uv run jupyter lab
```

VS Code 打开项目后会推荐 Python、Debugger、Pylance 和 Jupyter 扩展，并默认使用
`.venv/bin/python`。按 `Ctrl+Shift+B` 可以运行默认测试任务；运行和调试面板中可以
调试主程序、当前文件、全部 pytest 或当前测试文件。

## 项目结构

```text
.
├── python_interview_practice/  # 按主题编号的可运行讲解
├── interview_exercises/        # 面试题、参考实现和自检
├── backend_interview/          # FastAPI、Pydantic v2、asyncio 项目实战
├── tests/                      # unittest、pytest、Hypothesis 属性测试
├── notebooks/                  # 可调参数、图示和时间线组成的 Jupyter 概念教程
├── tools/                      # Notebook 构建工具
├── run_all.py                  # 隔离运行所有编号示例
└── pyproject.toml              # 开发依赖和工具配置
```

## 覆盖范围

| 阶段 | 主题 |
| --- | --- |
| 基础 | 字符串、列表、元组、字典、集合、推导式、真值、对象身份 |
| 函数 | 参数、作用域、闭包、递归、装饰器、函数是一等对象 |
| 对象模型 | 可变性、深浅拷贝、继承、MRO、描述符、魔术方法、数据类 |
| 迭代 | 可迭代对象、迭代器、生成器、惰性计算、`itertools` |
| 类型系统 | 类型标注、泛型、`Protocol`、`TypeVar`、`TypedDict` |
| 工程能力 | 异常、上下文管理器、测试、Mock、依赖注入、代码质量 |
| 并发 | 线程、锁、线程池、`asyncio`、任务、超时和队列 |
| 现代后端 | FastAPI、Pydantic v2、认证、幂等、乐观锁、依赖覆盖 |
| 可靠性 | 限流、重试、取消、缓存击穿、生命周期、可观测性 |
| 性能 | 时间复杂度、`timeit`、`cProfile`、`tracemalloc`、内存模型 |
| 算法 | 哈希表、栈、队列、二分、排序、双指针、动态规划 |
| 标准库 | `collections`、`functools`、`heapq`、`bisect`、`pathlib` |

## 推荐学习方法

### 第一遍：只读和预测

打开 `python_interview_practice/` 中的一个文件，先不要运行。在纸上写出输出、对象
是否共享、异常会出现在哪里以及时间复杂度。

### 第二遍：运行和断点

选择 VS Code 的“Python: 调试当前文件”，重点观察：

- 当前局部变量和调用栈；
- `id(a)`、`a is b`、`a[0] is b[0]`；
- 递归每一层的参数；
- 生成器停在 `yield` 的位置；
- 装饰器包装前后的函数对象。

### 第三遍：做题和测试

先看 `interview_exercises/` 的题目，遮住参考实现。完成后运行：

```bash
uv run pytest -v
```

测试失败时先读失败样例，不要立刻看答案。重点补齐空输入、重复值、Unicode、错误
类型和大输入等边界条件。

### 第四遍：分步实验

在 `notebooks/` 中操作下拉框和滑块，观察对象引用图、生成器暂停状态和 asyncio
任务时间线如何变化；再修改输入并重新执行单元格。Notebook 适合建立执行模型，但最终答案
仍应整理成可以从头运行的函数和测试，避免依赖隐藏状态。

### 第五遍：模拟口述

对每道题至少回答：

1. 方案是什么？
2. 为什么正确？
3. 时间和空间复杂度是多少？
4. 有哪些边界条件？
5. 如果数据量扩大十倍，会改什么？
6. 有没有更 Pythonic 或更易维护的写法？

### 第六遍：项目场景面试

进入 [`backend_interview/`](backend_interview/README.md)，运行订单 API 并配合
[`QUESTIONS.md`](backend_interview/QUESTIONS.md) 练习。这里不只问框架语法，还要求解释：

- 为什么路由、服务、仓储和外部网关要分层；
- 取消、超时、并发上限和幂等如何共同影响可靠性；
- Pydantic 校验边界、领域规则和数据库约束应分别放在哪里；
- 如何用同步客户端、异步客户端、依赖覆盖和 Fake 设计可维护测试。

## 常用命令

```bash
# 隔离运行全部编号示例
uv run python run_all.py

# 自动测试
uv run pytest -v

# 分支覆盖率
uv run pytest --cov --cov-report=term-missing

# 代码风格和常见错误
uv run ruff check .

# 静态类型检查
uv run mypy run_all.py interview_exercises python_interview_practice backend_interview

# 启动现代后端项目（Swagger UI: http://127.0.0.1:8000/docs）
uv run uvicorn backend_interview.main:app --reload

# 只运行后端场景测试
uv run pytest tests/backend -v

# 启动 Notebook
uv run jupyter lab

# 重新生成 Notebook
uv run python tools/build_notebooks.py
```

学习时可以故意改坏一个实现，观察测试、Ruff、Mypy 和调试器分别能发现哪一类问题。
