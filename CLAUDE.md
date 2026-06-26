# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## 虚拟环境（必须）

本项目所有 Python 命令**必须使用项目根目录下的 venv 虚拟环境**，不要用系统 Python 或其他环境。

```bash
# 激活 venv（Windows / Git Bash）
source venv/Scripts/activate

# 或直接用 venv 的解释器（无需激活）
venv/Scripts/python.exe -m pytest ...
venv/Scripts/python.exe -m mypy src/
venv/Scripts/ruff check src/
venv/Scripts/easy-tdx --help
```

easy-tdx 已在 venv 中以 editable 模式安装（`pip install -e .`），修改 `src/` 后即时生效，无需重装。

## Build / Test / Lint

```bash
# 单元测试（无需网络，使用 tests/fixtures/ 中的 hex 数据）
python -m pytest tests/unit/ -v

# 集成测试（需要网络，默认跳过）
XMTDX_LIVE=1 python -m pytest tests/integration/ -v

# 类型检查（strict mypy）
mypy src/

# lint + format
ruff check src/ tests/
ruff format --check src/ tests/
```

## 架构

```
src/easy_tdx/
├── client.py          # TdxClient / AsyncTdxClient（Windows 通达信协议高层 API）
├── mac/               # macOS 通达信协议（独立命令/编解码/握手）
│   ├── client.py      # MacClient / AsyncMacClient（mac 行情高层 API）
│   ├── commands/      # mac 协议命令（SymbolQuotesCmd / BoardMembersQuotesCmd 等）
│   ├── enums.py       # Category / SortType / FilterType / BoardType / Period / Adjust
│   └── models.py      # MacQuoteField / MacTickChart 等 dataclass
├── ex/                # 扩展行情协议（ExTdx）+ macOS 扩展（MacEx）
│   ├── client.py      # ExTdxClient / AsyncExTdxClient
│   ├── mac_client.py  # MacExClient / AsyncMacExClient（goods_* 系列方法）
│   ├── commands/      # 扩展协议命令
│   └── models.py      # ExMarketInfo / ExInstrumentInfo 等
├── unified.py         # UnifiedTdxClient / AsyncUnifiedTdxClient（聚合 mac + mac_ex 的门面）
├── chanlun/           # 缠论技术分析模块（独立于 transport，纯计算）
│   ├── analyser.py    # ChanlunAnalyser 主入口（接收 DataFrame）
│   ├── types.py       # 数据结构（Kline/CLKline/FX/BI/XD/ZS/MMD/BC）
│   ├── config.py      # ChanlunConfig 配置项
│   ├── kline_merge.py # K线包含处理
│   ├── fractal.py     # 分型识别
│   ├── bi.py          # 笔计算
│   ├── xd.py          # 线段计算
│   ├── zs.py          # 中枢计算
│   ├── zsd.py         # 走势段/趋势段
│   ├── macd.py        # MACD 指标（纯 numpy）
│   ├── mmd.py         # 一二三类买卖点识别
│   ├── beichi.py      # 背驰判断（笔/盘整/趋势）
│   └── multi_level.py # 多级别联立分析
├── transport/
│   ├── sync.py        # TdxConnection（socket）+ ping_host / ping_all / ping_mac_all
│   └── async_.py      # AsyncTdxConnection（asyncio）
├── commands/          # 每条命令：build_request() + parse_response()，无 IO
├── codec/             # price / volume / datetime / frame / financial / bitmap 编解码
├── backtest/          # 回测引擎
│   ├── engine.py      # BacktestEngine（止损/止盈执行/缠论自动桥接）
│   ├── strategy.py    # Strategy 基类（向量化 datetime）
│   ├── orders.py      # OrderSimulator（SL/TP 同 bar 执行）
│   ├── execution.py   # 可插拔执行模型（Immediate/TWAP/VWAP/Limit）
│   ├── slippage.py    # 滑点模型（Fixed/Percent/Volume/Volatility）
│   ├── performance.py # PerformanceAnalyzer（FIFO 真实持仓天数）
│   ├── portfolio.py / portfolio_engine.py # 多标的组合回测
│   ├── combo.py       # 多因子组合回测
│   ├── attribution.py # Brinson / 因子 / 成本归因
│   └── dsl.py         # 策略 DSL 解析
├── portfolio/         # 组合层
│   ├── optimizer.py   # 权重优化（mean_variance 可选 scipy，缺失回退等权）
│   └── ...            # risk / rebalance 等
├── factor/            # 因子分析
│   ├── analysis.py    # FactorAnalyzer（compute_ic 用 spearman，可选 scipy → pip install easy-tdx[science]）
│   ├── engine.py / base.py / transform.py
│   └── builtin/       # 内置因子
├── screen/
│   ├── scanner.py     # SignalScanner（并发扫描/增量缓存）
│   └── ranker.py      # 排序/打分
├── realtime/
│   └── engine.py      # EventBus + RealtimeStrategy（asyncio 事件驱动）
├── offline/           # 离线数据读写（daily_bar / min_bar / gbbq / history_financial 等）
├── indicator.py / MyTT.py  # 技术指标（MyTT 为第三方库移植，命名沿袭惯例）
├── config.py          # 主机/端口/超时配置 + best_host 持久化
├── cli/               # easy-tdx CLI（click）；cmd_chanlun / cmd_backtest / cmd_offline / cmd_factor 等
└── models/            # 纯 dataclass，无业务逻辑
```

