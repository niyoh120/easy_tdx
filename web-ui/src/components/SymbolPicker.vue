<script setup lang="ts">
// 选标的 + 配置日期范围（取行情由父组件在「开始回测/开始寻优」时触发）。
// 市场按 6 位代码智能识别，不再手动选择。
// 后端 /bars 仅支持 count（上限 800，约 3.2 年），固定拉满后前端按日期过滤。
// 默认：结束日=今天（最近交易日），开始日=3年前。

import { computed, ref } from 'vue'

import { fetchBars, formatError } from '../api'
import { detectMarket, marketLabel } from '../market'
import { useBacktestStore } from '../stores/backtest'
import type { Category } from '../types'

const store = useBacktestStore()

const code = ref('000001')
const category = ref<Category>('DAY')

// 日期默认：结束=今天，开始=3年前
function isoDaysFromNow(days: number): string {
  const d = new Date()
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}
const endDate = ref(isoDaysFromNow(0))
const startDate = ref(isoDaysFromNow(-365 * 3))

const error = ref('')
// loading 由父组件控制（回测/寻优时驱动），组件自身只暴露 loadBars
const loading = ref(false)

const CATEGORIES: Category[] = ['DAY', 'WEEK', 'MONTH', 'MIN_5', 'MIN_15', 'MIN_30', 'MIN_60']

// 智能识别的市场（用于提示展示）
const detectedMarket = computed(() => (code.value && /^\d{6}$/.test(code.value)
  ? marketLabel(detectMarket(code.value))
  : ''))

/** 取行情（由父组件在点击「开始回测/开始寻优」时调用）。
 * 成功返回 true，失败返回 false（并把错误写入 store.error 供父组件感知）。 */
async function loadBars(): Promise<boolean> {
  // 基本校验
  if (!/^\d{6}$/.test(code.value)) {
    error.value = '股票代码必须是 6 位数字'
    store.error = error.value
    return false
  }
  if (startDate.value >= endDate.value) {
    error.value = '开始日期必须早于结束日期'
    store.error = error.value
    return false
  }

  loading.value = true
  error.value = ''
  try {
    const market = detectMarket(code.value)
    const bars = await fetchBars(
      market,
      code.value,
      category.value,
      startDate.value,
      endDate.value,
    )
    if (bars.length < 2) {
      error.value = `该日期范围内仅取到 ${bars.length} 根 K 线，不足以回测`
      store.error = error.value
      return false
    }
    const range = `${startDate.value} ~ ${endDate.value}`
    store.setOhlcv(bars, `${market}:${code.value} ${category.value} ${range}`)
    store.clearResult()
    return true
  } catch (e) {
    error.value = formatError(e)
    store.error = error.value
    return false
  } finally {
    loading.value = false
  }
}

// 暴露给父组件（BacktestView / OptimizeView）在「开始回测/寻优」时串联调用
defineExpose({ loadBars, loading })
</script>

<template>
  <div class="symbol-picker">
    <div class="field code-field">
      <label>代码</label>
      <input
        v-model="code"
        maxlength="6"
        placeholder="6位代码（市场自动识别）"
      />
      <span v-if="detectedMarket" class="market-tag">{{ detectedMarket }}</span>
    </div>

    <div class="field">
      <label>周期</label>
      <select v-model="category">
        <option v-for="c in CATEGORIES" :key="c" :value="c">{{ c }}</option>
      </select>
    </div>

    <div class="row">
      <div class="field">
        <label>开始日期</label>
        <input v-model="startDate" type="date" />
      </div>
      <div class="field">
        <label>结束日期</label>
        <input v-model="endDate" type="date" />
      </div>
    </div>

    <p v-if="error" class="err">{{ error }}</p>
    <p v-if="store.barsSource" class="ok">
      已加载：{{ store.barsSource }}（{{ store.ohlcv.length }} 根）
    </p>
  </div>
</template>

<style scoped>
.code-field {
  position: relative;
}
.code-field input {
  padding-right: 70px;
}
.market-tag {
  position: absolute;
  right: 8px;
  bottom: 8px;
  font-size: 11px;
  color: var(--text-dim);
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  padding: 1px 6px;
  border-radius: 3px;
}
.err {
  color: var(--up);
  font-size: 12px;
  margin-top: 8px;
}
.ok {
  color: var(--down);
  font-size: 12px;
  margin-top: 8px;
}
</style>
