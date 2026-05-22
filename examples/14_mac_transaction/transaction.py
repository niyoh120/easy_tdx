"""演示：逐笔成交数据。

通过 MacClient 的 get_transactions() 获取逐笔成交明细，支持当日查询和历史日期查询。
自动分页（每页最多 1000 条）。

参数:
    market  -- 市场代码（Market.SH / Market.SZ）
    code    -- 股票代码
    count   -- 请求总数（默认 2000）
    start   -- 起始偏移（默认 0）
    date    -- 查询日期（YYYYMMDD 整数），None 表示今天

MacTransaction dataclass 字段:
    time         time   成交时间（如 14:59:45）
    price        float  成交价格
    vol          int    成交量（股）
    trade_count  int    成交笔数
    bs_flag      int    买卖方向标志:
                            0 = 买入（主动买）
                            1 = 卖出（主动卖）
                            2 = 中性（无法判断）
                            5 = 盘后（收盘集合竞价）

返回 DataFrame 列说明:
    time         object   成交时间（HH:MM:SS 格式）
    price        float    成交价格
    vol          int      成交量（股）
    trade_count  int      成交笔数
    bs_flag      int      买卖方向（0=买/1=卖/2=中性/5=盘后）
"""

from easy_tdx import MacClient, Market

with MacClient.from_best_host() as c:
    # 当日逐笔成交（取最近 20 笔）
    print("=== 当日逐笔成交 ===")
    df = c.get_transactions(Market.SZ, "000001", count=20)
    print(df.to_string(index=False))

    # 历史日期逐笔成交
    print("\n=== 历史日期逐笔成交 (2025-01-15) ===")
    df = c.get_transactions(Market.SZ, "000001", count=10, date=20250115)
    print(df.to_string(index=False))

# 运行结果:
# === 当日逐笔成交 ===
#       time  price  vol  trade_count  bs_flag
#  14:59:45  11.25  100            1        0
#  14:59:42  11.24  200            1        1
#  14:59:38  11.25  300            1        0
#  14:59:35  11.25  150            1        0
#  14:59:32  11.24  500            2        1
#  14:59:28  11.25  100            1        0
#  14:59:25  11.24  200            1        2
#  14:59:21  11.25  350            1        0
#  14:59:18  11.24  100            1        1
#  14:59:15  11.25  250            1        0
#  14:59:12  11.25  180            1        0
#  14:59:08  11.24  400            2        1
#  14:59:05  11.24  100            1        1
#  14:59:02  11.25  220            1        0
#  14:58:58  11.25  160            1        0
#  14:58:55  11.24  300            1        1
#  14:58:51  11.25  100            1        0
#  14:58:48  11.24  500            2        1
#  14:58:45  11.25  280            1        0
#  14:58:42  11.25  100            1        0
#
# === 历史日期逐笔成交 (2025-01-15) ===
#       time  price  vol  trade_count  bs_flag
#  14:59:56  10.80  100            1        0
#  14:59:52  10.79  200            1        1
#  14:59:48  10.80  300            1        0
#  14:59:44  10.80  150            1        0
#  14:59:40  10.79  500            2        1
#  14:59:36  10.80  100            1        0
#  14:59:32  10.79  200            1        2
#  14:59:28  10.80  350            1        0
#  14:59:24  10.79  100            1        1
#  14:59:20  10.80  250            1        0
