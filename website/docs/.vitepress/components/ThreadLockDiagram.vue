<script setup>
import { computed, ref } from "vue";

const mode = ref("unlocked");
const step = ref(0);

const scenarios = {
  unlocked: [
    { total: 0, a: "准备读取", b: "准备读取", note: "两个线程都准备执行 total += 1。" },
    { total: 0, a: "读取 0", b: "准备读取", note: "A 把旧值 0 保存到自己的临时状态。" },
    { total: 0, a: "持有 0", b: "读取 0", note: "A 尚未写回时，B 也读到了旧值 0。" },
    { total: 1, a: "写回 1", b: "持有 0", note: "A 完成写回，但 B 的计算仍基于旧值。" },
    { total: 1, a: "完成", b: "写回 1", note: "B 覆盖写入 1，两个自增最终只增加了一次。" },
  ],
  locked: [
    { total: 0, a: "等待锁", b: "等待锁", note: "两个线程竞争同一把互斥锁。" },
    { total: 0, a: "持锁并读取 0", b: "阻塞", note: "A 获得锁，B 不能进入临界区。" },
    { total: 0, a: "计算 1", b: "阻塞", note: "读取、计算和写回被保护为一个整体。" },
    { total: 1, a: "写回并释放", b: "等待锁", note: "A 写回 1 后释放锁。" },
    { total: 2, a: "完成", b: "持锁写回 2", note: "B 随后读取最新值 1，最终正确得到 2。" },
  ],
};

const state = computed(() => scenarios[mode.value][step.value]);

function chooseMode(nextMode) {
  mode.value = nextMode;
  step.value = 0;
}
</script>

<template>
  <figure class="concept-figure">
    <div class="figure-controls">
      <div class="control-field">
        <span class="control-label">执行方式</span>
        <div class="control-buttons">
          <button
            class="control-button"
            :class="{ active: mode === 'unlocked' }"
            type="button"
            @click="chooseMode('unlocked')"
          >
            不加锁
          </button>
          <button
            class="control-button"
            :class="{ active: mode === 'locked' }"
            type="button"
            @click="chooseMode('locked')"
          >
            使用 Lock
          </button>
        </div>
      </div>
      <label class="control-field grow">
        <span class="control-label">
          调度步骤
          <output>{{ step }} / 4</output>
        </span>
        <input v-model.number="step" class="control-range" type="range" min="0" max="4" />
      </label>
    </div>

    <div class="figure-status" aria-live="polite">
      <strong>共享 total = {{ state.total }}</strong>
      <p>{{ state.note }}</p>
    </div>

    <div class="figure-canvas thread-lanes">
      <div class="thread-lane">
        <small>Thread A</small>
        <strong>{{ state.a }}</strong>
      </div>
      <div class="shared-counter">
        <small>共享变量</small>
        <code>{{ state.total }}</code>
        <span v-if="mode === 'locked'" class="lock-indicator">Lock</span>
      </div>
      <div class="thread-lane">
        <small>Thread B</small>
        <strong>{{ state.b }}</strong>
      </div>
    </div>

    <figcaption class="figure-caption">
      这是一次刻意安排的交错顺序，用来说明竞态如何发生；真实线程的调度顺序并不固定。
    </figcaption>
  </figure>
</template>
