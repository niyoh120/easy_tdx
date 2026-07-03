<script setup lang="ts">
// 多标的输入（组合回测用）。逐个添加 6 位代码，市场自动识别。
// 删除手动市场选择（沪市/深市/北交所），由 detectMarket 智能匹配。

import { computed, ref } from 'vue'

import { detectMarket, marketLabel } from '../market'

const props = defineProps<{
  modelValue: string[]
}>()
const emit = defineEmits<{ 'update:modelValue': [value: string[]] }>()

const code = ref('')
const detectedMarket = computed(() => (code.value && /^\d{6}$/.test(code.value)
  ? marketLabel(detectMarket(code.value))
  : ''))

function add() {
  if (!/^\d{6}$/.test(code.value)) return
  const sym = `${detectMarket(code.value)}:${code.value}`
  if (!props.modelValue.includes(sym)) {
    emit('update:modelValue', [...props.modelValue, sym])
  }
  code.value = ''
}

function remove(sym: string) {
  emit('update:modelValue', props.modelValue.filter((s) => s !== sym))
}
</script>

<template>
  <div class="stocks-picker">
    <div class="row add-row">
      <input
        v-model="code"
        maxlength="6"
        placeholder="6位代码（市场自动识别）"
        @keyup.enter="add"
      />
      <button @click="add">添加</button>
    </div>
    <p v-if="detectedMarket" class="market-hint">将识别为：{{ detectedMarket }}</p>

    <div v-if="modelValue.length" class="stock-list">
      <span v-for="s in modelValue" :key="s" class="stock-tag">
        {{ s }}
        <button class="remove" @click="remove(s)">×</button>
      </span>
    </div>
    <p v-else class="hint">至少添加 1 只标的</p>
  </div>
</template>

<style scoped>
.add-row {
  display: flex;
  gap: 6px;
}
.add-row input {
  flex: 1;
}
.market-hint {
  color: var(--text-dim);
  font-size: 11px;
  margin-top: 4px;
}
.stock-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}
.stock-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-family: var(--font-mono);
}
.remove {
  border: none;
  background: none;
  color: var(--text-dim);
  padding: 0 2px;
  font-size: 14px;
  line-height: 1;
}
.remove:hover {
  color: var(--up);
}
.hint {
  color: var(--text-dim);
  font-size: 11px;
  margin-top: 8px;
}
</style>
