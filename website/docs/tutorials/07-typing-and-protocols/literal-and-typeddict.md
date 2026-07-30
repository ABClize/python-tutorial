# Python Enum、Literal、类型别名与 TypedDict

普通的 `int`、`str` 和 `dict` 有时说明得不够具体。类型别名给复杂类型起名字，`Literal` 限制可选
值，`Enum` 创建运行时可用的枚举成员，`TypedDict` 说明字典中有哪些 key。

<!-- 对应源码：python/python_interview_practice/11_typing_protocols.py -->

## 类型别名

下面给用户编号和成绩表分别起一个类型名称：

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

用户 id 和订单 id 在运行时都是整数，但不能混用。下面使用 `NewType` 区分它们：

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

下面的排序函数只允许 `"asc"` 和 `"desc"` 两个排序方向：

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

## Enum 创建运行时枚举

`Enum` 把一组相关常量组织成一种真正的运行时类型。下面用它表示审核状态：

```python
from enum import Enum


class ReviewStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"


current = ReviewStatus.APPROVED

print(current)
print(current.name)
print(current.value)
print(current == "approved")
```

运行结果：

```text
ReviewStatus.APPROVED
APPROVED
approved
False
```

`ReviewStatus.APPROVED` 是枚举成员，不是普通字符串：

- `name` 是代码中定义的成员名称，这里是 `"APPROVED"`；
- `value` 是赋给成员的值，这里是 `"approved"`；
- 普通 `Enum` 成员不会直接等于它的字符串值，需要字符串时显式读取 `.value`。

枚举类可以直接遍历，成员按定义顺序出现：

```python
for status in ReviewStatus:
    print(status.name, status.value)
```

运行结果：

```text
PENDING pending
APPROVED approved
```

遍历适合生成选项列表。还可以用 `ReviewStatus("approved")` 从 value 找到成员；如果 value 不存在，
会抛出 `ValueError`，因此 `Enum` 能参与运行时校验。

## StrEnum 与 auto

接口、配置和 JSON 经常需要字符串。Python 3.11 新增的 `StrEnum` 是 `str` 的子类，同时具有枚举
成员的性质：

```python
from enum import StrEnum, auto


class Command(StrEnum):
    START = auto()
    STOP = auto()


command = Command.START

print(command)
print(command.name)
print(command.value)
print(command == "start")
```

运行结果：

```text
start
START
start
True
```

`StrEnum` 的 `auto()` 会把成员名称转换为小写字符串，因此 `START` 的 value 是 `"start"`。
`StrEnum` 成员可以直接和字符串比较，也能用在大多数接收字符串的地方。少数代码会严格检查
`type(value) == str`，此时应显式传入 `str(command)`。如果外部协议要求 `"in-progress"` 这类
不能由名称简单转成小写的值，就应显式写出：

```python
class JobStatus(StrEnum):
    IN_PROGRESS = "in-progress"
```

`command.upper()` 等字符串操作返回的是普通 `str`，不会自动保留 `Command` 枚举类型。需要继续按
枚举处理时，应保留原成员，或用 `Command(value)` 显式转换。

### Enum、Literal 和局部常量怎么选

| 情况 | 建议 |
| --- | --- |
| 只想让静态检查器限制几个字面值 | 使用 `Literal` |
| 需要运行时成员、遍历、value 转换或枚举方法 | 使用 `Enum` |
| 外部接口需要字符串，同时需要枚举能力 | Python 3.11+ 使用 `StrEnum` |
| 值只在一个很小的局部范围使用，也不需要类型限制或遍历 | 保留简单常量 |

例如 `DEFAULT_PAGE_SIZE = 20` 只表示当前模块的默认值，没有必要为了它定义枚举。反过来，审核状态会在
多个函数之间传递，还需要生成选项和校验输入，使用 `Enum` 更清楚。

## TypedDict 描述字典结构

下面的 `CandidateRecord` 要求字典包含 `name` 和 `skills`，`years` 可以省略：

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

检查器会相信 `TypeGuard` 的声明，因此函数返回 `True` 时必须真的满足目标结构。普通
`isinstance()` 和 `is not None` 已经够用时，不必增加 `TypeGuard`。

## 选择数据表示

| 需求 | 常用工具 |
| --- | --- |
| 为复杂类型起名字 | `TypeAlias` |
| 区分底层类型相同的标识 | `NewType` |
| 限制少量固定值 | `Literal` |
| 组织运行时可遍历的固定成员 | `Enum` |
| 固定成员还要直接作为字符串使用 | `StrEnum` |
| 描述既有 dict 的 key 结构 | `TypedDict` |
| 需要运行时校验 | Pydantic 或显式校验 |
| 需要方法和不变量 | dataclass 或普通类 |

TypedDict 适合保留 dict 接口的数据。数据需要行为、构造校验或不可变约束时，类通常更清楚。
