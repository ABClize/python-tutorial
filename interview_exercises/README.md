# Python 面试练习与参考实现

这个目录不是用来“背答案”的，而是用来练习面试时完整的思考过程：

1. 只看函数文档中的题目，先自己写一版。
2. 写出时间复杂度、空间复杂度和边界条件。
3. 运行文件，让 `assert` 帮你检查结果。
4. 对照参考实现，尝试解释每一行为什么存在。
5. 修改测试数据，并在 VS Code 中打断点观察变量变化。

所有代码只使用 Python 标准库，适合 Python 3.11+。

## 内容

| 文件 | 面试主题 | 重点 |
| --- | --- | --- |
| `strings.py` | 字符串 | 计数、滑动窗口、栈、编码 |
| `collections.py` | 容器 | 去重、区间合并、频率统计、LRU |
| `algorithms.py` | 算法 | 二分、哈希、动态规划、图、堆 |
| `oop.py` | 面向对象 | 属性、数据类、抽象、组合、上下文管理器 |
| `concurrency.py` | 并发 | 线程、锁、队列、线程池、asyncio |

## 运行

在项目根目录运行单个主题：

```bash
python3.11 interview_exercises/strings.py
python3.11 interview_exercises/collections.py
python3.11 interview_exercises/algorithms.py
python3.11 interview_exercises/oop.py
python3.11 interview_exercises/concurrency.py
```

运行全部主题：

```bash
for file in interview_exercises/{strings,collections,algorithms,oop,concurrency}.py; do
    python3.11 "$file"
done
```

每个脚本最后都会运行自检。看到 `全部测试通过`，表示文件中的断言均成立。

## 推荐的面试练法

面对每一道题，按下面的顺序回答：

- 先确认输入、输出、重复值、空输入、非法输入等约束。
- 先说最直接的方案，再说明如何优化。
- 写代码时说出关键变量维护的不变量。
- 主动给出时间与空间复杂度。
- 用正常用例、边界用例和异常用例测试。
- 最后说明真实项目中可能采用的标准库或第三方工具。

例如“最长无重复子串”不应该只给出代码，还应该解释：

- 窗口 `[left, right]` 内始终没有重复字符。
- 遇到重复字符时，左边界只能向右移动，不能后退。
- 每个字符最多被窗口边界处理常数次，因此时间复杂度是 `O(n)`。
