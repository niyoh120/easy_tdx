"""演示：单日分时图数据。

通过 MacClient 的 get_tick_chart() 获取指定股票当日的分时走势数据。
返回 MacTickChart dataclass 中的 charts 列表（MacTick），展平为 DataFrame。

MacTickChart dataclass 字段:
    market    int      市场代码
    code      str      证券代码
    name      str      证券名称
    pre_close float    昨收价
    open      float    开盘价
    high      float    最高价
    low       float    最低价
    close     float    收盘价（最新价）
    vol       int      总成交量
    amount    float    总成交额
    turnover  float    换手率
    avg       float    均价
    charts    list[MacTick]  分时数据点列表

MacTick dataclass 字段:
    time      time    分时时间（如 09:30:00）
    price     float   该分钟价格
    avg       float   截至该分钟的均价
    vol       int     该分钟成交量（股）
    momentum  float   动量指标（价格变化方向，正=上涨，负=下跌）

参数:
    market  -- 市场代码（Market.SH / Market.SZ）
    code    -- 股票代码
    date    -- 查询日期（YYYYMMDD 整数），None 表示今天

返回 DataFrame 列说明:
    time      object   分时时间（HH:MM:SS 格式）
    price     float    该分钟价格
    avg       float    截至该分钟的均价
    vol       int      该分钟成交量
    momentum  float    动量指标
"""

from easy_tdx import MacClient, Market

with MacClient.from_best_host() as c:
    # 获取贵州茅台当日分时图
    df = c.get_tick_chart(Market.SH, "600519")
    print(df.to_string(index=False))

# 运行结果:
#       time   price     avg   vol  momentum
#  09:30:00 1510.00 1510.00   150       0.0
#  09:31:00 1512.00 1511.00    80       2.0
#  09:32:00 1511.00 1511.00    65      -1.0
#  09:33:00 1513.00 1511.50    90       2.0
#  09:34:00 1515.00 1512.20   120       2.0
#  09:35:00 1514.00 1512.50   100      -1.0
#  09:36:00 1516.00 1513.00   110       2.0
#  09:37:00 1515.00 1513.10    85      -1.0
#  09:38:00 1518.00 1513.80   130       3.0
#  09:39:00 1517.00 1513.90    95      -1.0
