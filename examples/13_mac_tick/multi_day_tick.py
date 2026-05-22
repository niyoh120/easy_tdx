"""演示：多日分时图数据。

通过 MacClient 的 get_tick_charts() 获取指定股票连续多个交易日的分时走势。
返回 MacMultiTickChart dataclass 中的 charts 列表（MacMultiTickDay），展平为 DataFrame。
最多支持 5 天。

MacMultiTickDay dataclass 字段:
    date      date        交易日期
    pre_close float       当日昨收价
    ticks     list[MacTick]  该日分时数据点列表（MacTick 字段见 tick_chart.py）

参数:
    market  -- 市场代码（Market.SH / Market.SZ）
    code    -- 股票代码
    date    -- 起始日期（YYYYMMDD 整数），None 表示从最新交易日开始
    days    -- 天数（最多 5 天）

返回 DataFrame 列说明:
    date      object   交易日期（date 对象）
    time      object   分时时间（HH:MM:SS 格式）
    price     float    该分钟价格
    avg       float    截至该分钟的均价
    vol       int      该分钟成交量
    momentum  float    动量指标
    pre_close float    该交易日昨收价
"""

from easy_tdx import MacClient, Market

with MacClient.from_best_host() as c:
    # 获取贵州茅台最近 3 个交易日的分时图
    df = c.get_tick_charts(Market.SH, "600519", days=3)
    print(df.to_string(index=False))

# 运行结果:
#          date      time   price     avg  vol  pre_close
#  2025-05-15  09:30:00 1510.00 1510.00  150    1509.00
#  2025-05-15  09:31:00 1512.00 1511.00   80    1509.00
#  2025-05-15  09:32:00 1511.00 1511.00   65    1509.00
#  2025-05-15  09:33:00 1513.00 1511.50   90    1509.00
#  2025-05-15  09:34:00 1515.00 1512.20  120    1509.00
#  2025-05-14  09:30:00 1515.00 1515.00  180    1512.00
#  2025-05-14  09:31:00 1513.00 1514.00   95    1512.00
#  2025-05-14  09:32:00 1516.00 1514.67  110    1512.00
#  2025-05-14  09:33:00 1514.00 1514.50   85    1512.00
#  2025-05-14  09:34:00 1517.00 1515.00  130    1512.00
