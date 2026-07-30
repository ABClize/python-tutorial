<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";

const modes = {
  assignment: {
    label: "直接赋值",
    code: "copied = original",
    outer: ["outer-a"],
    nested: ["nested-a", "nested-b"],
    edges: [
      ["name-original", "outer-a"],
      ["name-copied", "outer-a"],
      ["outer-a", "nested-a"],
      ["outer-a", "nested-b"],
    ],
    base: "两个变量名指向同一个外层列表，没有创建新列表。",
    changed: "两个名字共享同一个外层对象，因此 copied 也会看到内层列表中的 99。",
  },
  shallow: {
    label: "浅拷贝",
    code: "copied = original.copy()",
    outer: ["outer-a", "outer-b"],
    nested: ["nested-a", "nested-b"],
    edges: [
      ["name-original", "outer-a"],
      ["name-copied", "outer-b"],
      ["outer-a", "nested-a"],
      ["outer-a", "nested-b"],
      ["outer-b", "nested-a"],
      ["outer-b", "nested-b"],
    ],
    base: "外层列表已经分开，但两个外层列表仍指向相同的内层列表。",
    changed: "修改发生在共享的内层列表中，所以 original 和 copied 都能观察到 99。",
  },
  deep: {
    label: "深拷贝",
    code: "copied = copy.deepcopy(original)",
    outer: ["outer-a", "outer-b"],
    nested: ["nested-a", "nested-b", "nested-c", "nested-d"],
    edges: [
      ["name-original", "outer-a"],
      ["name-copied", "outer-b"],
      ["outer-a", "nested-a"],
      ["outer-a", "nested-b"],
      ["outer-b", "nested-c"],
      ["outer-b", "nested-d"],
    ],
    base: "外层和内层列表都已经分开，两个变量指向独立的对象图。",
    changed: "只有 original 指向的内层列表被修改；copied 的对应列表保持不变。",
  },
};

const mode = ref("shallow");
const mutated = ref(false);
const stage = ref(null);
const paths = ref([]);
const nodeRefs = new Map();
let resizeObserver;

const current = computed(() => modes[mode.value]);
const explanation = computed(() =>
  mutated.value ? current.value.changed : current.value.base,
);

function setNodeRef(id, element) {
  if (element) {
    nodeRefs.set(id, element);
  } else {
    nodeRefs.delete(id);
  }
}

function nestedValue(id) {
  if (id === "nested-a") {
    return mutated.value ? "[1, 2, 99]" : "[1, 2]";
  }
  return id === "nested-b" || id === "nested-d" ? "[3, 4]" : "[1, 2]";
}

function outerValue(id) {
  return id === "outer-a" && mutated.value ? "[[…99], […]]" : "[[…], […]]";
}

function drawConnections() {
  if (!stage.value || window.matchMedia("(max-width: 640px)").matches) {
    paths.value = [];
    return;
  }

  const stageRect = stage.value.getBoundingClientRect();
  paths.value = current.value.edges.flatMap(([fromId, toId]) => {
    const from = nodeRefs.get(fromId)?.getBoundingClientRect();
    const to = nodeRefs.get(toId)?.getBoundingClientRect();
    if (!from || !to) {
      return [];
    }
    const startX = from.right - stageRect.left;
    const startY = from.top + from.height / 2 - stageRect.top;
    const endX = to.left - stageRect.left;
    const endY = to.top + to.height / 2 - stageRect.top;
    const horizontalGap = Math.max(0, endX - startX);
    const bend = Math.min(26, horizontalGap * 0.36);
    return [
      `M ${startX} ${startY} C ${startX + bend} ${startY}, ${
        endX - bend
      } ${endY}, ${endX} ${endY}`,
    ];
  });
}

function chooseMode(nextMode) {
  mode.value = nextMode;
  mutated.value = false;
}

watch([mode, mutated], async () => {
  await nextTick();
  drawConnections();
});

onMounted(async () => {
  await nextTick();
  drawConnections();
  resizeObserver = new ResizeObserver(drawConnections);
  resizeObserver.observe(stage.value);
});

onBeforeUnmount(() => resizeObserver?.disconnect());
</script>

<template>
  <figure class="concept-figure">
    <div class="figure-controls diagram-controls">
      <div class="control-field">
        <span class="control-label">复制方式</span>
        <div class="control-buttons">
          <button
            v-for="(item, key) in modes"
            :key="key"
            class="control-button"
            :class="{ active: mode === key }"
            :aria-pressed="mode === key"
            type="button"
            @click="chooseMode(key)"
          >
            {{ item.label }}
          </button>
        </div>
      </div>
      <div class="control-buttons">
        <button
          class="control-button primary"
          type="button"
          :disabled="mutated"
          @click="mutated = true"
        >
          {{ mutated ? "修改已执行" : "修改 original[0]" }}
        </button>
        <button class="control-button" type="button" @click="mutated = false">
          重置
        </button>
      </div>
    </div>

    <div class="figure-status" aria-live="polite">
      <strong>{{ current.label }} · {{ mutated ? "已追加 99" : "尚未修改" }}</strong>
      <p>{{ explanation }}</p>
    </div>

    <div class="figure-canvas">
      <code class="diagram-source">{{ current.code }}</code>
      <div class="diagram-headings">
        <span>变量名</span>
        <span>外层对象</span>
        <span>内层对象</span>
      </div>
      <div ref="stage" class="diagram-stage">
        <svg class="diagram-edges" aria-hidden="true">
          <defs>
            <marker
              id="mutability-arrow"
              marker-width="8"
              marker-height="8"
              ref-x="7"
              ref-y="4"
              orient="auto"
            >
              <path d="M 0 0 L 8 4 L 0 8 z" fill="var(--vp-c-brand-1)" />
            </marker>
          </defs>
          <path
            v-for="(path, index) in paths"
            :key="index"
            :d="path"
            marker-end="url(#mutability-arrow)"
          />
        </svg>

        <div class="diagram-column">
          <span class="diagram-column-label">变量名</span>
          <div
            v-for="name in ['original', 'copied']"
            :key="name"
            :ref="(element) => setNodeRef(`name-${name}`, element)"
            class="diagram-node"
          >
            <small>name</small>
            <code>{{ name }}</code><br />
            <span>引用</span>
          </div>
        </div>

        <div class="diagram-column">
          <span class="diagram-column-label">外层对象</span>
          <div
            v-for="(id, index) in current.outer"
            :key="id"
            :ref="(element) => setNodeRef(id, element)"
            class="diagram-node"
          >
            <small>list</small>
            <code>outer list {{ index === 0 ? "A" : "B" }}</code
            ><br />
            <span>{{ outerValue(id) }}</span>
          </div>
        </div>

        <div class="diagram-column">
          <span class="diagram-column-label">内层对象</span>
          <div
            v-for="(id, index) in current.nested"
            :key="id"
            :ref="(element) => setNodeRef(id, element)"
            class="diagram-node"
            :class="{
              shared: mode === 'shallow',
              changed: id === 'nested-a' && mutated,
            }"
          >
            <small>list</small>
            <code>nested list {{ String.fromCharCode(65 + index) }}</code
            ><br />
            <span>{{ nestedValue(id) }}</span>
          </div>
        </div>
      </div>
    </div>

    <figcaption class="figure-caption">
      箭头表示“引用”，不是把对象装进变量。切换复制方式后，先预测修改会传播到哪里，再执行修改。
    </figcaption>
  </figure>
</template>
