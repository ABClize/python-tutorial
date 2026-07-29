# 教程站点

这是仓库的 VitePress 文档工程。Markdown 负责教程正文，Vue 组件只用于对象图、执行状态和定量曲线
等确实需要交互的概念。

## 目录

```text
website/
├── docs/
│   ├── tutorials/                 # 16 篇中文概念教程
│   ├── .vitepress/components/     # Vue/Plotly 可视化
│   ├── .vitepress/theme/          # 文档主题和少量样式
│   └── index.md                   # 教程目录
├── package.json
└── package-lock.json
```

## 命令

```bash
npm install
npm run docs:dev
npm run docs:build
npm run docs:preview
```

新增教程时，需要同步更新：

1. `docs/tutorials/` 中的 Markdown；
2. `docs/.vitepress/config.mjs` 中的侧栏；
3. `docs/index.md` 中的首页目录。

教程正文优先使用中文，代码标识符和库名保留原文。每篇内容应对应 `python/` 中的真实示例，
不要添加无法从源码验证的项目行为。
