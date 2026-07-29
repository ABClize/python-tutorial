<script setup>
import { computed, ref } from "vue";

const examples = [
  { label: "0", value: 0, type: "int", reason: "数字零是假值。" },
  { label: "1", value: 1, type: "int", reason: "非零数字是真值。" },
  { label: "''", value: "", type: "str", reason: "空字符串是假值。" },
  { label: "'0'", value: "0", type: "str", reason: "只要字符串非空，就是真值。" },
  { label: "[]", value: [], type: "list", reason: "空容器是假值。" },
  { label: "[0]", value: [0], type: "list", reason: "容器是否为真只看是否为空，不看元素真假。" },
  { label: "None", value: null, type: "NoneType", reason: "None 固定是假值。" },
];

const selectedIndex = ref(0);
const selected = computed(() => examples[selectedIndex.value]);
const result = computed(() => Boolean(selected.value.value));
</script>

<template>
  <figure class="concept-figure">
    <div class="figure-controls">
      <div class="control-field grow">
        <span class="control-label">选择一个值</span>
        <div class="control-buttons">
          <button
            v-for="(item, index) in examples"
            :key="item.label"
            class="control-button"
            :class="{ active: selectedIndex === index }"
            type="button"
            @click="selectedIndex = index"
          >
            {{ item.label }}
          </button>
        </div>
      </div>
    </div>

    <div class="figure-status" aria-live="polite">
      <strong>bool({{ selected.label }}) → {{ result }}</strong>
      <p>{{ selected.reason }}</p>
    </div>

    <div class="figure-canvas truthiness-result">
      <div>
        <small>值</small>
        <code>{{ selected.label }}</code>
      </div>
      <span aria-hidden="true">→</span>
      <div>
        <small>类型</small>
        <code>{{ selected.type }}</code>
      </div>
      <span aria-hidden="true">→</span>
      <div>
        <small>真值</small>
        <strong :class="result ? 'truthy' : 'falsy'">{{ result }}</strong>
      </div>
    </div>

    <figcaption class="figure-caption">
      条件表达式会调用对象的真值规则；它不会把字符串内容“解析”为数字或布尔值。
    </figcaption>
  </figure>
</template>
