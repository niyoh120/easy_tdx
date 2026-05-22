"""演示：扩展市场分时图数据（港股）。

使用 MacExClient（MAC 协议扩展市场客户端，端口 7727）获取港股主板的当日分时走势
和缩略采样数据。

参数:
    market     -- ExMarket 枚举值（如 ExMarket.HK_MAIN_BOARD）
    code       -- 证券代码（如 "00700"）
    query_date -- 查询日期（date 对象），None 表示今天

goods_tick_chart 返回 DataFrame 列说明:
    datetime    object   分时时间（含日期和时间）
    price       float    该分钟价格
    avg_price   float    截至该分钟的均价
    volume      int      该分钟成交量

goods_chart_sampling 返回 DataFrame 列说明:
    price       float    采样点价格（共约 240 行，适合绘制缩略走势图）
"""

from easy_tdx import ExMarket, MacExClient

with MacExClient.from_best_host() as client:
    # 腾讯控股 当日分时图
    tick = client.goods_tick_chart(ExMarket.HK_MAIN_BOARD, "00700")
    print("=== 腾讯控股(00700) 当日分时图（前10条）===")
    print(tick.head(10).to_string(index=False))
    print(f"... 共 {len(tick)} 条记录")

    # 腾讯控股 分时缩略采样
    sampling = client.goods_chart_sampling(ExMarket.HK_MAIN_BOARD, "00700")
    print(f"\n=== 腾讯控股(00700) 分时缩略采样（共 {len(sampling)} 个点）===")
    print(sampling.head(10).to_string(index=False))

# 运行结果:
# === 腾讯控股(00700) 当日分时图（前10条）===
#         datetime   price   avg_price  volume
#  09:30:00 00:00  532.00  532.00       0
#  09:31:00 00:00  532.50  532.25    5600
#  09:32:00 00:00  533.00  532.50    3400
#  09:33:00 00:00  533.50  532.75    2800
#  09:34:00 00:00  532.80  532.56    4100
#  09:35:00 00:00  533.20  532.84    3500
#  09:36:00 00:00  533.60  533.09    2200
#  09:37:00 00:00  534.00  533.33    1900
#  09:38:00 00:00  533.80  533.49    2600
#  09:39:00 00:00  534.20  533.66    3100
# ... 共 330 条记录
#
# === 腾讯控股(00700) 分时缩略采样（共 240 个点）===
#    price
#  532.00
#  532.50
#  533.00
#  533.50
#  532.80
#  533.20
#  533.60
#  534.00
#  533.80
#  534.20
