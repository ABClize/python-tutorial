<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

const delays = ref([0.8, 0.5, 0.3]);
const cancelB = ref(false);
const plot = ref(null);
let Plotly;

const names = ["任务 A", "任务 B", "任务 C"];
const colors = ["#173b5c", "#d97706", "#256f8a"];
const cancelAt = 0.3;

const visibleDelays = computed(() => [
  delays.value[0],
  cancelB.value && cancelAt < delays.value[1] ? cancelAt : delays.value[1],
  delays.value[2],
]);
const isActuallyCancelled = computed(
  () => cancelB.value && cancelAt < delays.value[1],
);
const timelineEvents = computed(() =>
  names
    .map((name, index) => ({
      name: isActuallyCancelled.value && index === 1 ? "任务 B（取消）" : name,
      time: visibleDelays.value[index],
      index,
    }))
    .sort((left, right) => left.time - right.time || left.index - right.index),
);
const summary = computed(() => {
  if (isActuallyCancelled.value) {
    return "B 在等待期间收到取消，先执行 finally 清理，再把 CancelledError 传播给等待 gather 的调用者。";
  }

  const earliestTime = timelineEvents.value[0].time;
  const earliestTasks = timelineEvents.value
    .filter((event) => event.time === earliestTime)
    .map((event) => event.name);
  const earliestDescription =
    earliestTasks.length === 1
      ? `${earliestTasks[0]} 最先完成`
      : `${earliestTasks.join("、")} 在图中同时完成`;
  const longest = Math.max(...visibleDelays.value);
  return `${earliestDescription}；总等待约等于最慢任务的 ${longest.toFixed(
    1,
  )} 秒，而不是三段延迟相加。`;
});

function updateDelay(index, event) {
  const next = [...delays.value];
  next[index] = Number(event.target.value) / 10;
  delays.value = next;
}

function renderPlot() {
  if (!Plotly || !plot.value) {
    return;
  }

  const shapes = isActuallyCancelled.value
    ? [
        {
          type: "line",
          x0: cancelAt,
          x1: cancelAt,
          y0: -0.5,
          y1: 2.5,
          line: { color: "#b91c1c", width: 2, dash: "dot" },
        },
      ]
    : [];
  const annotations = isActuallyCancelled.value
    ? [
        {
          x: cancelAt,
          y: 1.14,
          xref: "x",
          yref: "paper",
          text: "cancel(B)",
          showarrow: false,
          font: { color: "#b91c1c", size: 12 },
        },
      ]
    : [];

  Plotly.react(
    plot.value,
    [
      {
        x: visibleDelays.value,
        y: names,
        type: "bar",
        orientation: "h",
        name: "等待外部 I/O",
        marker: { color: colors, opacity: 0.82 },
        text: visibleDelays.value.map((delay, index) =>
          isActuallyCancelled.value && index === 1
            ? `等待 ${delay.toFixed(1)} 秒后取消`
            : `等待 ${delay.toFixed(1)} 秒`,
        ),
        textposition: "inside",
        insidetextanchor: "middle",
        hovertemplate: "%{y}<br>%{text}<extra></extra>",
      },
      {
        x: visibleDelays.value,
        y: names,
        type: "scatter",
        mode: "markers",
        name: "恢复或取消点",
        marker: {
          color: colors,
          size: 14,
          symbol: names.map((_, index) =>
            isActuallyCancelled.value && index === 1 ? "x" : "diamond",
          ),
          line: { color: "#ffffff", width: 2 },
        },
        hovertemplate: "%{y}<br>时间 %{x:.1f} 秒<extra></extra>",
      },
    ],
    {
      autosize: true,
      height: 430,
      margin: { l: 72, r: 22, t: 42, b: 58 },
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      font: {
        color: "#506176",
        family: "'Segoe UI', 'Microsoft YaHei', sans-serif",
      },
      showlegend: false,
      bargap: 0.48,
      xaxis: {
        title: { text: "相对时间（秒）", standoff: 10 },
        automargin: true,
        range: [0, Math.max(1.05, Math.max(...delays.value) + 0.08)],
        gridcolor: "rgba(23,32,51,0.12)",
        zeroline: false,
      },
      yaxis: { autorange: "reversed", gridcolor: "rgba(0,0,0,0)" },
      shapes,
      annotations,
    },
    { displayModeBar: false, responsive: true },
  );
}

watch([delays, cancelB], renderPlot, { deep: true });

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
      <label v-for="(delay, index) in delays" :key="index" class="control-field">
        <span class="control-label">
          任务 {{ String.fromCharCode(65 + index) }}
          <output>{{ delay.toFixed(1) }} 秒</output>
        </span>
        <input
          class="control-range"
          type="range"
          min="2"
          max="10"
          step="1"
          :value="delay * 10"
          @input="updateDelay(index, $event)"
        />
      </label>
      <div class="control-field">
        <span class="control-label">取消</span>
        <div class="control-buttons">
          <button
            class="control-button"
            :class="{ active: !cancelB }"
            type="button"
            @click="cancelB = false"
          >
            不取消
          </button>
          <button
            class="control-button"
            :class="{ active: cancelB }"
            type="button"
            @click="cancelB = true"
          >
            0.3 秒取消 B
          </button>
        </div>
      </div>
    </div>

    <div class="figure-status" aria-live="polite">
      <strong>{{ isActuallyCancelled ? "取消在暂停点传播" : "并发等待" }}</strong>
      <p>{{ summary }}</p>
    </div>

    <div class="figure-canvas">
      <div ref="plot" class="plot-container" aria-label="asyncio 任务时间线"></div>
      <div class="state-row">
        <small>按时间排序的完成 / 取消事件</small>
        <div class="task-order">
          <template v-for="(event, index) in timelineEvents" :key="event.name">
            <span class="task-pill">{{ event.name }}</span>
            <span v-if="index < timelineEvents.length - 1" aria-hidden="true">
              {{ event.time === timelineEvents[index + 1].time ? "＝" : "→" }}
            </span>
          </template>
        </div>
      </div>
      <div class="state-row">
        <small>await gather(...) 的观察结果</small>
        <div class="task-order">
          <span v-if="isActuallyCancelled" class="task-pill">抛出 CancelledError</span>
          <template v-else>
            <template v-for="(name, index) in names" :key="name">
              <span class="task-pill">{{ name }}</span>
              <span v-if="index < names.length - 1" aria-hidden="true">→</span>
            </template>
          </template>
        </div>
      </div>
    </div>

    <figcaption class="figure-caption">
      条形长度表示任务暂停等待外部 I/O 的时间；菱形或叉号表示任务恢复或接收取消的位置。
      等号表示事件落在同一图示时刻，不代表事件循环内部存在固定先后顺序。
    </figcaption>
  </figure>
</template>
