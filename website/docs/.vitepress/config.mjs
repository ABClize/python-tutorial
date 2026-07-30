import { defineConfig } from "vitepress";

const tutorialSections = [
  {
    text: "Python 核心",
    items: [
      {
        text: "01 变量、基本类型与控制语句",
        link: "/tutorials/01-basic-types-and-truthiness",
        collapsed: true,
        items: [
          {
            text: "变量、类型与类型转换",
            link: "/tutorials/01-basic-types-and-truthiness/variables-and-types",
          },
          {
            text: "数值与运算符",
            link: "/tutorials/01-basic-types-and-truthiness/numbers-and-operators",
          },
          {
            text: "条件语句与循环",
            link: "/tutorials/01-basic-types-and-truthiness/conditions-and-loops",
          },
          {
            text: "字符串",
            link: "/tutorials/01-basic-types-and-truthiness/strings",
          },
          {
            text: "真值、相等与对象身份",
            link: "/tutorials/01-basic-types-and-truthiness/truthiness-and-identity",
          },
        ],
      },
      {
        text: "02 可变对象、引用与拷贝",
        link: "/tutorials/02-mutability-and-copy",
        collapsed: true,
        items: [
          {
            text: "引用与可变性",
            link: "/tutorials/02-mutability-and-copy/references-and-mutability",
          },
          {
            text: "浅拷贝与深拷贝",
            link: "/tutorials/02-mutability-and-copy/shallow-and-deep-copy",
          },
          {
            text: "函数参数与默认值",
            link: "/tutorials/02-mutability-and-copy/function-arguments-and-defaults",
          },
          {
            text: "哈希与复制策略",
            link: "/tutorials/02-mutability-and-copy/hashing-and-copy-strategy",
          },
        ],
      },
      {
        text: "03 函数、作用域与生成器",
        link: "/tutorials/03-functions-and-generators",
        collapsed: true,
        items: [
          {
            text: "函数基础",
            link: "/tutorials/03-functions-and-generators/function-basics",
          },
          {
            text: "作用域与函数对象",
            link: "/tutorials/03-functions-and-generators/scope-and-function-objects",
          },
          {
            text: "闭包、装饰器与递归",
            link: "/tutorials/03-functions-and-generators/closures-decorators-recursion",
          },
          {
            text: "可迭代对象与迭代器",
            link: "/tutorials/03-functions-and-generators/iterables-and-iterators",
          },
          {
            text: "生成器与 itertools",
            link: "/tutorials/03-functions-and-generators/generators-and-itertools",
          },
        ],
      },
      {
        text: "04 容器、推导式与排序",
        link: "/tutorials/04-containers-and-sorting",
        collapsed: true,
        items: [
          {
            text: "列表、元组与解包",
            link: "/tutorials/04-containers-and-sorting/lists-tuples-unpacking",
          },
          {
            text: "字典",
            link: "/tutorials/04-containers-and-sorting/dictionaries",
          },
          {
            text: "集合与推导式",
            link: "/tutorials/04-containers-and-sorting/sets-and-comprehensions",
          },
          {
            text: "排序与去重",
            link: "/tutorials/04-containers-and-sorting/sorting-and-deduplication",
          },
          {
            text: "collections 与复杂度",
            link: "/tutorials/04-containers-and-sorting/collections-and-complexity",
          },
        ],
      },
      {
        text: "05 面向对象与数据模型",
        link: "/tutorials/05-oop-and-data-model",
        collapsed: true,
        items: [
          {
            text: "类、实例与方法",
            link: "/tutorials/05-oop-and-data-model/classes-instances-methods",
          },
          {
            text: "封装、property 与组合",
            link: "/tutorials/05-oop-and-data-model/encapsulation-properties-composition",
          },
          {
            text: "继承、MRO 与抽象基类",
            link: "/tutorials/05-oop-and-data-model/inheritance-mro-abc",
          },
          {
            text: "dataclass 与特殊方法",
            link: "/tutorials/05-oop-and-data-model/dataclasses-and-special-methods",
          },
          {
            text: "描述符、属性查找与 slots",
            link: "/tutorials/05-oop-and-data-model/descriptors-attribute-lookup-slots",
          },
        ],
      },
      {
        text: "06 异常与上下文管理器",
        link: "/tutorials/06-exceptions-and-context-managers",
        collapsed: true,
        items: [
          {
            text: "异常基础",
            link: "/tutorials/06-exceptions-and-context-managers/exception-basics",
          },
          {
            text: "抛出与自定义异常",
            link: "/tutorials/06-exceptions-and-context-managers/raising-and-custom-exceptions",
          },
          {
            text: "assert、LBYL 与 EAFP",
            link: "/tutorials/06-exceptions-and-context-managers/assertions-and-eafp",
          },
          {
            text: "文件与上下文管理器",
            link: "/tutorials/06-exceptions-and-context-managers/files-and-context-managers",
          },
          {
            text: "contextlib 与高级异常",
            link: "/tutorials/06-exceptions-and-context-managers/contextlib-and-advanced-exceptions",
          },
        ],
      },
      {
        text: "07 类型标注、泛型与 Protocol",
        link: "/tutorials/07-typing-and-protocols",
        collapsed: true,
        items: [
          {
            text: "类型标注基础",
            link: "/tutorials/07-typing-and-protocols/typing-basics",
          },
          {
            text: "Enum、Literal 与 TypedDict",
            link: "/tutorials/07-typing-and-protocols/literal-and-typeddict",
          },
          {
            text: "泛型",
            link: "/tutorials/07-typing-and-protocols/generics",
          },
          {
            text: "Protocol 与 Callable",
            link: "/tutorials/07-typing-and-protocols/protocols-and-callables",
          },
          {
            text: "高级类型工具",
            link: "/tutorials/07-typing-and-protocols/advanced-typing",
          },
        ],
      },
      {
        text: "08 常用标准库",
        link: "/tutorials/08-standard-library-patterns",
        collapsed: true,
        items: [
          {
            text: "模块、命令行参数与 uv",
            link: "/tutorials/08-standard-library-patterns/modules-and-imports",
          },
          {
            text: "pathlib、JSON 与 CSV 文件",
            link: "/tutorials/08-standard-library-patterns/paths-and-json",
          },
          {
            text: "collections 工具",
            link: "/tutorials/08-standard-library-patterns/collections-tools",
          },
          {
            text: "日期、时间与时区",
            link: "/tutorials/08-standard-library-patterns/datetime",
          },
          {
            text: "Decimal 与数值工具",
            link: "/tutorials/08-standard-library-patterns/decimal",
          },
          {
            text: "itertools 惰性迭代",
            link: "/tutorials/08-standard-library-patterns/itertools",
          },
          {
            text: "heapq 与 bisect",
            link: "/tutorials/08-standard-library-patterns/heapq-and-bisect",
          },
          {
            text: "functools 函数工具",
            link: "/tutorials/08-standard-library-patterns/functools",
          },
          {
            text: "tempfile、logging 与工具选择",
            link: "/tutorials/08-standard-library-patterns/tempfile-and-guide",
          },
        ],
      },
    ],
  },
  {
    text: "算法、性能与测试",
    items: [
      {
        text: "09 算法与复杂度",
        link: "/tutorials/09-algorithms-and-complexity",
        collapsed: true,
        items: [
          {
            text: "复杂度基础",
            link: "/tutorials/09-algorithms-and-complexity/complexity-basics",
          },
          {
            text: "正确性与查找",
            link: "/tutorials/09-algorithms-and-complexity/correctness-and-search",
          },
          {
            text: "栈、队列与广度优先搜索",
            link: "/tutorials/09-algorithms-and-complexity/stacks-queues-and-bfs",
          },
          {
            text: "动态规划与序列处理",
            link: "/tutorials/09-algorithms-and-complexity/dynamic-programming-and-sequences",
          },
          {
            text: "边界验证与实际测量",
            link: "/tutorials/09-algorithms-and-complexity/testing-and-measurement",
          },
        ],
      },
      {
        text: "10 性能分析与内存管理",
        link: "/tutorials/10-performance-and-memory",
        collapsed: true,
        items: [
          {
            text: "性能指标与 timeit",
            link: "/tutorials/10-performance-and-memory/measurement-and-timeit",
          },
          {
            text: "使用 cProfile 定位热点",
            link: "/tutorials/10-performance-and-memory/profiling-with-cprofile",
          },
          {
            text: "测量内存分配",
            link: "/tutorials/10-performance-and-memory/measuring-memory",
          },
          {
            text: "迭代器、回收与 RSS",
            link: "/tutorials/10-performance-and-memory/iterators-gc-and-rss",
          },
          {
            text: "泄漏、缓存与优化顺序",
            link: "/tutorials/10-performance-and-memory/leaks-caches-and-optimization",
          },
        ],
      },
      {
        text: "11 Python 自动化测试",
        link: "/tutorials/11-testing-and-mocking",
        collapsed: true,
        items: [
          {
            text: "pytest 基础",
            link: "/tutorials/11-testing-and-mocking/pytest-basics",
          },
          {
            text: "异常、参数化与 fixture",
            link: "/tutorials/11-testing-and-mocking/exceptions-parameters-and-fixtures",
          },
          {
            text: "隔离与依赖注入",
            link: "/tutorials/11-testing-and-mocking/isolation-and-dependency-injection",
          },
          {
            text: "测试替身与 Mock",
            link: "/tutorials/11-testing-and-mocking/test-doubles-and-mock",
          },
          {
            text: "patch、side_effect 与 monkeypatch",
            link: "/tutorials/11-testing-and-mocking/patch-side-effect-and-monkeypatch",
          },
          {
            text: "异步测试与 unittest",
            link: "/tutorials/11-testing-and-mocking/async-and-unittest",
          },
          {
            text: "测试策略与覆盖率",
            link: "/tutorials/11-testing-and-mocking/testing-strategy",
          },
        ],
      },
    ],
  },
  {
    text: "并发模型",
    items: [
      {
        text: "12 线程、线程池、进程池与同步",
        link: "/tutorials/12-threads-and-synchronization",
        collapsed: true,
        items: [
          {
            text: "线程、线程池与进程池",
            link: "/tutorials/12-threads-and-synchronization/thread-basics-and-pools",
          },
          {
            text: "共享状态与锁",
            link: "/tutorials/12-threads-and-synchronization/shared-state-and-locks",
          },
          {
            text: "队列与同步工具",
            link: "/tutorials/12-threads-and-synchronization/queues-and-synchronization",
          },
          {
            text: "死锁、GIL 与使用边界",
            link: "/tutorials/12-threads-and-synchronization/deadlocks-gil-and-guidelines",
          },
        ],
      },
      {
        text: "13 asyncio 协程与任务",
        link: "/tutorials/13-asyncio-task-timeline",
        collapsed: true,
        items: [
          {
            text: "协程、Task 与事件循环",
            link: "/tutorials/13-asyncio-task-timeline/coroutines-tasks-and-loop",
          },
          {
            text: "await 与并发执行",
            link: "/tutorials/13-asyncio-task-timeline/await-and-concurrency",
          },
          {
            text: "任务时间线与结构化并发",
            link: "/tutorials/13-asyncio-task-timeline/task-timeline-gather-and-taskgroup",
          },
          {
            text: "超时与取消",
            link: "/tutorials/13-asyncio-task-timeline/timeouts-and-cancellation",
          },
          {
            text: "并发限制与异步资源",
            link: "/tutorials/13-asyncio-task-timeline/limits-queues-and-async-resources",
          },
        ],
      },
    ],
  },
  {
    text: "后端工程",
    items: [
      {
        text: "14 FastAPI 分层后端",
        link: "/tutorials/14-fastapi-layered-backend",
        collapsed: true,
        items: [
          {
            text: "运行、路由与请求数据",
            link: "/tutorials/14-fastapi-layered-backend/running-routes-and-requests",
          },
          {
            text: "依赖注入与应用生命周期",
            link: "/tutorials/14-fastapi-layered-backend/dependencies-and-lifecycle",
          },
          {
            text: "请求流与分层职责",
            link: "/tutorials/14-fastapi-layered-backend/request-flow-and-layers",
          },
          {
            text: "持久化、幂等与并发控制",
            link: "/tutorials/14-fastapi-layered-backend/persistence-idempotency-and-locking",
          },
          {
            text: "异常、批量接口与 OpenAPI",
            link: "/tutorials/14-fastapi-layered-backend/errors-batch-and-openapi",
          },
        ],
      },
      {
        text: "15 Pydantic v2 数据边界",
        link: "/tutorials/15-pydantic-v2-data-boundaries",
        collapsed: true,
        items: [
          {
            text: "模型、错误与字段约束",
            link: "/tutorials/15-pydantic-v2-data-boundaries/models-errors-and-fields",
          },
          {
            text: "规范化、配置与严格模式",
            link: "/tutorials/15-pydantic-v2-data-boundaries/normalization-config-and-strict-mode",
          },
          {
            text: "验证器与默认值",
            link: "/tutorials/15-pydantic-v2-data-boundaries/validators-and-defaults",
          },
          {
            text: "联合类型、适配器与对象输入",
            link: "/tutorials/15-pydantic-v2-data-boundaries/unions-adapters-and-object-input",
          },
          {
            text: "序列化、配置读取与领域模型",
            link: "/tutorials/15-pydantic-v2-data-boundaries/serialization-settings-and-domain-models",
          },
        ],
      },
      {
        text: "16 异步可靠性模式",
        link: "/tutorials/16-async-reliability-patterns",
        collapsed: true,
        items: [
          {
            text: "超时与截止时间",
            link: "/tutorials/16-async-reliability-patterns/timeouts-and-deadlines",
          },
          {
            text: "重试、退避与幂等",
            link: "/tutorials/16-async-reliability-patterns/retries-backoff-and-idempotency",
          },
          {
            text: "并发限制与背压",
            link: "/tutorials/16-async-reliability-patterns/concurrency-limits-and-backpressure",
          },
          {
            text: "single-flight 与任务组",
            link: "/tutorials/16-async-reliability-patterns/single-flight-and-task-groups",
          },
          {
            text: "取消、隔离与可观测性",
            link: "/tutorials/16-async-reliability-patterns/cancellation-isolation-and-observability",
          },
        ],
      },
    ],
  },
];

export default defineConfig({
  lang: "zh-CN",
  title: "Python 概念教程",
  description: "从基础语法到并发与后端工程，逐步讲清 Python 的常用概念。",
  cleanUrls: true,
  appearance: false,
  head: [["link", { rel: "icon", href: "/favicon.svg", type: "image/svg+xml" }]],
  themeConfig: {
    sidebar: [
      {
        text: "教程目录",
        items: [{ text: "首页", link: "/" }],
      },
      ...tutorialSections,
    ],
    outline: {
      level: [2, 3],
      label: "文章大纲",
    },
    docFooter: {
      prev: "上一篇",
      next: "下一篇",
    },
    sidebarMenuLabel: "教程目录",
    returnToTopLabel: "返回顶部",
  },
});
