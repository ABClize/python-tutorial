# 仓库协作指南

## 语言约定

- 项目文档、代码注释、文档字符串和 `AGENTS.md` 在表达准确的前提下优先使用中文。
- 命令、代码标识符、协议字段、库名及业内通用术语保留原文，避免生硬翻译影响检索和理解。
- 修改既有内容时保持必要的上下文一致性，不为统一语言而批量改写无关文件。

## 仓库结构

- `python/` 是独立的 Python 3.11+ / uv 工程，包含可运行课程、练习、FastAPI 示例和测试。
- `website/` 是独立的 VitePress / Vue 工程，包含 Markdown 教程和少量 Plotly 可视化。
- `docs/architecture/` 记录两个工程的长期边界与结构变更。
- `.vscode/` 提供从仓库根目录调试两个工程的任务配置。

不要在仓库根目录新增 Python 包或前端源码。Python 运行时代码进入 `python/`，教程正文和组件进入
`website/`，跨工程的长期说明才放在根目录文档中。

## Python 工程

- `python/python_interview_practice/` 包含按编号排列、可直接运行的课程；新增主题时沿用
  `NN_topic.py` 编号顺序。
- `python/interview_exercises/` 包含按主题归类、可复用的练习实现。
- `python/backend_interview/` 保持路由、Schema、服务、仓储、领域对象和网关之间的边界。
- `python/tests/` 对应课程和练习；`python/tests/backend/` 覆盖 FastAPI 示例。

在 `python/` 目录使用：

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

目标版本为 Python 3.11 或更高。使用四空格缩进、类型注解、简洁文档字符串和 100 字符行宽。
Ruff 启用 `E`、`F`、`I`、`B`、`UP` 和 `SIM`。模块、函数、fixture 和变量使用
`snake_case`，类使用 `PascalCase`，常量使用 `UPPER_SNAKE_CASE`。优先显式依赖注入，
避免让 FastAPI 类型进入领域层和服务层。

测试使用 pytest、pytest-asyncio、Hypothesis，并包含少数 unittest 风格示例。测试文件命名为
`test_<subject>.py`，测试函数命名为 `test_<behavior>()`。行为变更应覆盖正常、边界和失败场景；
适合表达普遍不变量时使用属性测试。

## 教程站点

- `website/docs/tutorials/` 保存中文概念教程，每篇应对应 `python/` 中的真实源码。
- `website/docs/.vitepress/components/` 只放有明确教学价值的 Vue 可视化。
- `website/docs/.vitepress/config.mjs` 和 `website/docs/index.md` 必须与教程目录同步。

在 `website/` 目录使用：

```bash
npm install
npm run docs:dev
npm run docs:build
npm run docs:preview
```

教程保持标准文档阅读流：概念说明、短代码、必要的图解、常见误区和面试表述。不要加入营销首页、
演示式大屏、无教学价值的动画或重复卡片。Plotly 依赖必须本地打包，不使用 CDN。

## 架构文档

如果变更影响两个工程的目录边界、运行命令、公共入口、路由、配置、认证、存储、请求流或模块职责，
同步更新 `docs/architecture/index.md`，并在 `docs/architecture/change-log.md` 追加记录。
如果检查后无需更新，最终回复中明确说明。

## Commit 与 Pull Request

遵循 Conventional Commits，例如 `feat: add generator exercises`、`docs: clarify asyncio
cancellation`、`refactor: separate python and docs projects`。每个 commit 保持聚焦。Pull Request
说明学习内容或运行时行为的变化并列出验证命令；教程页面发生明显视觉变化时附截图。
不要提交 `.venv`、`node_modules`、构建目录、覆盖率产物、缓存或 `.env` 中的敏感信息。
