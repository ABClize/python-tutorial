# 架构变更记录

## 2026-07-31：纠正乐观锁请求头语义

- 订单状态更新接口用 `X-Expected-Version` 传递整数版本号，不再把标准 `If-Match` 当作普通整数头。
- 保留版本不匹配返回 HTTP 409 的业务冲突语义，并同步 API 测试、后端说明和教程。

## 2026-07-30：项目更名并接入 GitHub Pages

- 仓库由 `python-interview-learning` 更名为 `python-tutorial`，站点默认地址调整为
  `https://abclize.github.io/python-tutorial/`。
- 增加 GitHub Pages 工作流，从 `master` 分支构建并部署 `website/`。
- VitePress 部署前缀由 GitHub Pages 元数据经 `VITEPRESS_BASE` 注入，本地开发仍使用根路径
  `/`。
- favicon、代码字体样式和预加载字体改为跟随部署前缀，避免项目站点子路径下资源 404。

## 2026-07-30：教程站点支持深色主题与本地代码字体

- 启用 VitePress 深浅主题切换，并让 Plotly 可视化跟随主题重新着色。
- 优化手机端导航、代码块、表格和交互式可视化的响应式布局。
- 将 Maple Mono CN 拆分为按 `unicode-range` 加载的本地 WOFF2 静态资源，不依赖访客设备字体
  或外部 CDN。
- 字体来源、版本、校验值和 SIL Open Font License 记录在字体资源目录中。

## 2026-07-30：教程改为章目录与子教程

- 保留 16 个编号教程入口作为章目录，为每章增加围绕单个概念簇编写的子教程。
- VitePress 左侧侧栏改为可折叠的“章 → 子教程”结构，右侧继续显示当前文章大纲。
- 教程定位调整为面向初学者的纯概念教程，不再组织面试问答。
- 可视化继续嵌入相关概念页面，只用于引用关系、执行过程、调度和定量变化等抽象内容。

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
