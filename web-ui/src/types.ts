// 后端 API 的 TypeScript 类型镜像。
// 与 src/easy_tdx/web/backtest_schemas.py 及 backtest router 的响应保持一致。
// 后端是唯一事实源；这里只做类型契约。

// ── 策略 schema（GET /api/v1/backtest/strategies） ───────────────────────────

export type ParamType = 'int' | 'float' | 'bool' | 'str'

export interface ParamSchema {
  name: string
  type: ParamType
  default: number | string | boolean
  label: string
  min_value?: number
  max_value?: number
  choices?: string[]
  description?: string
}

export interface StrategySchema {
  name: string
  label: string
  description: string
  params: ParamSchema[]
  preset_grid?: Record<string, Array<number | string>>
}

export interface StrategiesResponse {
  strategies: StrategySchema[]
  count: number
}

// ── OHLCV 行情（GET /api/v1/bars） ────────────────────────────────────────────

export interface Bar {
  datetime: string
  open: number
  high: number
  low: number
  close: number
  vol: number
  amount: number
}

export interface DataFrameResponse {
  data: Record<string, unknown>[]
  count: number
}

// ── 回测请求（POST /api/v1/backtest/run） ─────────────────────────────────────

export type ExecutionMode = 'next_open' | 'next_close'
export type Category = 'DAY' | 'WEEK' | 'MONTH' | 'MIN_5' | 'MIN_15' | 'MIN_30' | 'MIN_60'

export interface BacktestRequest {
  strategy: string
  params?: Record<string, number | string | boolean>
  cash?: number
  commission?: number
  min_commission?: number
  stamp_tax?: number
  slippage?: number
  execution?: ExecutionMode
  ohlcv?: Bar[]
  symbol?: string
  category?: Category
  count?: number
}

// ── 回测结果 ──────────────────────────────────────────────────────────────────

export interface Performance {
  total_return: number
  annual_return: number
  max_drawdown: number
  max_dd_duration: number
  sharpe: number
  sortino: number
  calmar: number
  total_trades: number
  win_trades: number
  lose_trades: number
  rejected_trades: number
  win_rate: number
  profit_factor: number
  avg_win: number
  avg_loss: number
  max_win: number
  max_loss: number
  avg_holding_days: number
  volatility: number
}

export interface EquityPoint {
  datetime: string
  cash: number
  position_value: number
  total: number
  drawdown: number
  drawdown_pct: number
}

export interface Trade {
  datetime: string
  direction: 'BUY' | 'SELL'
  size: number
  price: number
  commission: number
  slippage: number
  pnl: number
  rejected: boolean
}

export interface BacktestResult {
  performance: Performance
  equity_curve: EquityPoint[]
  trades: Trade[]
  positions: Record<string, unknown>[]
  config: Record<string, unknown>
}

// ── 后台任务（POST /api/v1/backtest/run/async + GET /tasks/{id}） ─────────────

export interface TaskSubmitResponse {
  task_id: string
  status: 'pending' | 'running'
}

export type TaskStatus = 'pending' | 'running' | 'done' | 'failed'

export interface TaskState {
  task_id: string
  status: TaskStatus
  result: BacktestResult | PortfolioResult | OptimizeResult | OptimizeAllResult | null
  error: string | null
  description: string
  elapsed: number
}

// ── 任务摘要（Phase 5 对比页） ────────────────────────────────────────────────

export interface TaskSummary {
  task_id: string
  status: TaskStatus
  description: string
  created_at: number
  elapsed: number
}

export interface TaskListResponse {
  tasks: TaskSummary[]
  count: number
}

// ── 组合回测（Phase 3） ───────────────────────────────────────────────────────

export interface PortfolioBacktestRequest {
  strategy: string
  params?: Record<string, number | string | boolean>
  cash?: number
  commission?: number
  slippage?: number
  execution?: ExecutionMode
  stocks: string[]
  category?: Category
  start_date?: string
  end_date?: string
}

export interface PortfolioResult {
  total_performance: {
    total_return: number
    annual_return: number
    total_stocks: number
    total_cash: number
  }
  individual_results: Record<string, BacktestResult>
  equity_allocation: Record<string, number>
  combined_equity: EquityPoint[]
}

// ── 参数网格寻优（Phase 4） ──────────────────────────────────────────────────

export interface OptimizeBacktestRequest {
  strategy: string
  cash?: number
  commission?: number
  slippage?: number
  execution?: ExecutionMode
  param_grid: Record<string, Array<number | string>>
  ohlcv?: Bar[]
  symbol?: string
  category?: Category
  count?: number
  start_date?: string
  end_date?: string
}

export interface GridPointResult {
  params: Record<string, number | string>
  total_return: number | null
  sharpe: number | null
  max_drawdown: number | null
  total_trades: number
  win_rate: number | null
  profit_factor: number | null
}

export interface OptimizeHeatmap {
  x_name: string
  y_name: string
  x: Array<number | string>
  y: Array<number | string>
  data: Array<[number, number, number | null]>
}

export interface OptimizeResult {
  strategy: string
  param_names: string[]
  results: GridPointResult[]
  best: GridPointResult | null
  heatmap: OptimizeHeatmap | null
}

// ── 一键寻优所有策略（Phase 6） ──────────────────────────────────────────────

export interface OptimizeAllBacktestRequest {
  cash?: number
  commission?: number
  slippage?: number
  execution?: ExecutionMode
  ohlcv?: Bar[]
  symbol?: string
  category?: Category
  count?: number
  start_date?: string
  end_date?: string
}

export interface OptimizeAllRankEntry {
  strategy: string
  strategy_label: string
  params: Record<string, number | string>
  total_return: number | null
  sharpe: number | null
  max_drawdown: number | null
  total_trades: number
  win_rate: number | null
  profit_factor: number | null
  grid_points: number
}

export interface OptimizeAllResult {
  ranking: OptimizeAllRankEntry[]
  best: OptimizeAllRankEntry | null
  per_strategy: Record<string, OptimizeAllRankEntry>
  total_grid_points: number
}

// ── 错误响应（后端 ApiErrorResponse） ─────────────────────────────────────────

export interface ApiError {
  error: string
  detail: string
}
