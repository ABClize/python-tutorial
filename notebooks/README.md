# Jupyter 教程

这些 Notebook 用于理解 Python 概念的执行过程，按从上到下的顺序设计，不依赖隐藏状态。
部分单元使用 `ipywidgets`、Matplotlib 和 Plotly，通过下拉框、滑块、关系图和时间线改变实验条件。

| Notebook | 重点展示 |
| --- | --- |
| `01_mutability_and_copy.ipynb` | 变量、外层列表和内层列表之间的引用关系 |
| `02_functions_and_generators.ipynb` | 生成器每次 `yield` 后保存的执行位置和局部变量 |
| `03_algorithms_and_complexity.ipynb` | 两种算法的正确性与性能差异 |
| `04_asyncio_task_timeline.ipynb` | Task 的并发等待、恢复、完成顺序和取消传播 |

启动 JupyterLab：

```bash
uv sync --group dev
uv run jupyter lab
```

教程内容统一维护在 `tools/build_notebooks.py`，不要直接手工修改 `.ipynb` JSON。重新生成：

```bash
uv run python tools/build_notebooks.py
```

验证全部 Notebook 时把执行输出写入临时目录，避免把控件状态和 Plotly 数据写回源文件：

```bash
notebook_validation_dir="$(mktemp -d)"
for notebook in notebooks/*.ipynb; do
  uv run python -m jupyter nbconvert \
    --execute \
    --to notebook \
    --output-dir "$notebook_validation_dir" \
    "$notebook"
done
```

Notebook 适合操作参数、观察关系和建立心智模型；完整面试题仍建议在 `.py` 文件中完成。
