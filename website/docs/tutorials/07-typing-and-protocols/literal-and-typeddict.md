# Python Literal、类型别名与 TypedDict

基础类型有时无法表达业务含义。类型别名可以给复杂类型命名，`Literal` 限制有限选项，`TypedDict`
描述具有固定 key 结构的字典。

<p class="source-note">对应源码：<code>python/python_interview_practice/11_typing_protocols.py</code></p>

## 类型别名

```python
from typing import TypeAlias

UserId: TypeAlias = int
ScoreMap: TypeAlias = dict[str, int]


def find_score(name: str, scores: ScoreMap) -> int | None:
    return scores.get(name)
```

本项目使用 Python 3.11，因此采用 `TypeAlias`。Python 3.12+ 还可以使用 type 语句：

```text
type ScoreMap = dict[str, int]
```

普通别名改善可读性，但不会创建新类型，`UserId` 与 int 对静态检查器仍然可以互换。

## NewType 区分业务标识

底层都是 int 的用户 id 和订单 id 可以使用 `NewType` 区分：

```python
from typing import NewType

UserId = NewType("UserId", int)
OrderId = NewType("OrderId", int)


def load_user(user_id: UserId) -> str:
    return f"user-{user_id}"


print(load_user(UserId(1001)))
```

运行结果：

```text
user-1001
```

静态检查器会区分 `UserId` 和 `OrderId`。运行时 `NewType` 几乎不增加包装，不能承担范围校验和对象
行为；需要这些能力时应定义真正的值对象。

## Literal 限制有限值

```python
from typing import Literal

SortOrder = Literal["asc", "desc"]


def sort_numbers(
    values: list[int],
    order: SortOrder = "asc",
) -> list[int]:
    return sorted(values, reverse=order == "desc")


print(sort_numbers([3, 1, 2], "desc"))
```

运行结果：

```text
[3, 2, 1]
```

检查器能够发现 `sort_numbers(values, "random")`。Literal 本身不会在运行时拒绝其他字符串。选项需要
方法、展示名称或运行时枚举时，可以使用 `Enum`。

## TypedDict 描述字典结构

```python
from typing import NotRequired, TypedDict


class CandidateRecord(TypedDict):
    name: str
    skills: list[str]
    years: NotRequired[int]


def display_candidate(record: CandidateRecord) -> str:
    years = record.get("years", 0)
    return f"{record['name']}：{years} 年"


candidate: CandidateRecord = {
    "name": "小林",
    "skills": ["Python", "SQL"],
}

print(display_candidate(candidate))
```

运行结果：

```text
小林：0 年
```

默认情况下每个字段都是必需的。`NotRequired[int]` 表示 key 可以不存在；它不是 `int | None`，key
存在时 value 仍必须是 int。

TypedDict 实例在运行时仍是普通 dict：

```python
print(type(candidate))
```

运行结果：

```text
<class 'dict'>
```

因此它不会自动验证外部 JSON 是否缺字段或类型错误。外部数据进入系统时仍需运行时验证。

## total=False 与 Required

大多数字段都可省略时，可以设置 `total=False`，再用 `Required` 标记少数必需字段：

```python
from typing import Required, TypedDict


class UpdateCandidate(TypedDict, total=False):
    candidate_id: Required[int]
    name: str
    years: int
```

这里 `candidate_id` 必须存在，`name` 和 `years` 可以省略。是否允许省略 key 与 value 是否允许 None
是两个独立问题。

## TypeGuard 缩窄 TypedDict

复杂判断可以通过 `TypeGuard` 告诉检查器 True 分支中的精确结构：

```python
from typing import NotRequired, TypeGuard, TypedDict


class CandidateRecord(TypedDict):
    name: str
    years: NotRequired[int]


class ExperiencedCandidate(TypedDict):
    name: str
    years: int


def has_experience(
    record: CandidateRecord,
) -> TypeGuard[ExperiencedCandidate]:
    return isinstance(record.get("years"), int)


candidate: CandidateRecord = {"name": "小林", "years": 5}

if has_experience(candidate):
    print(candidate["years"] + 1)
```

运行结果：

```text
6
```

检查器会相信 TypeGuard 的声明，因此实现必须真的保证目标结构。普通 `isinstance()` 和
`is not None` 已经足够时，不必增加 TypeGuard。

## 选择数据表示

| 需求 | 常用工具 |
| --- | --- |
| 为复杂类型起名字 | `TypeAlias` |
| 区分底层类型相同的标识 | `NewType` |
| 限制少量固定值 | `Literal` |
| 描述既有 dict 的 key 结构 | `TypedDict` |
| 需要运行时校验 | Pydantic 或显式校验 |
| 需要方法和不变量 | dataclass 或普通类 |

TypedDict 适合保留 dict 接口的数据。数据需要行为、构造校验或不可变约束时，类通常更清楚。
