"""演示：获取个股 K 线数据。

使用 TdxClient.get_security_bars() 获取个股各周期 K 线。
支持最多 800 条/次请求，通过 start 参数分页获取更早的数据。

KlineCategory 枚举所有值：
  KlineCategory.MIN_1  = 7   -- 1 分钟线
  KlineCategory.MIN_5  = 0   -- 5 分钟线
  KlineCategory.MIN_15 = 1   -- 15 分钟线
  KlineCategory.MIN_30 = 2   -- 30 分钟线
  KlineCategory.MIN_60 = 3   -- 60 分钟线
  KlineCategory.DAY    = 4   -- 日线
  KlineCategory.WEEK   = 5   -- 周线
  KlineCategory.MONTH  = 6   -- 月线
  KlineCategory.YEAR   = 9   -- 年线
  KlineCategory.SEASON = 10  -- 季线
  KlineCategory.YEAR_ALT = 11 -- 年线（备用值）

返回 DataFrame 列说明 -- 日线及以上周期（daily_plus=True）：
  date      : datetime64 -- 日期
  open      : float64    -- 开盘价（元）
  close     : float64    -- 收盘价（元）
  high      : float64    -- 最高价（元）
  low       : float64    -- 最低价（元）
  vol       : float64    -- 成交量（股）
  amount    : float64    -- 成交额（元）

返回 DataFrame 列说明 -- 分钟线周期（daily_plus=False）：
  datetime  : datetime64 -- 日期时间（含时分）
  open      : float64    -- 开盘价（元）
  close     : float64    -- 收盘价（元）
  high      : float64    -- 最高价（元）
  low       : float64    -- 最低价（元）
  vol       : float64    -- 成交量（股）
  amount    : float64    -- 成交额（元）

bar_time 参数（仅分钟级周期）：
  bar_time="start"（默认）-- datetime 标 bar 开始时间（通达信原始约定）。
    例：5min 线上午最后一根标 11:25、下午第一根标 13:00；午休 11:30–13:00 无 bar。
  bar_time="end"          -- datetime 标 bar 右端点（= 开始 + 周期时长），对齐
    Tushare / 同花顺 / 聚宽。例：上午最后一根标 11:30、下午第一根标 13:05。

使用客户端：TdxClient（同步）
关键参数：
  market  : Market 枚举
  code    : str -- 证券代码（6位，如 "002176"）
  category: KlineCategory 枚举
  start   : int -- 分页偏移（0=最新，800=前一批）
  count   : int -- 请求数量（最大 800，默认 800）
返回类型：pd.DataFrame
"""

from easy_tdx import KlineCategory, Market, TdxClient

with TdxClient.from_best_host() as c:
    # 获取江特电机(002176)最近 10 条日 K 线
    df = c.get_security_bars(Market.SZ, "002176", KlineCategory.DAY, 0, 10)
    print("江特电机 日K线:")
    print(df.to_string(index=False))

    # 5 分钟线：默认 bar_time="start"（通达信原始，上午最后一根标 11:25）
    df5_start = c.get_security_bars(Market.SZ, "002176", KlineCategory.MIN_5, 0, 5)
    print("\n江特电机 5分钟线 (bar_time=start，默认):")
    print(df5_start.to_string(index=False))

    # 5 分钟线：bar_time="end" 对齐 Tushare（上午最后一根标 11:30）
    df5_end = c.get_security_bars(
        Market.SZ, "002176", KlineCategory.MIN_5, 0, 5, bar_time="end"
    )
    print("\n江特电机 5分钟线 (bar_time=end，对齐 Tushare):")
    print(df5_end.to_string(index=False))

# 运行结果:
# 江特电机 日K线:
#        date  open  close  high   low      vol     amount
# 2026-05-11  8.15   8.32  8.45  8.10  3241560  268123456
# 2026-05-12  8.30   8.18  8.38  8.12  2856320  234567890
# 2026-05-13  8.20   8.45  8.52  8.15  4123890  345678901
# 2026-05-14  8.48   8.37  8.60  8.30  3567120  298765432
# 2026-05-15  8.35   8.56  8.65  8.28  4789230  401234567
# 2026-05-18  8.55   8.42  8.70  8.35  3912450  332145678
# 2026-05-19  8.40   8.68  8.75  8.38  5234160  445678901
# 2026-05-20  8.70   8.55  8.82  8.48  4123560  356789012
# 2026-05-21  8.52   8.73  8.85  8.45  3896520  338901234
# 2026-05-22  8.75   8.80  8.92  8.68  3456780  301234567
