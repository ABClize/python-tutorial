<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

const inputSize = ref(120);
const scale = ref("linear");
const plot = ref(null);
let Plotly;

const counts = computed(() => ({
  brute: (inputSize.value * (inputSize.value - 1)) / 2,
  hashed: inputSize.value,
}));
const ratio = computed(() => counts.value.brute / counts.value.hashed);
const formatNumber = (value) =>
  new Intl.NumberFormat("zh-CN", { maximumFractionDigits: 1 }).format(value);

function renderPlot() {
  if (!Plotly || !plot.value) {
    return;
  }

  const xValues = [];
  const bruteValues = [];
  const hashValues = [];
  for (let current = 10; current <= 500; current += 10) {
    xValues.push(current);
    bruteValues.push((current * (current - 1)) / 2);
    hashValues.push(current);
  }

  Plotly.react(
    plot.value,
    [
      {
        x: xValues,
        y: bruteValues,
        type: "scatter",
        mode: "lines",
        name: "暴力搜索 O(n²)",
        line: { color: "#d97706", width: 3 },
        hovertemplate: "n = %{x}<br>数对检查 ≈ %{y:,}<extra></extra>",
      },
      {
        x: xValues,
        y: hashValues,
        type: "scatter",
        mode: "lines",
        name: "哈希表 O(n)",
        line: { color: "#256f8a", width: 3 },
        hovertemplate: "n = %{x}<br>元素处理 ≈ %{y:,}<extra></extra>",
      },
      {
        x: [inputSize.value, inputSize.value],
        y: [counts.value.brute, counts.value.hashed],
        type: "scatter",
        mode: "markers",
        name: "当前 n",
        marker: {
          color: ["#d97706", "#256f8a"],
          size: 11,
          line: { color: "#ffffff", width: 2 },
        },
        hovertemplate: "当前值：%{y:,}<extra></extra>",
      },
    ],
    {
      autosize: true,
      height: 430,
      margin: { l: 68, r: 20, t: 24, b: 60 },
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      font: {
        color: "#506176",
        family: "'Segoe UI', 'Microsoft YaHei', sans-serif",
      },
      legend: { orientation: "h", x: 0, y: 1.12 },
      xaxis: {
        title: { text: "输入规模 n", standoff: 10 },
        automargin: true,
        gridcolor: "rgba(23,32,51,0.12)",
        zeroline: false,
      },
      yaxis: {
        title: { text: "主要操作量（估算）", standoff: 8 },
        automargin: true,
        type: scale.value,
        gridcolor: "rgba(23,32,51,0.12)",
        zeroline: false,
        rangemode: "tozero",
      },
      hovermode: "x unified",
      showlegend: true,
    },
    { displayModeBar: false, responsive: true },
  );
}

watch([inputSize, scale], renderPlot);

onMounted(async () => {
  const module = await import("plotly.js-basic-dist-min");
  Plotly = module.default ?? module;
  renderPlot();
});

onBeforeUnmount(() => {
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
          输入规模
          <output>n = {{ inputSize }}</output>
        </span>
        <input
          v-model.number="inputSize"
          class="control-range"
          type="range"
          min="10"
          max="500"
          step="10"
        />
      </label>
      <div class="control-field">
        <span class="control-label">纵轴</span>
        <div class="control-buttons">
          <button
            class="control-button"
            :class="{ active: scale === 'linear' }"
            type="button"
            @click="scale = 'linear'"
          >
            线性
          </button>
          <button
            class="control-button"
            :class="{ active: scale === 'log' }"
            type="button"
            @click="scale = 'log'"
          >
            对数
          </button>
        </div>
      </div>
    </div>

    <div class="figure-status" aria-live="polite">
      <strong>n = {{ inputSize }}</strong>
      <p>
        暴力方案约检查 {{ formatNumber(counts.brute) }} 个数对；哈希方案约处理
        {{ formatNumber(counts.hashed) }} 个元素。
      </p>
    </div>

    <div class="figure-canvas">
      <div ref="plot" class="plot-container" aria-label="复杂度增长曲线"></div>
      <div class="metric-row">
        <div class="metric-item">
          <small>暴力搜索 O(n²)</small>
          <strong>{{ formatNumber(counts.brute) }}</strong>
        </div>
        <div class="metric-item">
          <small>哈希表 O(n)</small>
          <strong>{{ formatNumber(counts.hashed) }}</strong>
          <em> · 约少 {{ formatNumber(ratio) }} 倍</em>
        </div>
      </div>
    </div>

    <figcaption class="figure-caption">
      曲线表示主要操作量的数量级，不是某台机器上的真实运行时间。切换到对数轴可以同时观察两条曲线。
    </figcaption>
  </figure>
</template>
