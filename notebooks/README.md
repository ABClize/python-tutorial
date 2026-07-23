# Jupyter 教程

这些 Notebook 用于分步骤实验，按从上到下的顺序设计，不依赖隐藏状态。

启动 JupyterLab：

```bash
uv run jupyter lab
```

重新生成并验证全部 Notebook：

```bash
uv run python tools/build_notebooks.py
for notebook in notebooks/*.ipynb; do
  uv run python -m jupyter nbconvert --execute --to notebook --inplace "$notebook"
done
```

Notebook 适合观察变量和分段实验；完整面试题仍建议在 `.py` 文件中完成，并通过自动测试验证。
