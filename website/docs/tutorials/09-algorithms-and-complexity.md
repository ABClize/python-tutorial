# Python 算法与复杂度

算法是一组把输入转换为输出的明确步骤。写出能运行的代码只是第一步，还需要知道它对哪些输入有效、
为什么能得到正确结果，以及数据量增大后会消耗多少时间和内存。

本章从复杂度的基本读法开始，再用查找、栈、队列和动态规划等例子说明怎样设计、验证和衡量算法。

<p class="source-note">对应源码：<code>python/python_interview_practice/08_algorithms.py</code>、<code>python/python_interview_practice/09_practice_questions.py</code></p>

## 本章内容

- [复杂度基础](./09-algorithms-and-complexity/complexity-basics)：输入规模、大 O、时间与空间复杂度，以及不同增长速度的可视化。
- [正确性与查找](./09-algorithms-and-complexity/correctness-and-search)：用循环不变量理解两数之和、回文判断和二分查找。
- [栈、队列与广度优先搜索](./09-algorithms-and-complexity/stacks-queues-and-bfs)：根据“后进先出”和“先进先出”选择数据结构。
- [动态规划与序列处理](./09-algorithms-and-complexity/dynamic-programming-and-sequences)：从斐波那契数到合并有序列表、分组和文本处理。
- [测试与实际测量](./09-algorithms-and-complexity/testing-and-measurement)：边界用例、属性测试和 `timeit` 的基本用法。
