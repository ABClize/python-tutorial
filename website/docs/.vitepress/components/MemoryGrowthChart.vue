<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { observePlotTheme, readPlotTheme } from "./plotTheme.js";

const itemCount = ref(100_000);
const plot = ref(null);
let Plotly;
let stopObservingTheme;

const listBytes = computed(() => 56 + itemCount.value * 8);
const generatorBytes = 208;
const formatBytes = (bytes) => {
  if (bytes >= 1024 * 1024) {
    return `${(bytes / 1024 / 1024).toFixed(2)} MiB`;
  }
  if (bytes >= 1024) {
    return `${(bytes / 1024).toFixed(1)} KiB`;
  }
  return `${bytes} B`;
};

function renderPlot() {
  if (!Plotly || !plot.value) {
    return;
  }

  const colors = readPlotTheme();
  const sizes = [1_000, 10_000, 50_000, 100_000, 250_000, 500_000];
  Plotly.react(
    plot.value,
    [
      {
        x: sizes,
        y: sizes.map((size) => 56 + size * 8),
        type: "scatter",
        mode: "lines",
        name: "列表容器（估算）",
        line: { color: colors.secondary, width: 3 },
        hovertemplate: "n = %{x:,}<br>容器 ≈ %{y:,} B<extra></extra>",
      },
      {
        x: sizes,
        y: sizes.map(() => generatorBytes),
        type: "scatter",
        mode: "lines",
        name: "生成器对象（近似常量）",
        line: { color: colors.primary, width: 3 },
        hovertemplate: "n = %{x:,}<br>对象 ≈ %{y:,} B<extra></extra>",
      },
      {
        x: [itemCount.value, itemCount.value],
        y: [listBytes.value, generatorBytes],
        type: "scatter",
        mode: "markers",
        name: "当前 n",
        marker: {
          color: [colors.secondary, colors.primary],
          size: 11,
          line: { color: colors.markerBorder, width: 2 },
        },
        hovertemplate: "%{y:,} B<extra></extra>",
      },
    ],
    {
      autosize: true,
      height: 410,
      margin: { l: 72, r: 20, t: 24, b: 60 },
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      font: {
        color: colors.text,
        family: "'Segoe UI', 'Microsoft YaHei', sans-serif",
      },
      legend: { orientation: "h", x: 0, y: 1.13 },
      xaxis: {
        title: { text: "元素数量 n", standoff: 10 },
        automargin: true,
        type: "log",
        minorloglabels: "none",
        gridcolor: colors.grid,
        zeroline: false,
      },
      yaxis: {
        title: { text: "浅层容器大小（字节）", standoff: 8 },
        automargin: true,
        type: "log",
        minorloglabels: "none",
        gridcolor: colors.grid,
        zeroline: false,
      },
      hovermode: "x unified",
    },
    { displayModeBar: false, responsive: true },
  );
}

watch(itemCount, renderPlot);

onMounted(async () => {
  const module = await import("plotly.js-basic-dist-min");
  Plotly = module.default ?? module;
  stopObservingTheme = observePlotTheme(renderPlot);
  renderPlot();
});

onBeforeUnmount(() => {
  stopObservingTheme?.();
  if (Plotly && plot.value) {
    Plotly.purge(plot.value);
  }
});
</script>

<template>
  <figure class="concept-figure">
    <div class="figure-controls">
      <label class="control-field grow">
        <span class="control-label">
          元素数量
          <output>n = {{ itemCount.toLocaleString("zh-CN") }}</output>
        </span>
        <input
          v-model.number="itemCount"
          class="control-range"
          type="range"
          min="1000"
          max="500000"
          step="1000"
        />
      </label>
    </div>

    <div class="figure-status" aria-live="polite">
      <strong>列表容器约 {{ formatBytes(listBytes) }}</strong>
      <p>生成器对象本身约 {{ formatBytes(generatorBytes) }}，不会随尚未产出的元素数量线性增长。</p>
    </div>

    <div class="figure-canvas">
      <div ref="plot" class="plot-container" aria-label="列表和生成器的浅层内存增长"></div>
    </div>

    <figcaption class="figure-caption">
      图中是用于解释增长趋势的浅层估算，不包含元素对象及共享引用；实际值应以 tracemalloc
      和当前 Python 版本测量为准。
    </figcaption>
  </figure>
</template>
