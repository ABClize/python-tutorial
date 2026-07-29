<script setup>
import { computed, onBeforeUnmount, ref } from "vue";

const fibonacciValues = [0, 1, 1, 2, 3, 5, 8, 13];
const states = [{ left: null, right: null, line: 1, yielded: null }];
let left = 0;
let right = 1;
for (const value of fibonacciValues) {
  states.push({ left, right, line: 4, yielded: value });
  [left, right] = [right, left + right];
}

const step = ref(0);
const playing = ref(false);
let timer;

const state = computed(() => states[step.value]);
const produced = computed(() => fibonacciValues.slice(0, step.value));
const explanation = computed(() =>
  step.value === 0
    ? "调用 fibonacci() 只创建生成器对象，函数体还没有执行。"
    : "yield 把当前值交给调用者，但 frame 仍保存局部变量；下一次 next() 会从 yield 后继续。",
);

function stop() {
  window.clearInterval(timer);
  timer = undefined;
  playing.value = false;
}

function next() {
  step.value = Math.min(fibonacciValues.length, step.value + 1);
  if (step.value === fibonacciValues.length) {
    stop();
  }
}

function togglePlay() {
  if (playing.value) {
    stop();
    return;
  }
  if (step.value === fibonacciValues.length) {
    step.value = 0;
  }
  playing.value = true;
  timer = window.setInterval(next, 680);
}

onBeforeUnmount(stop);
</script>

<template>
  <figure class="concept-figure">
    <div class="figure-controls">
      <label class="control-field grow">
        <span class="control-label">
          调用次数
          <output>{{ step }} / {{ fibonacciValues.length }}</output>
        </span>
        <input
          v-model.number="step"
          class="control-range"
          type="range"
          min="0"
          :max="fibonacciValues.length"
          step="1"
        />
      </label>
      <div class="control-buttons">
        <button
          class="control-button primary"
          type="button"
          :disabled="step === fibonacciValues.length"
          @click="next"
        >
          {{ step === fibonacciValues.length ? "已到最后一步" : "下一次 next()" }}
        </button>
        <button
          class="control-button"
          type="button"
          :aria-pressed="playing"
          @click="togglePlay"
        >
          {{ playing ? "暂停" : "自动播放" }}
        </button>
      </div>
    </div>

    <div class="figure-status" aria-live="polite">
      <strong>{{ step === 0 ? "尚未开始" : `第 ${step} 次暂停` }}</strong>
      <p>{{ explanation }}</p>
    </div>

    <div class="figure-canvas">
      <div class="frame-layout">
        <div class="code-panel">
          <div class="panel-title">fibonacci()</div>
          <pre class="code-lines"><code><span class="code-line" :class="{ active: state.line === 1 }">1  def fibonacci():</span>
<span class="code-line">2      left, right = 0, 1</span>
<span class="code-line">3      while True:</span>
<span class="code-line" :class="{ active: state.line === 4 }">4          yield left</span>
<span class="code-line">5          left, right = right, left + right</span></code></pre>
        </div>

        <div class="state-panel">
          <div class="panel-title">generator frame</div>
          <div class="state-row">
            <small>状态</small>
            <strong>{{ step === 0 ? "created" : "suspended" }}</strong>
          </div>
          <div class="state-row">
            <small>指令位置</small>
            <span>{{ step === 0 ? "函数体尚未进入" : "第 4 行：yield left" }}</span>
          </div>
          <div class="state-row">
            <small>局部变量</small>
            <code>{{
              step === 0 ? "暂无" : `left = ${state.left}, right = ${state.right}`
            }}</code>
          </div>
          <div class="state-row">
            <small>刚刚产出的值</small>
            <code>{{ step === 0 ? "暂无" : state.yielded }}</code>
          </div>
        </div>
      </div>

      <div class="value-sequence" aria-label="已经产出的值">
        <span v-if="produced.length === 0">尚未调用 next()</span>
        <span v-for="(value, index) in produced" :key="index" class="value-chip">
          {{ value }}
        </span>
      </div>
    </div>

    <figcaption class="figure-caption">
      滑块表示调用者已经执行了多少次 next()；高亮行是生成器当前暂停的位置。
    </figcaption>
  </figure>
</template>
