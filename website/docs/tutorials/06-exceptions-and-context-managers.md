# Python 异常与上下文管理器

异常用于表示程序在运行期间无法正常完成某项操作。上下文管理器则负责资源的获取和释放，确保文件、
锁、连接和事务在正常结束或异常结束时都能正确清理。

这一章从异常的产生和捕获开始，再介绍主动抛出、自定义异常、文件管理、`contextlib` 和
`ExceptionGroup`。

<p class="source-note">对应源码：<code>python/python_interview_practice/06_exceptions_context.py</code></p>

## 本章内容

- [异常基础：传播、捕获与清理](./06-exceptions-and-context-managers/exception-basics)：
  理解异常如何沿调用栈传播，以及 `try`、`except`、`else`、`finally` 分别何时执行。
- [主动抛出与自定义异常](./06-exceptions-and-context-managers/raising-and-custom-exceptions)：
  为参数和业务规则选择异常类型，并在跨层转换异常时保留原因。
- [assert、LBYL 与 EAFP](./06-exceptions-and-context-managers/assertions-and-eafp)：
  区分内部不变量、外部输入校验和两种常见错误处理风格。
- [文件与上下文管理器](./06-exceptions-and-context-managers/files-and-context-managers)：
  使用 `with`、`pathlib` 和类形式的上下文管理器可靠释放资源。
- [contextlib 与高级异常](./06-exceptions-and-context-managers/contextlib-and-advanced-exceptions)：
  使用 `@contextmanager`、`suppress()`、`ExitStack` 和 `ExceptionGroup` 处理更复杂的资源与失败。
