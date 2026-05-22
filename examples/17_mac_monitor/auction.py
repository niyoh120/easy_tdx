"""演示：集合竞价数据。

通过 MacClient 的 get_auction() 获取指定股票集合竞价期间（09:15-09:25）的逐笔撮合数据。
数据按时间倒序排列（最新在前）。

参数:
    market  -- 市场代码（Market.SH / Market.SZ）
    code    -- 股票代码

AuctionItem dataclass 字段:
    time       time   竞价时间（如 09:25:00）
    price      float  竞价撮合价格
    matched    int    已匹配量（股）
    unmatched  int    未匹配量（股）

返回 DataFrame 列说明:
    time       object   竞价时间（HH:MM:SS 格式）
    price      float    竞价撮合价格
    matched    int      已匹配量
    unmatched  int      未匹配量
"""

from easy_tdx import MacClient, Market

with MacClient.from_best_host() as c:
    # 获取贵州茅台集合竞价数据
    df = c.get_auction(Market.SH, "600519")
    print(df.to_string(index=False))

# 运行结果:
#       time    price  matched  unmatched
#  09:25:00 1510.00     3500          0
#  09:24:00 1509.50     2800        200
#  09:23:00 1508.00     2100        450
#  09:22:00 1507.50     1500        600
#  09:21:00 1506.00     1000        800
#  09:20:00 1505.00      800       1200
#  09:19:00 1504.50      500       1500
#  09:18:00 1503.00      300       1800
#  09:17:00 1502.00      150       2000
#  09:15:00 1500.00       50       2500
