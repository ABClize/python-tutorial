import { defineConfig } from "vitepress";

const coreTutorials = [
  {
    text: "01 基础类型、比较与真值",
    link: "/tutorials/01-basic-types-and-truthiness",
  },
  {
    text: "02 可变对象、引用与拷贝",
    link: "/tutorials/02-mutability-and-copy",
  },
  {
    text: "03 函数、闭包与生成器",
    link: "/tutorials/03-functions-and-generators",
  },
  {
    text: "04 容器、推导式与排序",
    link: "/tutorials/04-containers-and-sorting",
  },
  {
    text: "05 面向对象与数据模型",
    link: "/tutorials/05-oop-and-data-model",
  },
  {
    text: "06 异常与上下文管理器",
    link: "/tutorials/06-exceptions-and-context-managers",
  },
  {
    text: "07 类型标注、泛型与 Protocol",
    link: "/tutorials/07-typing-and-protocols",
  },
  {
    text: "08 常用标准库模式",
    link: "/tutorials/08-standard-library-patterns",
  },
];

const engineeringTutorials = [
  {
    text: "09 算法正确性与复杂度",
    link: "/tutorials/09-algorithms-and-complexity",
  },
  {
    text: "10 性能分析与内存模型",
    link: "/tutorials/10-performance-and-memory",
  },
  {
    text: "11 测试、依赖注入与 Mock",
    link: "/tutorials/11-testing-and-mocking",
  },
];

const concurrencyTutorials = [
  {
    text: "12 线程、线程池与同步",
    link: "/tutorials/12-threads-and-synchronization",
  },
  {
    text: "13 asyncio 任务时间线",
    link: "/tutorials/13-asyncio-task-timeline",
  },
];

const projectTutorials = [
  {
    text: "14 FastAPI 分层后端",
    link: "/tutorials/14-fastapi-layered-backend",
  },
  {
    text: "15 Pydantic v2 与数据边界",
    link: "/tutorials/15-pydantic-v2-data-boundaries",
  },
  {
    text: "16 异步可靠性模式",
    link: "/tutorials/16-async-reliability-patterns",
  },
];

export default defineConfig({
  lang: "zh-CN",
  title: "Python 概念教程",
  description: "通过可操作的图形理解 Python 对象、执行状态、复杂度与异步调度。",
  cleanUrls: true,
  appearance: false,
  head: [["link", { rel: "icon", href: "/favicon.svg", type: "image/svg+xml" }]],
  themeConfig: {
    nav: [{ text: "教程目录", link: "/" }],
    sidebar: [
      {
        text: "教程目录",
        items: [{ text: "首页", link: "/" }],
      },
      {
        text: "Python 核心",
        items: coreTutorials,
      },
      {
        text: "算法、性能与测试",
        items: engineeringTutorials,
      },
      {
        text: "并发模型",
        items: concurrencyTutorials,
      },
      {
        text: "后端工程",
        items: projectTutorials,
      },
    ],
    outline: {
      level: [2, 3],
      label: "本页目录",
    },
    docFooter: {
      prev: "上一篇",
      next: "下一篇",
    },
    sidebarMenuLabel: "教程目录",
    returnToTopLabel: "返回顶部",
  },
});
