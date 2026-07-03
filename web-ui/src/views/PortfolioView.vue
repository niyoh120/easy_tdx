<script setup lang="ts">
// 组合回测主页面：左配置（多标的 + 策略 + 日期）/ 右报告（组合净值 + 各标的对比）。

import { onMounted, ref } from 'vue'

import EquityChart from '../components/EquityChart.vue'
import PortfolioCompareChart from '../components/PortfolioCompareChart.vue'
import PortfolioSummaryTable from '../components/PortfolioSummaryTable.vue'
import StocksPicker from '../components/StocksPicker.vue'
import StrategyPicker from '../components/StrategyPicker.vue'
import type { Category, ExecutionMode } from '../types'
import { useBacktestStore } from '../stores/backtest'

const store = useBacktestStore()

const stocks = ref<string[]>(['SZ:000001', 'SH:600519'])
const strategy = ref('ma_cross')
const params = ref<Record<string, number | string | boolean>>({})
const cash = ref(1000000)
const category = ref<Category>('DAY')
const execution = ref<ExecutionMode>('next_open')

// 成交价模式（精简为 开盘价/收盘价）
const EXECUTIONS: { value: ExecutionMode; label: string }[] = [
  { value: 'next_open', label: '开盘价' },
  { value: 'next_close', label: '收盘价' },
]
const CATEGORIES: Category[] = ['DAY', 'WEEK', 'MONTH', 'MIN_5', 'MIN_15', 'MIN_30', 'MIN_60']

// 日期默认（复用单标的逻辑）
function isoDaysFromNow(days: number): string {
  const d = new Date()
  d.setDate(d.getDate() + days)
  return d.toISOString().slice(0, 10)
}
const startDate = ref(isoDaysFromNow(-365 * 3))
const endDate = ref(isoDaysFromNow(0))

onMounted(() => {
  store.loadStrategies().catch((e) => {
    store.error = `加载策略列表失败：${e instanceof Error ? e.message : e}`
  })
})

async function onRun() {
  await store.runPortfolio({
    strategy: strategy.value,
    params: params.value,
    cash: cash.value,
    execution: execution.value,
    stocks: stocks.value,
    category: category.value,
    start_date: startDate.value,
    end_date: endDate.value,
  })
}
</script>

<template>
  <div class="portfolio-view">
    <aside class="config-panel">
      <section class="panel-section">
        <h3>标的列表</h3>
        <StocksPicker v-model="stocks" />
      </section>

      <section class="panel-section">
        <h3>策略</h3>
        <StrategyPicker
          v-if="store.strategies.length"
          v-model:strategy="strategy"
          v-model:params="params"
          :strategies="store.strategies"
        />
        <p v-else class="loading-text">加载策略中…</p>
      </section>

      <section class="panel-section">
        <h3>周期与日期</h3>
        <div class="field">
          <label>周期</label>
          <select v-model="category">
            <option v-for="c in CATEGORIES" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        <div class="row">
          <div class="field">
            <label>开始</label>
            <input v-model="startDate" type="date" />
          </div>
          <div class="field">
            <label>结束</label>
            <input v-model="endDate" type="date" />
          </div>
        </div>
      </section>

      <section class="panel-section">
        <h3>资金</h3>
        <div class="field">
          <label>组合总资金</label>
          <input v-model.number="cash" type="number" min="1000" step="10000" />
        </div>
        <div class="field">
          <label>成交价</label>
          <select v-model="execution">
            <option v-for="e in EXECUTIONS" :key="e.value" :value="e.value">{{ e.label }}</option>
          </select>
        </div>
      </section>

      <button
        class="primary run-btn"
        :disabled="store.portfolioRunning || stocks.length === 0"
        @click="onRun"
      >
        {{ store.portfolioRunning ? '组合回测中…' : '开始组合回测' }}
      </button>
    </aside>

    <main class="report-panel">
      <div v-if="store.error" class="error-banner">⚠ {{ store.error }}</div>

      <div
        v-if="!store.portfolioResult && !store.portfolioRunning && !store.error"
        class="placeholder"
      >
        <p>添加多只标的，选择策略后点击「开始组合回测」</p>
      </div>

      <div v-if="store.portfolioResult" class="report-content">
        <section class="report-section">
          <h3>组合整体绩效</h3>
          <div class="perf-summary">
            <div class="perf-item">
              <span class="label">组合总收益</span>
              <span
                class="value"
                :class="store.portfolioResult.total_performance.total_return > 0 ? 'pos' : 'neg'"
              >
                {{ (store.portfolioResult.total_performance.total_return * 100).toFixed(2) }}%
              </span>
            </div>
            <div class="perf-item">
              <span class="label">标的数量</span>
              <span class="value">{{ store.portfolioResult.total_performance.total_stocks }}</span>
            </div>
            <div class="perf-item">
              <span class="label">组合总资金</span>
              <span class="value">{{ store.portfolioResult.total_performance.total_cash.toFixed(0) }}</span>
            </div>
          </div>
        </section>

        <section class="report-section">
          <h3>组合净值曲线</h3>
          <EquityChart :equity="store.portfolioResult.combined_equity" />
        </section>

        <section class="report-section">
          <h3>各标的绩效对比</h3>
          <PortfolioSummaryTable
            :results="store.portfolioResult.individual_results"
            :allocation="store.portfolioResult.equity_allocation"
          />
        </section>

        <section class="report-section">
          <h3>各标的净值叠加（归一化）</h3>
          <PortfolioCompareChart :results="store.portfolioResult.individual_results" />
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
.portfolio-view {
  display: flex;
  height: 100%;
}
.config-panel {
  width: 320px;
  flex-shrink: 0;
  background: var(--bg-panel);
  border-right: 1px solid var(--border);
  padding: 16px;
  overflow-y: auto;
}
.panel-section {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}
.panel-section:last-of-type {
  border-bottom: none;
}
.panel-section h3 {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 12px;
}
.loading-text {
  color: var(--text-dim);
  font-size: 12px;
}
.run-btn {
  width: 100%;
  padding: 10px;
  font-size: 14px;
}
.report-panel {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}
.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-dim);
}
.error-banner {
  background: rgba(239, 65, 70, 0.12);
  border: 1px solid var(--up);
  color: var(--up);
  padding: 10px 14px;
  border-radius: var(--radius);
  margin-bottom: 16px;
  font-size: 13px;
}
.report-section {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 16px;
  margin-bottom: 16px;
}
.report-section h3 {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 12px;
}
.perf-summary {
  display: flex;
  gap: 32px;
}
.perf-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.perf-item .label {
  font-size: 12px;
  color: var(--text-dim);
}
.perf-item .value {
  font-size: 20px;
  font-weight: 600;
  font-family: var(--font-mono);
}
.pos {
  color: var(--up);
}
.neg {
  color: var(--down);
}
</style>
