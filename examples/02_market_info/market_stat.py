"""演示：获取全市场涨跌统计概况。

使用 TdxClient.get_market_stat() 获取 A 股全市场实时涨跌统计。
该方法通过查询通达信内置指数代码获取统计数据：
  - 880005: 全市场行情统计（涨/跌/平/总数）
  - 880001: 总市值指数（总市值 = price × 1e10）
  - 880006: 涨跌停统计

返回 DataFrame 列说明（MarketStat 表结构）：
  up_count          : int    -- 上涨家数
  down_count        : int    -- 下跌家数
  neutral_count     : int    -- 平盘家数
  suspended_count   : int    -- 残差估算值（total - up - down - neutral），
                               近似表示停牌/未参与统计家数。此字段并非协议明确
                               定义的停牌字段，仅用于保证计数守恒。
  total_count       : int    -- 总计（包含停牌）
  total_amount      : float  -- 总成交额（元）
  total_volume      : float  -- 总成交量
  total_market_cap  : float  -- 总市值（元），来自 880001 收盘价 × 1e10
  limit_up_count    : int    -- 涨停家数，来自 880006
  limit_down_count  : int    -- 跌停家数，来自 880006

使用客户端：TdxClient（同步）
关键参数：无
返回类型：pd.DataFrame（单行）
"""

from easy_tdx import TdxClient

with TdxClient.from_best_host() as c:
    stat = c.get_market_stat()
    print(stat.to_string(index=False))

# 运行结果:
#  up_count  down_count  neutral_count  suspended_count  total_count
#      2841        1985            512               82         5420
#  total_amount  total_volume  total_market_cap  limit_up_count  limit_down_count
#  1.234567e+12   8.765432e+09      9.876543e+13              68              12
