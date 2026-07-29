# Python 面试练习测试

这里组合使用 `unittest`、pytest、pytest-asyncio 和 Hypothesis 检验：

- `python_interview_practice/08_algorithms.py`
- `python_interview_practice/09_practice_questions.py`
- `interview_exercises/` 中的算法、容器、面向对象和异步代码
- `backend_interview/` 中的 FastAPI、Pydantic v2、服务层和 asyncio 场景

由于源文件以数字开头，不能写普通的
`import python_interview_practice.08_algorithms`。测试通过
`importlib.util.spec_from_file_location()` 按文件路径加载模块。

## 运行

在仓库根目录执行全部测试：

```bash
uv run pytest -v
```

单独运行某个测试文件：

```bash
uv run pytest tests/test_algorithms.py -v
uv run pytest tests/test_practice_questions.py -v
uv run pytest tests/test_properties.py -v
uv run pytest tests/backend -v
```

## 阅读建议

测试覆盖三类场景：

1. 正常输入：验证典型面试示例的结果。
2. 边界输入：如空序列、重复值、Unicode、只有一个元素。
3. 失败输入：如找不到答案、括号不匹配，或传入明显错误的类型。

可以先遮住实现，只看测试名称和断言，自己实现函数后再运行测试。
失败信息中的 `expected` 是期望值，`actual` 是函数实际返回值。

`test_properties.py` 不只测试手写的几个样例，而是用 Hypothesis 自动生成大量输入，
验证“合并结果一定有序”“编码后再解码一定回到原字符串”等普遍性质。这能发现人工
样例容易遗漏的边界情况。

`tests/backend/` 同时展示四个测试层次：Pydantic 模型测试、服务层异步测试、
FastAPI `TestClient` 请求测试，以及 `HTTPX + ASGITransport` 的全异步请求测试。
依赖覆盖、幂等并发、乐观锁、超时取消和资源清理也都有独立样例。

这些测试依据当前函数文档所表达的契约编写。例如二分查找假定输入
已经按升序排列，斐波那契函数的有效业务输入假定为非负整数；测试
不会把契约之外的输入结果当成正式功能。
