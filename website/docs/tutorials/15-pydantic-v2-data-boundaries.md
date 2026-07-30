# Pydantic v2 数据边界

Pydantic 是 Python 的数据校验库。它根据类型标注读取字典、JSON、环境变量或普通对象，把合法输入
转换成模型，并为错误输入生成结构化错误。模型输出时，还可以控制字段和序列化格式。

<p class="source-note">对应源码：<code>python/backend_interview/schemas.py</code>、<code>python/backend_interview/pydantic_patterns.py</code>、<code>python/backend_interview/config.py</code></p>

## 本章内容

- [模型、校验错误与字段约束](./15-pydantic-v2-data-boundaries/models-errors-and-fields)：
  定义 `BaseModel`，读取错误位置，并限制数值、字符串和嵌套字段。
- [输入规范化、模型配置与严格模式](./15-pydantic-v2-data-boundaries/normalization-config-and-strict-mode)：
  清理输入，配置模型行为，并决定是否允许自动类型转换。
- [字段校验器、模型校验器与默认值](./15-pydantic-v2-data-boundaries/validators-and-defaults)：
  编写单字段和跨字段规则，并为每个实例安全创建默认值。
- [联合类型、TypeAdapter 与对象输入](./15-pydantic-v2-data-boundaries/unions-adapters-and-object-input)：
  校验多种数据结构、顶层列表和普通 Python 对象。
- [序列化、配置读取与领域模型边界](./15-pydantic-v2-data-boundaries/serialization-settings-and-domain-models)：
  导出模型、读取环境变量，并区分传输模型和业务对象。
