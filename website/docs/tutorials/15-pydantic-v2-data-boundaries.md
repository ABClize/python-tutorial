# Pydantic v2 数据边界

程序接收到的 JSON、表单、环境变量和第三方响应都只是外部数据。Pydantic 的作用，是在这些数据进入
业务代码之前完成解析、校验和结构化，并在数据离开程序时控制序列化结果。

<p class="source-note">对应源码：<code>python/backend_interview/schemas.py</code>、<code>python/backend_interview/pydantic_patterns.py</code>、<code>python/backend_interview/config.py</code></p>

## 本章内容

- [模型、校验错误与字段约束](./15-pydantic-v2-data-boundaries/models-errors-and-fields)
- [输入规范化、模型配置与严格模式](./15-pydantic-v2-data-boundaries/normalization-config-and-strict-mode)
- [字段校验器、模型校验器与默认值](./15-pydantic-v2-data-boundaries/validators-and-defaults)
- [联合类型、TypeAdapter 与对象输入](./15-pydantic-v2-data-boundaries/unions-adapters-and-object-input)
- [序列化、配置读取与领域模型边界](./15-pydantic-v2-data-boundaries/serialization-settings-and-domain-models)
