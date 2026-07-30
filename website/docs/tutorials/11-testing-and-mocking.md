# Python 测试、pytest 与 Mock

自动化测试是可以重复运行的检查代码。它会调用程序，再核对返回值、异常、外部调用和资源清理结果。
程序修改后，重新运行测试就能发现原有行为是否被破坏。

<p class="source-note">对应源码：<code>python/python_interview_practice/14_testing_and_mocking.py</code>、<code>python/tests/</code></p>

## 本章内容

- [pytest 基础](./11-testing-and-mocking/pytest-basics)：安装并运行 pytest，理解测试发现、测试结构和
  `assert` 失败信息。
- [异常、参数化与 fixture](./11-testing-and-mocking/exceptions-parameters-and-fixtures)：验证异常，
  用多组数据复用同一规则，并管理测试准备与清理。
- [测试隔离与依赖注入](./11-testing-and-mocking/isolation-and-dependency-injection)：消除测试顺序、
  全局状态和真实外部系统带来的影响。
- [测试替身与 Mock](./11-testing-and-mocking/test-doubles-and-mock)：区分 Fake、Stub、Mock 和 Spy，
  验证结账服务的返回结果与外部调用。
- [patch、side_effect 与 monkeypatch](./11-testing-and-mocking/patch-side-effect-and-monkeypatch)：
  替换正确的名字，并模拟异常、连续结果、环境变量和动态行为。
- [异步测试与 unittest](./11-testing-and-mocking/async-and-unittest)：测试协程和异步依赖，理解 pytest
  与标准库 unittest 如何共存。
- [测试层次与项目实践](./11-testing-and-mocking/testing-strategy)：组合单元、API、属性和覆盖率工具，
  识别不稳定测试，并使用仓库中的测试命令。
