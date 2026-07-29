# Python 学习工程

这里保存所有可运行的 Python 示例、练习、后端项目和测试。目标不是只背面试答案，而是形成：

> 预测行为 → 运行代码 → 断点观察 → 测试边界 → 口头解释

## 目录

```text
python/
├── python_interview_practice/  # 15 个按编号排列的概念示例
├── interview_exercises/        # 可复用的算法、容器、OOP 和并发练习
├── backend_interview/          # 分层 FastAPI 订单 API
├── tests/                      # pytest、Hypothesis 和后端测试
├── run_all.py                  # 隔离运行全部编号示例
├── pyproject.toml              # Python 依赖和工具配置
└── uv.lock                     # 锁定依赖
```

## 常用命令

在当前 `python/` 目录执行：

```bash
uv sync --group dev
uv run python run_all.py
uv run pytest -v
uv run pytest tests/backend -v
uv run pytest --cov --cov-report=term-missing
uv run ruff check .
uv run mypy run_all.py interview_exercises python_interview_practice backend_interview
uv run uvicorn backend_interview.main:app --reload
```

## 建议阅读顺序

1. `python_interview_practice/01_*.py` 到 `15_*.py`：建立语言和工程概念；
2. `interview_exercises/`：遮住实现，依据测试自己完成；
3. `backend_interview/README.md`：把类型、异常、依赖注入和 asyncio 放进真实请求流；
4. `tests/`：从测试名称和断言反推行为契约。

配套概念教程位于仓库的 `website/` 工程。
