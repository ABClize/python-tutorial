# Python 面试学习项目

这个仓库由两个彼此独立的工程组成：`python/` 保存可运行的学习代码和测试，`website/`
保存面向阅读的 VitePress 教程站点。教程中的概念、代码和路径都以 Python 工程为依据。

```text
.
├── python/       # Python 示例、练习、FastAPI 项目、测试和 uv 配置
├── website/      # VitePress、Markdown 教程和 Vue/Plotly 可视化
├── .vscode/      # 跨两个工程的工作区任务和调试配置
├── AGENTS.md     # 仓库协作约定
└── README.md
```

## 查看教程

```bash
cd website
npm install
npm run docs:dev
```

然后打开终端显示的本地地址，默认是 <http://localhost:5173>。

教程包含 16 个主题，从基础类型、引用、函数和数据模型，一直覆盖算法、测试、并发、FastAPI、
Pydantic v2 和异步可靠性。交互图用于解释对象引用、生成器执行帧、复杂度、内存增长、线程竞态和
asyncio 时间线。

## 运行 Python 示例

```bash
cd python
uv sync --group dev
uv run python run_all.py
uv run pytest -v
```

Python 工程的完整目录说明和命令见 [`python/README.md`](python/README.md)，教程站点的维护说明见
[`website/README.md`](website/README.md)。

## VS Code

从仓库根目录打开 VS Code。工作区会推荐 Python、Debugger、Pylance 和 Vue - Official 扩展。

- `Ctrl+Shift+B`：运行 Python 测试；
- “运行和调试”：调试示例、pytest 或 FastAPI；
- “终端 → 运行任务 → Docs: 启动教程站点”：启动 VitePress。
