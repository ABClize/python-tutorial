# 仓库架构

## 总体边界

仓库包含两个可独立安装、运行和验证的工程：

```text
python-tutorial/
├── python/       # Python 学习运行时
├── website/      # VitePress 教程站点
└── docs/         # 仓库级长期架构说明
```

`python/` 是教程的事实来源，`website/` 是概念解释和可视化入口。站点可以引用 Python 源码路径，
Python 工程不依赖前端构建产物，因此删除或重新构建站点不会影响示例与测试运行。

## Python 工程

```text
python/
├── python_interview_practice/  # 15 个可直接运行的编号课程
├── interview_exercises/        # 可复用练习实现
├── backend_interview/          # 分层 FastAPI 示例
├── tests/                      # Python 与后端测试
├── run_all.py                  # 课程批量入口
├── pyproject.toml
└── uv.lock
```

依赖和工具由 `uv` 管理。执行命令的工作目录是 `python/`，包导入根也是该目录。

## 教程站点

```text
website/
├── docs/
│   ├── tutorials/              # 章目录 Markdown 与同名子教程目录
│   ├── .vitepress/components/  # Vue 与 Plotly 可视化
│   ├── .vitepress/theme/       # 文档主题
│   ├── public/fonts/            # 本地托管的网页字体与授权文件
│   └── index.md                # 教程目录
├── package.json
└── package-lock.json
```

站点由 VitePress 构建。Markdown 负责稳定正文，Vue 组件只承载需要交互状态或定量曲线的概念。
Plotly 随 npm 构建本地打包，代码字体以 WOFF2 分片随静态站点发布，二者都不依赖运行时 CDN。

教程采用两级内容结构：`tutorials/NN-topic.md` 是章目录和稳定入口，
`tutorials/NN-topic/*.md` 是围绕单个概念簇编写的子教程。VitePress 左侧导航按章折叠这些子教程，
右侧导航只展示当前文章的标题大纲。

## 部署

教程站点通过 `.github/workflows/deploy-pages.yml` 发布到 GitHub Pages。工作流只构建
`website/`，从 `actions/configure-pages` 取得当前站点路径，通过 `VITEPRESS_BASE` 传给
VitePress，然后上传 `website/docs/.vitepress/dist`。本地开发不设置该变量，继续使用根路径
`/`。

站点默认地址为 <https://abclize.github.io/python-tutorial/>。仓库再次重命名或改用自定义域名时，
部署前缀会跟随 GitHub Pages 元数据变化，不需要再修改 VitePress 配置。

## 跨工程契约

- 教程中的“对应源码”路径必须指向 `python/` 中存在的文件。
- Python 主题新增或职责明显变化时，检查对应教程是否需要更新。
- 教程章节新增、删除或重命名时，同步更新 VitePress 侧栏与首页目录；章内子教程变化时同步更新章目录
  与侧栏。
- 根目录 VS Code 配置通过不同 `cwd` 分别调用两个工程，不要求根目录存在包管理配置。
