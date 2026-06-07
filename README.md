# easy-tdx

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/easy-tdx.svg)](https://pypi.org/project/easy-tdx/)

量化机构花钱买的毫秒级行情通道，散户连一根日线都要手动截图。

这个项目想打破这件事。

easy-tdx 是一个完全免费、无需注册、无需 API Key 的开源行情数据工具。一行命令拿到 A 股、港股、美股、期货的 K 线、报价、资金流向、板块数据。32 个技术指标开箱即用，缠论分析（笔、中枢、买卖点、背驰）内置计算。装上就能跑，Python 代码和命令行双通道，输出的 JSON 天然喂给 AI Agent——Claude Code、OpenClaw、Hermes 直接用。

不需要你会写量化框架，不需要你懂 TCP 协议，不需要你给任何平台付一分钱。`pip install easy-tdx`，30 秒后你手里的数据和机构看到的是同一份。

做这个项目的出发点很简单：金融数据的获取门槛不该是散户亏钱的原因。当量化基金用程序化交易收割市场的时候，普通人至少应该有权利用同样的数据做自己的判断。这不是一个帮你赚钱的工具，这是一个让你不再裸奔的工具。

MIT 协议，代码全开源，随便用，随便改，随便分发。

## 安装

```bash
pip install easy-tdx
```

安装后自动注册 `easy-tdx` CLI 命令：

```bash
easy-tdx --help
```

开发模式：

```bash
pip install -e ".[dev]"
```

## CLI 参考

`easy-tdx` 默认输出 JSON（一行一条记录），`--table` 切换表格，`--output csv` 输出 CSV。

### 基础

```bash
easy-tdx ping                    # 服务器测速
easy-tdx version                 # 版本号
```

### 行情

```bash
# K 线
easy-tdx kline SZ 000001 --count 30 --table
easy-tdx kline SH 600519 --period 5MIN --adjust QFQ

# 实时报价
easy-tdx quote "SZ 000001,SH 600519" --table

# 市场分类报价（按涨幅排序）
easy-tdx quote-list A --count 20 --table
easy-tdx quote-list KCB --sort TOTAL_AMOUNT --order ASC
easy-tdx quote-list CYB --count 50
```

### 分时 / 成交

```bash
easy-tdx tick SZ 000001 --table
easy-tdx tick SH 600519 --days 5
easy-tdx tick SZ 000001 --date 20250115

easy-tdx transaction SZ 000001 --count 100 --table
easy-tdx transaction SH 600519 --date 20250115
```

### 板块

```bash
easy-tdx board-list --type GN --table
easy-tdx board-list --type HY --count 200
easy-tdx board-members 881001 --table
easy-tdx belong-board SZ 000001 --table
easy-tdx board-summary 881001 --table          # 板块汇总（成交额/主力净流入/涨跌家数）
easy-tdx board-summary 881001 --members --table # 含成分股明细
easy-tdx board-ranking --type HY --top 10 --table   # 行业板块排行
easy-tdx board-ranking --type GN --sort-by amount    # 概念板块按成交额排行
```

### 资金 / 监控

```bash
easy-tdx capital-flow SH 600519 --table
easy-tdx auction SZ 000001 --table
easy-tdx unusual SH --count 100 --table
easy-tdx market-stat --table
easy-tdx server-info --table
easy-tdx symbol-info SZ 000001 --table
```

### 技术指标

```bash
easy-tdx indicator-list --table                       # 列出所有可用指标
easy-tdx indicator MACD -m SH -c 600519 --table       # MACD
easy-tdx indicator KDJ -m SZ -c 000001 --table        # KDJ
easy-tdx indicator RSI -m SH -c 600519 --table        # RSI
easy-tdx indicator BOLL -m SH -c 600519 --table       # BOLL 布林带
easy-tdx indicator DMI -m SH -c 600519 --table        # DMI 动向指标
easy-tdx indicator ATR -m SH -c 600519 --table        # ATR 真实波幅
easy-tdx indicator WR -m SH -c 600519 --table         # WR 威廉指标
easy-tdx indicator CCI -m SH -c 600519 --table        # CCI 顺势指标
easy-tdx indicator BIAS -m SZ -c 000001 --table       # BIAS 乖离率
easy-tdx indicator BIAS_SIGNAL -m SH -c 600519 --table # 30日乖离率信号
easy-tdx indicator OBV -m SZ -c 000001 --table        # OBV 能量潮

# 多指标同时计算
easy-tdx indicator MACD,KDJ,RSI,BOLL -m SH -c 600519 --count 10 --table

# 自定义参数
easy-tdx indicator MACD -m SH -c 600519 --params SHORT=10,LONG=22

# 分钟线指标
easy-tdx indicator MACD -m SH -c 600519 --period 5MIN --count 50

# 仅输出指标值（不含 OHLCV）
easy-tdx indicator RSI -m SZ -c 000001 --no-ohlcv
```

### 缠论分析

基于缠论理论的技术分析，计算管道：`K 线合并 → 分型识别 → 笔 → 中枢 → 线段 → 买卖点 → 背驰`。默认输出 JSON，加 `--table` 输出可读表格。

```bash
easy-tdx chanlun SZ 000001 --table
easy-tdx chanlun SH 600519 --adjust QFQ --table
easy-tdx chanlun SZ 000001 --period 30MIN
```

#### 输出示例

以 `easy-tdx chanlun SH 601088 --table` 为例，输出分五个部分：

**概要统计**

```
标的: 601088  周期: DAILY
原始K线: 800  缠论K线: 589
分型: 275  笔: 131  中枢: 21  线段: 40
买卖点: 125  背驰: 73
```

| 字段 | 含义 |
|------|------|
| 原始 K 线 | 从服务端获取的原始 K 线条数 |
| 缠论 K 线 | 经过包含处理（合并）后的 K 线条数，数量一定 ≤ 原始 K 线 |
| 分型 | 识别出的顶分型 + 底分型总数 |
| 笔 | 相邻两个异向分型之间的连线（涨跌方向交替） |
| 中枢 | 至少 3 笔重叠区域形成的密集成交区间 |
| 线段 | 由笔构成的更大级别走势单位 |
| 买卖点 | 一二三类买卖点信号总数 |
| 背驰 | 力度衰减信号总数（笔背驰 / 盘整背驰 / 趋势背驰） |

**笔**

```
[0] ↑ 2023-02-17 → 2023-02-23 h=28.46 l=26.76 ✓
[1] ↓ 2023-02-23 → 2023-02-28 h=28.46 l=27.8 ✓
[2] ↑ 2023-02-28 → 2023-03-09 h=29.77 l=27.8 ✓
```

笔是缠论的基本走势单位。每条笔连接一个顶分型和一个底分型，方向严格交替（↑↓↑↓…）。`✓` 表示已确认（后续出现了反向笔），`…` 表示仍在进行中。

- `↑`：向上笔，起点是底分型（低点），终点是顶分型（高点）
- `↓`：向下笔，起点是顶分型（高点），终点是底分型（低点）
- `h`/`l`：该笔范围内的最高价 / 最低价

**中枢**

```
[0] zg=28.46 zd=28.11 gg=32.56 dd=26.76 lines=11 ✓
[1] zg=31.2  zd=30.45 gg=32.56 dd=27.9  lines=3  ✓
```

中枢是至少 3 笔重叠形成的密集成交区间，代表多空博弈的平衡区域。`✓` 表示已脱离，`…` 表示价格仍在中枢区间内震荡。

| 字段 | 含义 |
|------|------|
| `zg` | 中枢上沿（区间内最高的低点）— 支撑/压力的关键分界 |
| `zd` | 中枢下沿（区间内最低的高点） |
| `gg` | 中枢区间内的最高价 |
| `dd` | 中枢区间内的最低价 |
| `lines` | 构成该中枢的笔数，笔数越多代表震荡越充分 |

中枢的意义：价格在中枢内震荡 → 突破中枢上沿看涨，跌破下沿看跌。`zg`/`zd` 是实战中最常用的参考价位。

**线段**

```
[0] ↑ 2023-02-17 → 2023-03-09 h=29.77 l=26.76
[1] ↓ 2023-02-28 → 2023-03-29 h=29.77 l=27.18
```

线段是比笔更大的走势单位，由多笔重叠组合而成。线段的方向不严格交替，可能出现连续同向（如连续多段向上），代表更高一级的趋势方向。实战中通常在线段级别判断大方向，在笔级别找买卖点。

**买卖点**

```
1buy:  中枢下方力度衰减，一类买点 (l=27.30 < zd=46.72)
2buy:  回调不创新低，二类买点 (l=27.33)
3buy:  回调不破中枢上沿，三类买点 (l=27.80 > zg=27.58)
1sell: 中枢上方力度衰减，一类卖点 (h=50.38 > zg=46.97)
2sell: 反弹不创新高，二类卖点 (h=29.32)
3sell: 反弹不破中枢下沿，三类卖点 (h=28.46 < zd=46.72)
```

缠论定义三类买点和三类卖点：

| 类型 | 买点含义 | 卖点含义 |
|------|----------|----------|
| 一类 | 下跌趋势末端，力度衰减后的第一个低点（抄底） | 上涨趋势末端，力度衰减后的第一个高点（逃顶） |
| 二类 | 一类买点后的回调不创新低（确认反转） | 一类卖点后的反弹不创新高（确认反转） |
| 三类 | 回调不进入中枢上沿（趋势确认，中枢上方买） | 反弹不进入中枢下沿（趋势确认，中枢下方卖） |

括号内的条件是该信号的触发依据，如 `l=27.80 > zg=27.58` 表示回调低点 27.80 高于中枢上沿 27.58，所以是三类买点。

**背驰**

```
[✓] bi: 笔背驰: 笔[4] 力度=1.32 < 笔[2] 力度=1.97
[✓] pz: 盘整背驰: 中枢[11] 内末笔力度=2.49 < 首笔力度=6.64
[✓] qs: 趋势背驰(上): 中枢[1] 离开力度=3.32 < 中枢[0] 离开力度=4.45
```

背驰是力度衰减信号，表明当前走势动力正在减弱，可能即将反转。力度通过 MACD 面积计算，数值越小力度越弱。

| 类型 | 含义 |
|------|------|
| `bi`（笔背驰） | 同向相邻两笔比较，后一笔力度 < 前一笔 → 该方向动力减弱 |
| `pz`（盘整背驰） | 同一中枢内，末笔力度 < 首笔 → 中枢内动力衰减，即将突破 |
| `qs`（趋势背驰） | 两个同向中枢之间比较，后一中枢离开力度 < 前一中枢 → 趋势可能终结 |

`[✓]` 表示确认背驰。趋势背驰(上)代表上涨趋势可能结束，趋势背驰(下)代表下跌趋势可能结束。

### 捉妖大师（重点）

捉妖大师是多周期涨幅共振指标，通过 20/60/120 日涨幅及指数平滑判断短中长线趋势是否同向，用于筛选趋势刚启动的强势股。

```bash
easy-tdx indicator ZHUOYAO -m SH -c 600519 --count 30 --table

# 自定义周期参数
easy-tdx indicator ZHUOYAO -m SZ -c 000001 --params N1=90,N2=45,N3=15

# 结合其他指标一起看
easy-tdx indicator ZHUOYAO,MACD,KDJ -m SH -c 600519 --count 20 --table
```

输出列说明：

| 列名 | 含义 |
|------|------|
| `ZY_LONG` | 长线 — 120 日涨幅的 10 日指数平滑 |
| `ZY_MID` | 中线 — 60 日涨幅(%) |
| `ZY_SHORT` | 短线 — 20 日涨幅(%) |
| `ZY_TREND` | 趋势 — 中线的 10 日指数平滑 |

**核心信号：** 四线全部 > 0 且短线 > 中线 > 长线 = 短中长趋势完全一致向上，是强势股特征。详见 [捉妖大师指标详解](docs/indicator-zhuoyao.md)。

### 30日乖离率信号（重点）

30日乖离率信号指标，在标准乖离率（BIAS）基础上叠加短/长信号线，通过三者位置关系判断趋势方向和转折点。源自通达信经典指标。

```bash
easy-tdx indicator BIAS_SIGNAL -m SH -c 600519 --count 60 --table

# 自定义周期参数
easy-tdx indicator BIAS_SIGNAL -m SZ -c 000001 --params P=5,M=20

# 结合其他指标一起看
easy-tdx indicator BIAS_SIGNAL,MACD,KDJ -m SH -c 600519 --count 30 --table
```

输出列说明：

| 列名 | 含义 |
|------|------|
| `BS_X` | M日乖离率 — 当前价格偏离30日均线的百分比 |
| `BS_SMA` | 短周期信号线 — 乖离率的 P 日均线，过滤短期噪音 |
| `BS_LMA` | 长周期信号线 — 乖离率的 M 日均线，捕捉中期趋势方向 |

**核心信号：** X > S_SMA 且 X_LMA 上升 = 多头确认（通达信红色）；S_SMA > X 或 X_LMA 下降 = 空头预警（通达信绿色）。多空判断非对称设计——多头需两个条件同时满足，空头只需其一，偏向保守预警。详见 [30日乖离率信号指标详解](docs/indicator-bias-signal.md)。

```python
# Python API 用法
from easy_tdx import MacClient, Market

with MacClient.from_best_host() as c:
    df = c.get_stock_kline_with_indicators(
        Market.SH, "600519",
        indicators=["BIAS_SIGNAL"],
        count=60,
    )
    # df 包含: datetime, open, close, high, low, vol, amount
    #         + BS_X, BS_SMA, BS_LMA
```

支持 32 个指标：MACD, KDJ, RSI, BOLL, DMI, ATR, WR, CCI, BIAS, BIAS_SIGNAL, OBV, VR, EMV, MFI, BRAR, ASI, TRIX, DPO, MTM, ROC, EXPMA, BBI, PSY, DFMA, CR, KTN, XSII, MASS, TAQ, ZHUOYAO。

```python
# Python API 用法
from easy_tdx import MacClient, Market

with MacClient.from_best_host() as c:
    df = c.get_stock_kline_with_indicators(
        Market.SH, "600519",
        indicators=["ZHUOYAO"],
        count=30,
    )
    # df 包含: datetime, open, close, high, low, vol, amount
    #         + ZY_LONG, ZY_MID, ZY_SHORT, ZY_TREND
```

支持 32 个指标：MACD, KDJ, RSI, BOLL, DMI, ATR, WR, CCI, BIAS, BIAS_SIGNAL, OBV, VR, EMV, MFI, BRAR, ASI, TRIX, DPO, MTM, ROC, EXPMA, BBI, PSY, DFMA, CR, KTN, XSII, MASS, TAQ, ZHUOYAO。

### 财务

```bash
easy-tdx f10 SH 600519              # F10 公司信息
easy-tdx fund-flow SH 600519        # 历史资金流向
```

### 扩展市场（港股/美股/期货）

```bash
easy-tdx ex markets                                       # 列出可用市场
easy-tdx ex kline HK_MAIN_BOARD 00700 --count 30 --table  # 港股 K 线
easy-tdx ex kline US_STOCK AAPL --table                    # 美股 K 线
easy-tdx ex quote US_STOCK TSLA --table                    # 美股报价
easy-tdx ex quote-list HK_MAIN_BOARD --table               # 港股商品列表
easy-tdx ex tick HK_MAIN_BOARD 00700 --table               # 港股分时
```

### 离线数据（读取 + 写入同步）

从本地通达信安装目录直接读取数据文件，无需网络连接：

```bash
easy-tdx offline home                                # 检测通达信安装目录
easy-tdx offline daily SH 600000 --count 10 --table  # A 股日线
easy-tdx offline min SZ 000001 --type lc5 --table    # 分钟线（5min/lc1/lc5）
easy-tdx offline ex-files --table                    # 列出扩展市场可用文件
easy-tdx offline ex-daily 38#2_CPI --count 5 --table # 扩展市场日线（期货/港股/外盘）
easy-tdx offline gbbq C:\new_jyplug\T0002\hq_cache\gbbq --table        # 股本变迁
easy-tdx offline financial C:\new_jyplug\vipdoc\fin\gpcw20260331.dat    # 历史财务
easy-tdx offline blocks C:\new_jyplug\T0002\blocknew --table            # 自定义板块
```

从服务端获取最新日线并写入本地 .day 文件，替代通达信内置下载功能：

```bash
# 同步单只股票日线（自动增量/全量）
easy-tdx offline sync-daily SZ 000001
easy-tdx offline sync-daily SH 600519 --vipdoc C:\new_jyplug\vipdoc

# 一键同步沪深全市场（每天一条命令）
easy-tdx offline sync-all
```

> 建议在通达信关闭时执行 sync 命令，避免文件被锁定。空文件自动全量下载，已有数据只做增量追加。

## CLI 命令汇总

| 命令 | 说明 |
|------|------|
| `ping` | 服务器延迟测速 |
| `version` | 版本号 |
| `kline` | K 线（日/周/月/分钟，支持复权） |
| `quote` | 实时报价（单只/批量） |
| `quote-list` | 市场分类排序报价（A/SH/SZ/KCB/CYB） |
| `tick` | 分时图（单日/多日/历史） |
| `transaction` | 逐笔成交 |
| `board-list` | 板块列表（行业/概念/风格） |
| `board-members` | 板块成分股报价 |
| `board-summary` | 板块汇总（成交额、主力净流入、涨跌家数） |
| `board-ranking` | 板块涨跌幅排行榜（行业/概念排行） |
| `belong-board` | 个股所属板块 |
| `capital-flow` | 资金流向 |
| `auction` | 集合竞价 |
| `unusual` | 市场异动 |
| `market-stat` | 全市场涨跌统计 |
| `server-info` | 服务器交易时段 |
| `symbol-info` | 个股特征快照 |
| `indicator` | 技术指标计算（32 个：MACD/KDJ/RSI/BOLL/DMI/ATR...） |
| `indicator-list` | 列出可用技术指标 |
| `f10` | F10 公司信息 |
| `fund-flow` | 历史资金流向 |
| `ex kline` | 扩展市场 K 线 |
| `ex quote` | 扩展市场报价 |
| `ex quote-list` | 扩展市场商品列表 |
| `ex tick` | 扩展市场分时 |
| `ex markets` | 列出可用扩展市场 |
| `offline home` | 检测通达信安装目录 |
| `offline daily` | A 股日线（本地 .day 文件） |
| `offline sync-daily` | 从服务端同步单只股票日线到本地 .day 文件 |
| `offline sync-all` | 一键同步沪深全市场日线（扫描本地 .day 文件） |
| `offline min` | 分钟线（本地 .5/.lc1/.lc5 文件） |
| `offline ex-files` | 列出扩展市场可用文件 |
| `offline ex-daily` | 扩展市场日线（期货/港股/外盘） |
| `offline gbbq` | 股本变迁数据 |
| `offline financial` | 历史财务数据 |
| `offline blocks` | 自定义板块数据 |

## Python API

### 连接管理

所有客户端支持 `from_best_host()` 自动选最低延迟服务器：

```python
from easy_tdx import MacClient

with MacClient.from_best_host() as c:
    df = c.get_stock_kline(...)
```

| 客户端 | 端口 | 覆盖范围 |
|--------|------|----------|
| `MacClient` / `AsyncMacClient` | 7709 | A 股行情（MAC 协议，推荐） |
| `MacExClient` / `AsyncMacExClient` | 7727 | 港股/美股/期货（MAC 协议） |
| `UnifiedTdxClient` / `AsyncUnifiedTdxClient` | 自动 | A 股 + 扩展市场统一入口 |
| `TdxClient` / `AsyncTdxClient` | 7709 | A 股行情（标准协议） |

### MAC 协议（推荐）

#### 报价

```python
from easy_tdx import MacClient, Market, Category, SortType, SortOrder

with MacClient.from_best_host() as c:
    # 批量报价（最多 80 只/次）
    df = c.get_stock_quotes([(Market.SH, "600519"), (Market.SZ, "000858")])

    # 市场分类排序报价
    df = c.get_stock_quotes_list(
        Category.A, count=20,
        sort_type=SortType.CHANGE_PCT,
        sort_order=SortOrder.DESC,
    )
```

返回列：`market, code, name` + 动态字段（`pre_close, open, high, low, close, vol, amount, turnover, vol_ratio` 等）。

#### K 线（支持复权）

```python
from easy_tdx import MacClient, Market, Period, Adjust

with MacClient.from_best_host() as c:
    # 日K前复权
    df = c.get_stock_kline(Market.SH, "600519", Period.DAILY, count=10, adjust=Adjust.QFQ)
    # 5分钟线
    df = c.get_stock_kline(Market.SZ, "000001", Period.MIN_5, count=100)
```

返回列：`datetime, open, close, high, low, vol, amount`。

#### 技术指标

自动获取 200+ 条历史数据预热 EMA，返回最后 `count` 条带指标的结果：

```python
from easy_tdx import MacClient, Market, Period, Adjust
from easy_tdx.indicator import compute_indicators, list_indicators

with MacClient.from_best_host() as c:
    # 便捷方法：获取 K 线 + 计算指标一步完成（默认前复权）
    df = c.get_stock_kline_with_indicators(
        Market.SH, "600519",
        indicators=["MACD", "KDJ", "RSI", "BOLL"],
        count=30,
    )
    # df 包含: datetime, open, close, high, low, vol, amount
    #         + MACD_DIF, MACD_DEA, MACD_HIST, KDJ_K, KDJ_D, KDJ_J, RSI,
    #           BOLL_UPPER, BOLL_MID, BOLL_LOWER

    # 自定义指标参数
    df = c.get_stock_kline_with_indicators(
        Market.SH, "600519",
        indicators=["MACD"],
        params={"MACD": {"SHORT": 10, "LONG": 22}},
    )

    # 独立使用：对已有 DataFrame 计算指标
    raw = c.get_stock_kline(Market.SH, "600519", Period.DAILY, count=200, adjust=Adjust.QFQ)
    result = compute_indicators(raw, ["ATR", "CCI", "WR"], tail=30)

    # 查看所有可用指标
    for info in list_indicators():
        print(info["name"], info["description"], info["outputs"])
```

支持 31 个技术指标：

| 指标 | 输入 | 输出列 |
|------|------|--------|
| MACD | close | MACD_DIF, MACD_DEA, MACD_HIST |
| KDJ | close, high, low | KDJ_K, KDJ_D, KDJ_J |
| RSI | close | RSI |
| BOLL | close | BOLL_UPPER, BOLL_MID, BOLL_LOWER |
| DMI | close, high, low | DMI_PDI, DMI_MDI, DMI_ADX, DMI_ADXR |
| ATR | close, high, low | ATR |
| WR | close, high, low | WR1, WR2 |
| CCI | close, high, low | CCI |
| BIAS | close | BIAS1, BIAS2, BIAS3 |
| OBV | close, vol | OBV |
| VR | close, vol | VR |
| EMV | high, low, vol | EMV, EMV_MA |
| MFI | close, high, low, vol | MFI |
| BRAR | open, close, high, low | AR, BR |
| ASI | open, close, high, low | ASI, ASI_MA |
| TRIX | close | TRIX, TRIX_MA |
| DPO | close | DPO, DPO_MA |
| MTM | close | MTM, MTM_MA |
| ROC | close | ROC, ROC_MA |
| EXPMA | close | EXPMA_12, EXPMA_50 |
| BBI | close | BBI |
| PSY | close | PSY, PSY_MA |
| DFMA | close | DFMA_DIF, DFMA_DMA |
| CR | close, high, low | CR |
| KTN | close, high, low | KTN_UPPER, KTN_MID, KTN_LOWER |
| XSII | close, high, low | XSII_TD1, XSII_TD2, XSII_TD3, XSII_TD4 |
| MASS | high, low | MASS, MASS_MA |
| TAQ | high, low | TAQ_UP, TAQ_MID, TAQ_DOWN |
| ZHUOYAO | close | ZY_LONG, ZY_MID, ZY_SHORT, ZY_TREND |
| BIAS_SIGNAL | close | BS_X, BS_SMA, BS_LMA |

#### 分时

```python
with MacClient.from_best_host() as c:
    df = c.get_tick_chart(Market.SH, "600519")          # 单日分时
    df = c.get_tick_charts(Market.SH, "600519", days=3)  # 多日分时（最多5天）
    df = c.get_chart_sampling(Market.SH, "600519")       # 240点缩略采样
```

#### 逐笔成交

```python
with MacClient.from_best_host() as c:
    df = c.get_transactions(Market.SH, "600519", count=100)
    df = c.get_transactions(Market.SH, "600519", count=100, date=20250115)
```

#### 板块

```python
from easy_tdx import BoardType

with MacClient.from_best_host() as c:
    df = c.get_board_list(BoardType.GN)                       # 概念板块
    df = c.get_board_members("881001", sort_type=SortType.CHANGE_PCT)
    df = c.get_belong_board(Market.SZ, "000001")              # 个股所属板块

    # 板块汇总：成交额、主力净流入、涨跌家数
    summary = c.get_board_summary("881001")
    # summary = {
    #     "member_count": 82,
    #     "amount": 5823456000.0,        # 板块总成交额（元）
    #     "vol": 412356789,              # 板块总成交量（股）
    #     "main_net_amount": -123456.0,  # 当日主力净流入
    #     "main_net_3d": -567890.0,      # 近3日主力净流入
    #     "main_net_5d": -234567.0,      # 近5日主力净流入
    #     "up_count": 45,
    #     "down_count": 37,
    #     "members": DataFrame(...),     # 成分股明细
    # }

    # 板块涨跌幅排行榜
    df = c.get_board_ranking(BoardType.HY, top_n=10, sort_by="change_pct")
    df = c.get_board_ranking(BoardType.GN, top_n=20, sort_by="main_net_amount")
    # 返回列：code, name, change_pct, amount, vol, main_net_amount, up_count, down_count, member_count
```

#### 资金流向

```python
with MacClient.from_best_host() as c:
    df = c.get_capital_flow(Market.SH, "600519")
```

返回列：`date, main_in, main_out, main_net, small_in/out/net, mid_in/out/net, large_in/out/net`。

#### 监控

```python
with MacClient.from_best_host() as c:
    df = c.get_auction(Market.SH, "600519")     # 集合竞价
    df = c.get_unusual(Market.SH)               # 市场异动
    df = c.get_symbol_info(Market.SZ, "000001") # 个股特征快照
    df = c.get_server_info()                     # 服务器交易时段
```

### 扩展市场

```python
from easy_tdx import MacExClient, ExMarket, Period

with MacExClient.from_best_host() as c:
    count = c.goods_count(ExMarket.HK_MAIN_BOARD)
    df = c.goods_list(ExMarket.HK_MAIN_BOARD, start=0, count=50)
    df = c.goods_kline(ExMarket.US_STOCK, "AAPL", Period.DAILY, count=10)
    df = c.goods_quotes([(ExMarket.HK_MAIN_BOARD, "00700")])
    df = c.goods_tick_chart(ExMarket.HK_MAIN_BOARD, "00700")
    df = c.goods_transaction(ExMarket.HK_MAIN_BOARD, "00700", count=100)
```

### 统一客户端

```python
from easy_tdx import UnifiedTdxClient, ExMarket, Market, Period

with UnifiedTdxClient() as client:
    # A 股 -- 自动路由到 MacClient
    df = client.get_stock_kline(Market.SH, "600519", Period.DAILY, count=5)
    df = client.get_stock_quotes([(Market.SH, "600519")])
    df = client.get_board_list()

    # 扩展市场 -- 自动路由到 MacExClient
    df = client.goods_kline(ExMarket.HK_MAIN_BOARD, "00700", Period.DAILY, count=5)
```

### 标准协议

```python
from easy_tdx import TdxClient, Market, KlineCategory

with TdxClient.from_best_host() as c:
    count = c.get_security_count(Market.SH)
    stocks = c.get_security_list(Market.SH, start=0)
    quotes = c.get_security_quotes([(Market.SH, "600000"), (Market.SZ, "000001")])
    bars = c.get_security_bars(Market.SZ, "002176", KlineCategory.DAY, 0, 100)
    minute = c.get_minute_time_data(Market.SH, "600000")
    trades = c.get_transaction_data(Market.SH, "600000", 0, 20)
    flow = c.get_fund_flow(Market.SH, "600519")
    blocks = c.get_block_info("block_gn.dat")
    xdxr = c.get_xdxr_info(Market.SH, "600519")
    stat = c.get_market_stat()
```

`AsyncTdxClient` 提供对应的 `async def` 方法，接口一一对应。

### SecurityQuote 字段说明

`get_security_quotes()` 返回的 DataFrame 包含以下特殊字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `trading_status` | int | 交易状态标志。`0x8020`(32800) = 停牌，其余值表示正常交易或集合竞价 |
| `open_amount` | float | 集合竞价成交金额（元）。仅个股有效，指数该字段无意义 |
| `server_time` | str | 服务器时间，格式 `HH:MM:SS.mmm` |
| `unknown_2` | int | 指数: 集合竞价成交金额/100；个股: 舍入残差≈0 |
| `unknown_3` | int | 个股: 集合竞价成交金额/100；指数: 负值/无意义 |
| `unknown_5-8` | int | 保留字段，恒为 0 |

检测停牌：

```python
df = c.get_security_quotes([(Market.SH, "600000")])
is_suspended = df.iloc[0]["trading_status"] == 0x8020
```

### 离线数据读取

无需网络，从本地通达信安装目录直接读取：

```python
from easy_tdx.offline import detect_tdx_home, read_daily_bars, find_daily_bar_file
from easy_tdx import Market

home = detect_tdx_home()
filepath = find_daily_bar_file(Market.SH, "600000")
bars = read_daily_bars(filepath)
```

支持：日线、分钟线、扩展市场日线、板块、股本变迁、历史财务数据。

### 离线数据写入同步

从服务端获取最新数据并追加写入本地通达信数据文件：

```python
from easy_tdx.offline import (
    encode_daily_bar, append_daily_bars, get_last_bar_date,
    encode_5min_bar, append_5min_bars,
    encode_lc_min_bar, append_lc_min_bars,
)
from easy_tdx import Market
from easy_tdx.client import TdxClient

# 追加日线到 .day 文件（自动跳过重复日期）
from easy_tdx.offline import sync_daily_bars_from_security_bars

# 手动编码单条记录
bar_bytes = encode_daily_bar(bar, price_coeff=0.01, vol_coeff=0.01)

# 获取文件末尾日期
last_date = get_last_bar_date("C:/new_jyplug/vipdoc/sh/lday/sh600000.day")
```

v1.5.0 起可通过 CLI 直接使用：

```bash
easy-tdx offline daily SH 600000 --count 10 --table
easy-tdx offline ex-files --table
easy-tdx offline ex-daily 29#A1801 --table
```

### 缠论分析

基于缠论理论的技术分析模块，接收 easy_tdx 的 K 线 DataFrame，输出笔、中枢、线段、买卖点、背驰等分析结果：

```python
from easy_tdx.chanlun import ChanlunAnalyser, ChanlunConfig

# 使用 easy_tdx 获取 K 线数据
with TdxClient() as client:
    df = client.get_security_bars(Market.SH, "600519", KlineCategory.DAY, 0, 800)

# 缠论分析
analyser = ChanlunAnalyser("SH600519", "DAILY")
result = analyser.process_klines(df)

# 获取结果
print(f"笔数: {len(result.bis)}")
print(f"中枢数: {len(result.zss)}")
print(f"线段数: {len(result.xds)}")
print(f"买卖点: {[m.msg for m in result.mmds]}")
print(f"背驰: {[b.msg for b in result.bcs]}")

# JSON 兼容字典输出
print(result.to_dict())
```

## 枚举参考

### Period（K 线周期）

| 值 | 名称 | 说明 |
|----|------|------|
| 7 | `MIN_1` | 1 分钟 |
| 0 | `MIN_5` | 5 分钟 |
| 1 | `MIN_15` | 15 分钟 |
| 2 | `MIN_30` | 30 分钟 |
| 3 | `MIN_60` | 60 分钟 |
| 4 | `DAILY` | 日线 |
| 5 | `WEEKLY` | 周线 |
| 6 | `MONTHLY` | 月线 |
| 10 | `QUARTERLY` | 季线 |
| 11 | `YEARLY` | 年线 |

### Adjust（复权类型）

| 值 | 名称 | 说明 |
|----|------|------|
| 0 | `NONE` | 不复权 |
| 1 | `QFQ` | 前复权 |
| 2 | `HFQ` | 后复权 |

### Category（市场分类）

| 值 | 名称 | 说明 |
|----|------|------|
| 0 | `SH` | 上证 A 股 |
| 2 | `SZ` | 深证 A 股 |
| 6 | `A` | 全部 A 股 |
| 7 | `B` | B 股 |
| 8 | `KCB` | 科创板 |
| 12 | `BJ` | 北证 A 股 |
| 14 | `CYB` | 创业板 |

### BoardType（板块类型）

| 值 | 名称 | 说明 |
|----|------|------|
| 0 | `HY` | 行业一级 |
| 1 | `HY2` | 行业二级 |
| 3 | `GN` | 概念 |
| 4 | `FG` | 风格 |
| 5 | `DQ` | 地区 |
| 255 | `ALL` | 全部 |

### SortType（排序字段）

| 名称 | 说明 |
|------|------|
| `CODE` | 代码 |
| `PRICE` | 现价 |
| `CHANGE_PCT` | 涨幅% |
| `VOLUME` | 成交量 |
| `TOTAL_AMOUNT` | 成交额 |
| `TURNOVER_RATE` | 换手% |
| `MAIN_NET_AMOUNT` | 主力净额 |

### ExMarket（扩展市场）

| 值 | 名称 | 说明 |
|----|------|------|
| 28 | `ZZ_FUTURES` | 郑州商品 |
| 29 | `DL_FUTURES` | 大连商品 |
| 30 | `SH_FUTURES` | 上海期货 |
| 31 | `HK_MAIN_BOARD` | 香港主板 |
| 47 | `CFFEX_FUTURES` | 中金所期货 |
| 48 | `HK_GEM` | 香港创业板 |
| 74 | `US_STOCK` | 美国股票 |

### Market（市场）

| 值 | 名称 | 说明 |
|----|------|------|
| 0 | `SZ` | 深圳 |
| 1 | `SH` | 上海 |
| 2 | `BJ` | 北京 |

## 完整 API 列表

### MacClient / AsyncMacClient

| 方法 | 说明 |
|------|------|
| `get_stock_quotes(stocks, fields)` | 批量实时报价 |
| `get_stock_quotes_list(category, ...)` | 市场分类排序报价 |
| `get_stock_kline(market, code, period, ...)` | K 线（支持复权） |
| `get_stock_kline_with_indicators(market, code, indicators, ...)` | K 线 + 技术指标 |
| `get_tick_chart(market, code, date)` | 单日分时图 |
| `get_tick_charts(market, code, days)` | 多日分时图 |
| `get_chart_sampling(market, code)` | 分时缩略采样 |
| `get_transactions(market, code, ...)` | 逐笔成交 |
| `get_symbol_info(market, code)` | 个股特征快照 |
| `get_board_list(board_type, ...)` | 板块列表 |
| `get_board_members(board_symbol, ...)` | 板块成分股报价 |
| `get_board_summary(board_symbol, ...)` | 板块汇总（成交额、主力净流入、涨跌家数） |
| `get_board_ranking(board_type, top_n, sort_by, ...)` | 板块涨跌幅排行榜（行业/概念排行） |
| `get_belong_board(market, code)` | 个股所属板块 |
| `get_capital_flow(market, code)` | 资金流向 |
| `get_auction(market, code)` | 集合竞价 |
| `get_unusual(market, ...)` | 市场异动 |
| `get_server_info()` | 服务器交易时段 |
| `get_kline_offset(offset, count)` | K 线偏移信息 |
| `get_goods_list(market, ...)` | 扩展市场商品列表 |

### MacExClient / AsyncMacExClient

| 方法 | 说明 |
|------|------|
| `goods_count(market)` | 商品总数 |
| `goods_list(market, start, count)` | 商品列表 |
| `goods_quotes(stocks, fields)` | 批量报价 |
| `goods_quotes_list(market, ...)` | 市场分类报价列表 |
| `goods_kline(market, code, period, ...)` | K 线（支持复权） |
| `goods_tick_chart(market, code, ...)` | 分时图 |
| `goods_chart_sampling(market, code)` | 分时缩略采样 |
| `goods_transaction(market, code, ...)` | 逐笔成交 |

### TdxClient / AsyncTdxClient

| 方法 | 说明 |
|------|------|
| `get_security_count(market)` | 市场证券总数 |
| `get_security_list(market, start)` | 证券列表（分页） |
| `get_security_list_all()` | 沪深 A 股完整列表（含行业） |
| `get_security_quotes(stocks)` | 批量五档行情 |
| `get_security_bars(market, code, ...)` | 个股 K 线 |
| `get_index_bars(market, code, ...)` | 指数 K 线 |
| `get_minute_time_data(market, code)` | 今日分时 |
| `get_history_minute_time_data(market, code, date)` | 历史分时 |
| `get_transaction_data(market, code, ...)` | 当日逐笔成交 |
| `get_history_transaction_data(...)` | 历史逐笔成交 |
| `get_fund_flow(market, code)` | 当日资金流向 |
| `get_history_fund_flow(market, code, ...)` | 历史资金流向 |
| `get_xdxr_info(market, code)` | 除权除息历史 |
| `get_finance_info(market, code)` | 最新财务数据 |
| `get_company_info_category(market, code)` | 公司信息目录 |
| `get_company_info_content(...)` | 公司信息文本 |
| `get_block_info(filename)` | 板块信息 |
| `get_report_file(filename)` | 下载服务器文件 |
| `get_market_stat()` | 全市场涨跌统计 |
| `get_price_limits(market, code, name, pre_close)` | 涨跌停价 |

## 架构

```
src/easy_tdx/
├── client.py          # TdxClient / AsyncTdxClient（标准协议）
├── unified.py         # UnifiedTdxClient（统一入口）
├── config.py          # 服务器地址、端口、超时配置
├── indicator.py       # 技术指标计算（32 个，基于 MyTT）
├── MyTT.py            # 麦语言技术指标算法库
├── mac/
│   ├── client.py      # MacClient / AsyncMacClient（MAC 协议）
│   ├── enums.py       # Period, Adjust, Category, ExMarket, SortType, ...
│   ├── models.py      # MacBar, MacQuoteField, MacTick, BoardInfo, ...
│   └── commands/      # MAC 命令（build_request + parse_response，无 IO）
├── ex/
│   ├── client.py      # ExTdxClient / AsyncExTdxClient（标准协议扩展市场）
│   ├── mac_client.py  # MacExClient / AsyncMacExClient（MAC 协议扩展市场）
│   └── transport/     # ExTdxConnection（端口 7727）
├── transport/
│   ├── sync.py        # TdxConnection + ping_host / ping_all
│   └── async_.py      # AsyncTdxConnection（asyncio）
├── commands/          # 标准协议命令（无 IO）
├── codec/             # price / volume / datetime / frame / bitmap 编解码
├── chanlun/           # 缠论技术分析（K线合并/分型/笔/线段/中枢/买卖点/背驰）
├── models/            # 纯 dataclass，无业务逻辑
├── offline/           # 离线数据读写模块（读取 + 写入同步）
└── cli/               # easy-tdx CLI（click）
```

commands 层不依赖 transport，可独立单测。

## 开发

```bash
python -m pytest tests/unit/ -v                             # 单元测试（无需网络）
XMTDX_LIVE=1 python -m pytest tests/integration/ -v        # 集成测试
mypy src/                                                    # 类型检查
ruff check src/ tests/                                       # lint
ruff format --check src/ tests/                              # format check
```

## 致谢

- [pytdx](https://github.com/rainx/pytdx) -- 离线数据读取模块借鉴自 pytdx 项目，感谢 rainx 及所有贡献者
- [xmtdx](https://github.com/minionszyw/xmtdx) -- 本项目初始原型
- [mootdx](https://github.com/mootdx/mootdx) -- 工程化封装参考
- [MyTT](https://github.com/mpquant/MyTT) -- 麦语言技术指标算法库，技术指标计算基于此实现

详见 [NOTICE](NOTICE) 和 [LICENSE](LICENSE)。

## Changelog

### 1.7.0 (2026-06-07)

**缠论技术分析模块** — 新增完整的缠论（ChanLun）计算引擎，通过 CLI 和 Python API 提供个股缠论分析。

- 新增 `chanlun` 子包：K线合并、分型识别、笔/线段/中枢/买卖点/背驰计算
- 新增 `easy-tdx chanlun` CLI 命令，支持 JSON/表格输出
- 新增 MACD 指标计算（纯 numpy，无额外依赖）
- 新增多级别联立分析（MultiLevelAnalyser）
- 计算管道：`DataFrame → K线合并 → 分型 → 笔 → 中枢 → 线段 → 买卖点 → 背驰`
- 49 个离线单元测试覆盖，零网络依赖

### 1.6.1 (2026-06-07)

**Bug 修复** — 修复 sync-all/sync-daily 对指数文件误用股票解析器导致垃圾日期的问题。

- 修复 `_fetch_all_daily_bars` 对指数文件（sh00/sh88/sh99, sz39）错误调用 `get_security_bars()` 的问题
- 指数文件现在正确使用 `get_index_bars()`（服务端响应每条记录多 4 字节上涨/下跌家数）
- 新增 `_is_index_code()` 辅助函数，根据市场和代码前缀判断证券类型

### 1.6.0 (2026-06-07)

**离线数据写入同步** — 从服务端获取最新日线数据并写入本地通达信 .day 文件，替代通达信内置下载功能。

- 新增 `offline sync-daily` CLI 命令：同步单只股票日线，自动增量/全量判断，支持分页获取完整历史
- 新增 `offline sync-all` CLI 命令：一键扫描沪深全市场 .day 文件并同步
- 新增 `write_daily.py` 模块：日线编解码（`encode_daily_bar`）、追加写入（`append_daily_bars`）、末尾日期检测
- 新增 `write_ex_daily.py` 模块：扩展市场日线写入（期货/港股，价格 float32）
- 新增 `write_min_bar.py` 模块：分钟线写入（.5/.lc1/.lc5 格式）
- 写入自动跳过重复日期，空文件自动全量下载，已有数据只做增量追加
- 50 个新增单元测试覆盖编解码 round-trip、追加去重、边界条件

### 1.5.0 (2026-06-02)

**离线数据 CLI 命令** — 新增 `offline` 命令组，无需网络即可通过 CLI 读取本地通达信数据文件。

- 新增 `offline home`：检测通达信安装目录
- 新增 `offline daily`：A 股日线数据（.day 文件）
- 新增 `offline min`：分钟线数据（.5/.lc1/.lc5 文件，`--type` 指定格式）
- 新增 `offline ex-files`：列出扩展市场可用日线文件
- 新增 `offline ex-daily`：扩展市场日线数据（期货/港股/外盘）
- 新增 `offline gbbq`：股本变迁数据
- 新增 `offline financial`：历史财务数据
- 新增 `offline blocks`：自定义板块数据

### 1.4.3 (2026-05-28)

**30日乖离率信号指标** — 新增 BIAS_SIGNAL 指标，在标准乖离率基础上叠加短/长信号线，通过三者位置关系判断趋势方向和转折点。源自通达信经典指标。

- 新增 `BIAS_SIGNAL` 指标：输出 BS_X/BS_SMA/BS_LMA 三条线
- CLI: `easy-tdx indicator BIAS_SIGNAL -m SH -c 600519 --table`
- Python API: `indicators=["BIAS_SIGNAL"]`
- 详见 [30日乖离率信号指标详解](docs/indicator-bias-signal.md)

### 1.4.2 (2026-05-28)

修复 1.4.1 发布遗漏：MyTT.py 中 ZHUOYAO 函数定义未包含在 1.4.1 的 PyPI 包中。

### 1.4.1 (2026-05-28)

**捉妖大师指标** — 新增 ZHUOYAO 多周期涨幅共振指标，通过 20/60/120 日涨幅及指数平滑判断短中长线趋势是否同向，用于筛选趋势刚启动的强势股。

- 新增 `ZHUOYAO` 指标：输出 ZY_LONG/ZY_MID/ZY_SHORT/ZY_TREND 四条线
- CLI: `easy-tdx indicator ZHUOYAO -m SH -c 600519 --table`
- Python API: `indicators=["ZHUOYAO"]`
- 详见 [捉妖大师指标详解](docs/indicator-zhuoyao.md)

### 1.4.0 (2026-05-28)

**技术指标计算** — 集成 [MyTT](https://github.com/mpquant/MyTT) 麦语言指标库，支持 30 个常用技术指标，一步获取 K 线 + 指标值。

- 新增 `indicator.py` 核心模块：注册表驱动的指标调度，`compute_indicators()` 纯计算无 IO
- 新增 `MacClient.get_stock_kline_with_indicators()` / `AsyncMacClient` 同名方法
- 新增 `UnifiedTdxClient.get_stock_kline_with_indicators()` / `AsyncUnifiedTdxClient` 同名方法
- 新增 CLI 命令 `easy-tdx indicator` 和 `easy-tdx indicator-list`
- 自动获取 200+ 条历史数据预热 EMA，用户只需指定返回条数
- 支持的指标：MACD, KDJ, RSI, BOLL, DMI, ATR, WR, CCI, BIAS, OBV, VR, EMV, MFI, BRAR, ASI, TRIX, DPO, MTM, ROC, EXPMA, BBI, PSY, DFMA, CR, KTN, XSII, MASS, TAQ

### 1.3.1 (2025-05-15)

- 新增 `board-summary` 和 `board-ranking` CLI 命令
- 新增 `get_board_summary()` 板块汇总（成交额、主力净流入、涨跌家数）
- 新增 `get_board_ranking()` 板块涨跌幅排行榜

### 1.3.0 (2025-05-12)

- 新增 MAC 协议客户端 `MacClient` / `AsyncMacClient`（端口 7709）
- 新增扩展市场客户端 `MacExClient` / `AsyncMacExClient`（端口 7727）
- 新增统一客户端 `UnifiedTdxClient` 自动路由 A 股 / 扩展市场
- 新增板块、资金流向、集合竞价、异动、个股特征等数据接口
- 新增 `easy-tdx` CLI 工具，默认 JSON 输出

### 1.2.1 (2025-04-20)

- 离线数据读取模块（日线、分钟线、板块、财务）
- 除权除息、股本变迁读取

### 1.0.0 (2025-03-01)

- 首个正式版本
- TdxClient / AsyncTdxClient 标准协议客户端
- K 线、实时报价、分时、逐笔成交、财务数据
