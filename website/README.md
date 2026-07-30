# 教程站点

这是仓库的 VitePress 文档工程。Markdown 负责教程正文，Vue 组件只用于对象图、执行状态和定量曲线
等确实需要交互的概念。

## 目录

```text
website/
├── docs/
│   ├── tutorials/                 # 16 个章目录与 84 篇中文子教程
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

本地开发使用根路径 `/`。GitHub Actions 构建时从 GitHub Pages 元数据取得站点路径，通过
`VITEPRESS_BASE` 传给 VitePress，并将 `docs/.vitepress/dist` 发布到 GitHub Pages。

教程采用两级结构：`docs/tutorials/NN-topic.md` 是章目录和稳定入口，同名目录中的 Markdown
负责讲解各个概念簇。

新增或调整教程时，需要同步更新：

1. 章目录中的子教程列表；
2. `docs/.vitepress/config.mjs` 中的侧栏；
3. 新增或重命名章节时，更新 `docs/index.md` 中的首页目录。

教程正文优先使用中文，代码标识符和库名保留原文。每篇内容应对应 `python/` 中的真实示例，
不要添加无法从源码验证的项目行为。
