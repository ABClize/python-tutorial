# Python 异常与上下文管理器

异常表示程序在运行时发生了错误。例如，字符串不能转成整数、文件不存在、列表索引超出范围，都会
产生异常。程序可以捕获异常并给出处理办法，也可以让异常继续向上报告。

上下文管理器用于管理需要关闭或释放的资源。最常见的写法是 `with`。代码块结束时，文件、锁、连接
或事务会执行清理操作，即使代码块中途发生异常也一样。

本章先讲异常的产生、捕获和抛出，再讲文件管理、`contextlib` 和 `ExceptionGroup`。

<p class="source-note">对应源码：<code>python/python_interview_practice/06_exceptions_context.py</code></p>

## 本章内容

- [异常基础：传播、捕获与清理](./06-exceptions-and-context-managers/exception-basics)：
  学习异常如何沿调用栈传播，以及 `try`、`except`、`else`、`finally` 分别何时执行。
- [主动抛出与自定义异常](./06-exceptions-and-context-managers/raising-and-custom-exceptions)：
  使用 `raise` 报告错误，定义自己的异常类型，并保留底层错误原因。
- [assert、LBYL 与 EAFP](./06-exceptions-and-context-managers/assertions-and-eafp)：
  分清 `assert`、操作前检查和捕获异常各自适合的情况。
- [文件与上下文管理器](./06-exceptions-and-context-managers/files-and-context-managers)：
  使用 `with`、`pathlib` 和自定义上下文管理器关闭文件、释放资源。
- [contextlib 与高级异常](./06-exceptions-and-context-managers/contextlib-and-advanced-exceptions)：
  使用 `@contextmanager`、`suppress()`、`ExitStack` 和 `ExceptionGroup`。