四套 client 关系：`client.py`（Windows 标准）、`mac/client.py`（macOS）、`ex/client.py`（扩展）、`ex/mac_client.py`（macOS 扩展）；每套均提供 sync + async 镜像。`unified.py` 是 mac + mac_ex 的门面。commands 层不依赖 transport，可独立单测。修改 codec 或 commands 时不需要网络。

## 协议编解码注意事项

- **价格编码**：变长有符号整数（类 LEB128），bit8=继续，bit7=符号。差分编码（相邻 tick 存 delta）。
- **成交量编码**：4 字节自定义浮点（`_decode_volume`），字节 3=指数，字节 0-2=精度。**不可用于价格字段**。
- **握手**：连接后必须顺序发送 3 条 setup 命令，响应丢弃。
- **帧格式**：16 字节响应头，body 按需 zlib 解压。
- 新增编解码逻辑时务必在 `tests/fixtures/` 中补充 hex fixture 并编写对应的离线解析测试。

## 已知限制

- `Market.BJ` 的 `get_security_list()` 不能稳定获取（服务器端问题），不要尝试依赖它。
- `limit_up` / `limit_down` 在 `SecurityQuote` 中默认为 `None`，涨跌停价应通过 `get_price_limits()` 或 `compute_price_limits()` 计算。

## 代码风格

- ruff: line-length 100, target py310, rules: E/F/I/UP
- mypy strict mode
- 所有 `get_*` 公开方法返回 `pd.DataFrame`（通过 `_df._to_df()` 转换）。内部方法仍使用 dataclass 列表。
- 依赖：pandas（>=2.0）、tzdata（>=2024.1）。

## 缠论（chanlun）模块

独立计算模块，不依赖 transport/commands，仅依赖 pandas（隐含 numpy）。

**计算管道**：`DataFrame → Kline → K线合并 → 分型 → 笔 → 中枢 → 线段 → 买卖点 → 背驰`

**CLI**: `easy-tdx chanlun SZ 000001 --table`

**编程 API**:
```python
from easy_tdx.chanlun import ChanlunAnalyser
analyser = ChanlunAnalyser("SZ000001", "DAILY")
result = analyser.process_klines(df)  # 接收 easy_tdx 的 DataFrame
print(result.to_dict())  # JSON 兼容字典

# 增量追加新 K 线（去重后重新计算，适合实时场景）
result = analyser.append_klines(df_new)
```

**多级别联立**：`MultiLevelAnalyser.query_low_level_qs()` 返回趋势方向、笔重叠、背驰条件等增强字段。

**测试**: `python -m pytest tests/unit/test_chanlun*.py -v`（3 个测试文件共 49 个用例，无需网络）
