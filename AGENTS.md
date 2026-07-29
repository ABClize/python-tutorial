# 仓库协作指南

## 语言约定

- 项目文档、代码注释、文档字符串和 `AGENTS.md` 在表达准确的前提下优先使用中文。
- 命令、代码标识符、协议字段、库名及业内通用术语保留原文，避免生硬翻译影响检索和理解。
- 修改既有内容时保持必要的上下文一致性，不为统一语言而批量改写无关文件。

## 项目结构与模块组织

- `python_interview_practice/` 包含按编号排列、可直接运行的课程。新增主题时沿用现有
  `NN_topic.py` 编号顺序。
- `interview_exercises/` 包含按主题归类、可复用的练习实现。
- `backend_interview/` 是分层的 FastAPI 示例，包含路由、Schema、服务、仓储、领域对象和网关。
  扩展功能时保持这些边界。
- `tests/` 对应课程和练习模块；`tests/backend/` 覆盖 API 示例。
- `notebooks/` 存放生成的教程，`tools/build_notebooks.py` 是其生成源。根目录下的
  `run_all.py` 等脚本提供仓库级入口。

## 构建、测试与开发命令

在仓库根目录使用 `uv`：

```bash
uv sync --group dev                         # 安装运行时和开发依赖
uv run python run_all.py                    # 独立执行所有编号课程
uv run pytest -v                            # 运行完整测试套件
uv run pytest tests/backend -v              # 仅运行 FastAPI 后端测试
uv run pytest --cov --cov-report=term-missing
uv run ruff check .                         # 检查代码规范和导入顺序
uv run mypy run_all.py interview_exercises python_interview_practice backend_interview
uv run uvicorn backend_interview.main:app --reload
uv run python tools/build_notebooks.py       # 重新生成确定性的 notebooks
```

## 编码风格与命名约定

目标版本为 Python 3.11 或更高。使用四空格缩进、类型注解、简洁的文档字符串，以及
100 字符行宽限制。Ruff 启用 `E`、`F`、`I`、`B`、`UP` 和 `SIM` 规则，提交前应运行检查。
模块、函数、fixture 和变量使用 `snake_case`，类使用 `PascalCase`，常量使用
`UPPER_SNAKE_CASE`。优先使用显式依赖注入，并避免让 FastAPI 类型进入领域层和服务层。

## 测试指南

测试使用 pytest、pytest-asyncio、Hypothesis，并在少数场景使用 unittest 风格。测试文件命名为
`test_<subject>.py`，测试函数命名为 `test_<behavior>()`。应覆盖正常、边界和失败场景；当某项
不变量需要在大量输入下成立时，使用属性测试。覆盖率配置包含三个源码包并启用分支统计，但不设置
最低百分比。每项行为变更都应包含聚焦的回归测试。

## Commit 与 Pull Request 指南

遵循仓库现有的 Conventional Commits 历史，例如 `feat: add generator exercises`、
`docs: clarify asyncio cancellation` 或 `fix: preserve idempotent order creation`。每个 commit
应保持聚焦。Pull Request 应说明学习内容或运行时行为的变化、列出验证命令并关联相关 issue；
只有 notebook 或渲染文档发生变化时才需要截图。不要提交 `.venv`、覆盖率产物、缓存或 `.env`
中的敏感信息。
