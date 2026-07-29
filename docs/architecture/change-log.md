# 架构变更记录

## 2026-07-29：拆分 Python 工程与教程站点

- 将 Python 包、测试、运行入口、`pyproject.toml` 和 `uv.lock` 统一移动到 `python/`。
- 将 VitePress、Markdown、Vue 组件、`package.json` 和锁文件统一移动到 `website/`。
- 根目录仅保留仓库级说明、架构文档和编辑器工作区配置。
- 教程从 4 篇扩展为 16 篇，覆盖 15 个编号 Python 课程、FastAPI、Pydantic v2 与异步可靠性模式。
- 更新 VS Code 的 Python 解释器、pytest、调试和任务工作目录。

## 2026-07-29：深化概念教程

- 扩充 14 篇既有教程的运行机制、边界条件、工程取舍和常见追问。
- 新增 Pydantic v2 数据边界教程，覆盖验证顺序、判别联合、序列化和 BaseSettings。
- 新增异步可靠性教程，覆盖 deadline、重试、背压、single-flight、熔断边界与可观测性。
