---
title: Python 概念教程
outline: false
aside: false
prev: false
next: false
---

# Python 概念教程

从语言心智模型一路读到并发与后端项目。每篇教程都对应仓库中的可运行 Python 示例。

<div class="tutorial-index">
  <div class="index-group-label">Python 核心</div>
  <a href="/tutorials/01-basic-types-and-truthiness">
    <span class="index-number">01</span>
    <span><strong>基础类型、比较与真值</strong><small>区分值、类型、对象身份和条件判断。</small></span>
  </a>
  <a href="/tutorials/02-mutability-and-copy">
    <span class="index-number">02</span>
    <span><strong>可变对象、引用与拷贝</strong><small>看清变量名、容器和嵌套对象之间的引用关系。</small></span>
  </a>
  <a href="/tutorials/03-functions-and-generators">
    <span class="index-number">03</span>
    <span><strong>函数、闭包与生成器</strong><small>理解函数对象、闭包状态，以及生成器为何能暂停和恢复。</small></span>
  </a>
  <a href="/tutorials/04-containers-and-sorting">
    <span class="index-number">04</span>
    <span><strong>容器、推导式与排序</strong><small>根据数据约束选择容器，并理解排序与去重。</small></span>
  </a>
  <a href="/tutorials/05-oop-and-data-model">
    <span class="index-number">05</span>
    <span><strong>面向对象与数据模型</strong><small>串起属性查找、描述符、MRO 和特殊方法。</small></span>
  </a>
  <a href="/tutorials/06-exceptions-and-context-managers">
    <span class="index-number">06</span>
    <span><strong>异常与上下文管理器</strong><small>把失败传播与资源生命周期放在正确边界。</small></span>
  </a>
  <a href="/tutorials/07-typing-and-protocols">
    <span class="index-number">07</span>
    <span><strong>类型标注、泛型与 Protocol</strong><small>区分静态契约和运行时校验，表达接口能力。</small></span>
  </a>
  <a href="/tutorials/08-standard-library-patterns">
    <span class="index-number">08</span>
    <span><strong>常用标准库模式</strong><small>识别计数、惰性流水线、Top-K 和有序边界。</small></span>
  </a>

  <div class="index-group-label">算法、性能与测试</div>
  <a href="/tutorials/09-algorithms-and-complexity">
    <span class="index-number">09</span>
    <span><strong>算法正确性与复杂度</strong><small>从不变量解释正确性，并直观看见 O(n) 与 O(n²) 的差距。</small></span>
  </a>
  <a href="/tutorials/10-performance-and-memory">
    <span class="index-number">10</span>
    <span><strong>性能分析与内存模型</strong><small>用基准、profiler 和快照建立证据链。</small></span>
  </a>
  <a href="/tutorials/11-testing-and-mocking">
    <span class="index-number">11</span>
    <span><strong>测试、依赖注入与 Mock</strong><small>验证行为契约，正确选择 Fake、Mock 和 patch。</small></span>
  </a>

  <div class="index-group-label">并发模型</div>
  <a href="/tutorials/12-threads-and-synchronization">
    <span class="index-number">12</span>
    <span><strong>线程、线程池与同步</strong><small>理解 Future、竞态、Lock 和 I/O 并发边界。</small></span>
  </a>
  <a href="/tutorials/13-asyncio-task-timeline">
    <span class="index-number">13</span>
    <span><strong>asyncio 任务时间线</strong><small>区分协程、Task、并发等待、结果顺序与取消传播。</small></span>
  </a>

  <div class="index-group-label">后端工程</div>
  <a href="/tutorials/14-fastapi-layered-backend">
    <span class="index-number">14</span>
    <span><strong>FastAPI 分层后端</strong><small>跟踪订单请求如何穿过 HTTP、服务、领域和仓储边界。</small></span>
  </a>
  <a href="/tutorials/15-pydantic-v2-data-boundaries">
    <span class="index-number">15</span>
    <span><strong>Pydantic v2 与数据边界</strong><small>系统理解解析、验证、判别联合、序列化与配置。</small></span>
  </a>
  <a href="/tutorials/16-async-reliability-patterns">
    <span class="index-number">16</span>
    <span><strong>异步可靠性模式</strong><small>组合超时、重试、并发限制、背压和 single-flight。</small></span>
  </a>
</div>
