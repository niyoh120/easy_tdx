"""演示：扩展市场实时报价（港股/美股）。

使用 MacExClient（MAC 协议扩展市场客户端，端口 7727）批量获取港股主板和美股的实时报价。
stocks 参数为 [(ExMarket, 代码), ...] 列表，单次最多 80 只。

参数:
    stocks  -- list[tuple[int, str]]，例如 [(ExMarket.HK_MAIN_BOARD, "00700"), ...]
    fields  -- 字段选择（默认 None 即 PresetField.COMMON）

返回 DataFrame 列说明:
    market     int     市场代码（31=香港主板, 74=美国股票 等，对应 ExMarket 枚举值）
    code       str     证券代码
    name       str     证券名称
    pre_close  float   昨收价
    open       float   开盘价
    high       float   最高价
    low        float   最低价
    price      float   最新价
    volume     int     成交量
    amount     float   成交额
"""

from easy_tdx import ExMarket, MacExClient

with MacExClient.from_best_host() as client:
    stocks = [
        (ExMarket.HK_MAIN_BOARD, "00700"),  # 腾讯控股
        (ExMarket.HK_MAIN_BOARD, "09988"),  # 阿里巴巴-SW
        (ExMarket.US_STOCK, "AAPL"),  # 苹果
        (ExMarket.US_STOCK, "TSLA"),  # 特斯拉
    ]
    df = client.goods_quotes(stocks)
    print("=== 扩展市场实时报价 ===")
    print(df.to_string(index=False))

# 运行结果:
# === 扩展市场实时报价 ===
#  market   code        name   pre_close     open     high      low    price   volume        amount
#      31  00700      腾讯控股     531.00   532.00   537.00   530.50   535.00  13456000  7187650000
#      31  09988  阿里巴巴-SW     128.30   129.00   131.50   127.80   130.20   8765000  1134500000
#      74   AAPL       APPLE     213.75   214.00   218.00   213.50   217.50  49876000  10789650000
#      74   TSLA       TESLA     342.50   345.00   350.20   340.10   348.80  62345000  21678900000
