# Pydantic v2 与数据边界

Pydantic 的核心作用不是“把 dict 变成对象”，而是在不可信外部数据与内部代码之间建立明确边界：
解析输入、执行约束、生成稳定错误、序列化输出，并为 OpenAPI 提供结构信息。

<p class="source-note">对应源码：<code>python/backend_interview/schemas.py</code>、<code>python/backend_interview/pydantic_patterns.py</code>、<code>python/backend_interview/config.py</code></p>

## 验证流程不只是类型检查

一个输入值通常经历：

<div class="concept-map">
  <div class="concept-step"><small>原始输入</small><strong>JSON / env / dict</strong></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>预处理</small><strong>before validator</strong></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>核心解析</small><strong>类型与 Field 约束</strong></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>业务内一致性</small><strong>after validator</strong></div>
  <span class="concept-arrow">→</span>
  <div class="concept-step"><small>输出</small><strong>serializer</strong></div>
</div>

验证成功后，模型字段应处于内部代码可以信任的形态。数据库存在性、权限和远程服务状态需要 I/O，
不应隐藏在 validator 中，而应由服务层处理。

## Annotated 把约束绑定到类型

```python
from typing import Annotated
from pydantic import BeforeValidator, Field, StringConstraints


def normalize_sku(value):
    return value.strip().upper() if isinstance(value, str) else value


Sku = Annotated[
    str,
    BeforeValidator(normalize_sku),
    StringConstraints(pattern=r"^[A-Z0-9-]{3,20}$"),
]
Quantity = Annotated[int, Field(gt=0, le=100)]
```

类型别名可以在多个 Schema 之间复用统一边界。预处理只做安全、确定性的规范化；如果规范化会改变
业务含义，例如自动截断超长字符串，通常应直接拒绝输入。

## 宽松解析与 strict 模式

Pydantic 默认会执行一部分合理转换，例如把数字字符串解析为数字。这适合 HTTP 和环境变量等文本
边界，但也可能隐藏调用方错误。

```python
class StrictMetric(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    name: str
    value: float
```

strict 模式拒绝隐式类型转换，`extra="forbid"` 拒绝未声明字段。对内部命令、财务数据和安全敏感
配置，严格模式常更容易发现协议漂移；对用户表单，可选择规范化后给出友好错误。

## 字段验证与模型验证

字段验证适合单个字段的清洗和约束；模型验证适合跨字段不变量：

```python
class RegistrationRequest(BaseModel):
    password: SecretStr
    password_repeat: SecretStr

    @model_validator(mode="after")
    def passwords_must_match(self) -> Self:
        if self.password != self.password_repeat:
            raise ValueError("两次密码不一致")
        return self
```

验证顺序很重要：before validator 面对原始输入，after validator 面对已经解析的值。不要依赖兄弟
字段尚未保证的执行顺序来实现跨字段规则。

## default_factory 防止共享状态

```python
tags: list[str] = Field(default_factory=list)
```

工厂为每个模型创建独立列表。虽然 Pydantic 对部分默认值有自己的复制处理，显式 default_factory
仍最准确地表达意图，也与 dataclass 规则一致。

## 判别联合表达多种数据形状

支付方式、领域事件等数据通常由某个字段决定具体结构：

```python
class CardPayment(BaseModel):
    kind: Literal["card"]
    last_four: str


class WalletPayment(BaseModel):
    kind: Literal["wallet"]
    provider: Literal["alipay", "wechat"]


PaymentMethod = Annotated[
    CardPayment | WalletPayment,
    Field(discriminator="kind"),
]
```

discriminator 让解析直接选择分支，错误也更聚焦。没有判别字段的普通 Union 可能依次尝试多个模型，
产生难读错误或意外选择宽松分支。

## RootModel 与 TypeAdapter

并非所有 JSON 顶层都是对象。顶层列表可以使用 `RootModel[list[DomainEvent]]`。若只需要验证一个
类型表达式而不需要定义模型类，使用 TypeAdapter：

```python
adapter = TypeAdapter(list[DomainEvent])
events = adapter.validate_python(payload)
```

TypeAdapter 也能生成 JSON Schema 和执行序列化，适合列表、Union、TypedDict 等独立类型。

## 泛型响应模型

分页结构可以用 Generic 保留 items 元素类型：

```python
T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1)
```

`Page[OrderResponse]` 会在类型检查和 OpenAPI 中保留订单结构，而不是退化为 `list[Any]`。

## 从领域对象生成响应

`ConfigDict(from_attributes=True)` 允许从对象属性读取字段，替代 Pydantic v1 的 ORM mode。它只解决
数据读取方式，不等于领域对象与 API Schema 应该合并。

显式 `from_domain()` 转换能处理时间格式、枚举、计算字段和字段重命名，也为未来 API 版本演进提供
稳定边界。

## computed_field 与 serializer

computed_field 把派生值加入序列化结果，例如订单项 subtotal；field_serializer 控制日期、枚举和
自定义值的输出形式。

序列化规则属于公开契约。内部 datetime 可以保持 aware 对象，输出时统一为 UTC ISO 8601；Decimal
如何转 JSON 则要与客户端精度约定一致。

## SecretStr 只是防止意外展示

SecretStr 在 repr 和普通 dump 中遮蔽值，减少日志误泄露，但它不是加密，也不会清除进程内存。
真正使用时必须显式 `get_secret_value()`，并避免把结果写入日志、异常或追踪属性。

## BaseSettings 管理环境配置

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="INTERVIEW_",
        env_file=".env",
        extra="ignore",
    )

    request_timeout_seconds: float = Field(gt=0, le=30)
    max_concurrency: int = Field(ge=1, le=100)
```

配置应在应用启动边界解析一次，尽早失败。测试可以直接传 Settings 对象或清除缓存，不应在每个业务
函数里重新读取 `os.environ`。

环境变量都是字符串，Pydantic 会解析基础类型和复杂 JSON 值。生产 Secret 应来自专用密钥系统，
`.env` 只适合本地开发且不能提交敏感值。

## 验证错误如何成为 API 契约

Pydantic 错误包含 location、message、type 和上下文。API 可以把它映射为稳定 envelope，但不要把
内部 traceback 或敏感输入返回客户端。

客户端通常依赖字段路径定位表单问题，因此随意改嵌套结构、错误码或字段名称都可能是破坏性变更。

## 常见误区

### Pydantic 模型就是领域模型

Schema 面向外部数据格式，领域模型面向业务状态和行为。简单 CRUD 可以重合，复杂系统应明确边界。

### validator 可以查数据库

validator 应保持同步、快速和确定。数据库唯一性、资源权限和外部状态属于服务层。

### SecretStr 等于安全存储

它只减少 repr 和日志中的意外展示，不提供静态加密、权限隔离或密钥轮换。

### model_dump 后一定可以直接发 JSON

Python mode 可能保留 datetime、UUID、Decimal 等对象；需要 JSON 兼容输出时使用正确模式，并确认
序列化精度和格式契约。

## 面试时怎么表述

> Pydantic 位于不可信输入和内部代码之间，负责解析、约束、错误结构与序列化。字段 validator 处理
> 局部值，model validator 维护跨字段不变量；需要 I/O 的规则留在服务层。判别联合表达多态输入，
> Generic 保留响应元素类型，BaseSettings 在启动边界集中验证配置。
