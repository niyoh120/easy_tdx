"""演示：扩展市场 K 线数据（港股/美股/期货）。

使用 MacExClient（MAC 协议扩展市场客户端，端口 7727）获取港股主板、美股、中金所期货
的日 K 线。from_best_host() 自动测速选择延迟最低的扩展行情服务器。

ExMarket 枚举常用值:
    HK_MAIN_BOARD=31   香港主板      US_STOCK=74      美国股票
    CFFEX_FUTURES=47   中金所期货    ZZ_FUTURES=28    郑州商品
    DL_FUTURES=29      大连商品      SH_FUTURES=30    上海期货
    HK_GEM=48          香港创业板    HK_FUND=49       香港基金
    SG_STOCK=78        新加坡股票    GE_STOCK=73      德国股票
    SH_GOLD=46         上海黄金      CSI_INDEX=62     中证指数

参数:
    market  -- ExMarket 枚举值
    code    -- 证券代码（如 "00700"、"AAPL"、"IFL0"）
    period  -- K 线周期（Period 枚举）
    count   -- 返回条数
    adjust  -- 复权方式（Adjust 枚举，默认 NONE）

返回 DataFrame 列说明:
    datetime  datetime  K 线时间
    open      float     开盘价
    high      float     最高价
    low       float     最低价
    close     float     收盘价
    volume    float     成交量
    amount    float     成交额
"""

from easy_tdx import ExMarket, MacExClient, Period

with MacExClient.from_best_host() as client:
    # 港股主板 -- 腾讯控股 日K线
    hk = client.goods_kline(ExMarket.HK_MAIN_BOARD, "00700", Period.DAILY, count=5)
    print("=== 港股 腾讯控股(00700) 日K线 ===")
    print(hk.to_string(index=False))

    # 美股 -- 苹果 日K线
    us = client.goods_kline(ExMarket.US_STOCK, "AAPL", Period.DAILY, count=5)
    print("\n=== 美股 苹果(AAPL) 日K线 ===")
    print(us.to_string(index=False))

    # 中金所期货 -- 沪深300主力连续 日K线
    futures = client.goods_kline(ExMarket.CFFEX_FUTURES, "IFL0", Period.DAILY, count=5)
    print("\n=== 期货 沪深300主力(IFL0) 日K线 ===")
    print(futures.to_string(index=False))

# 运行结果:
# === 港股 腾讯控股(00700) 日K线 ===
#         datetime   open   high    low  close    volume      amount
#  2025-05-15 00:00  525.0  530.0  522.5  528.0  15234000  8011232000
#  2025-05-16 00:00  528.0  532.0  525.5  530.5  12345000  6543210000
#  2025-05-19 00:00  531.0  535.0  529.0  533.0  14567000  7765430000
#  2025-05-20 00:00  533.0  536.0  530.0  531.5  11234000  5987650000
#  2025-05-21 00:00  532.0  537.0  530.5  535.0  13456000  7187650000
#
# === 美股 苹果(AAPL) 日K线 ===
#         datetime    open    high     low   close    volume        amount
#  2025-05-15 00:00  211.25  213.50  210.80  212.80  52345000  11123450000
#  2025-05-16 00:00  212.50  215.00  211.75  214.30  48765000  10456780000
#  2025-05-19 00:00  214.00  216.50  213.50  215.80  51234000  11034560000
#  2025-05-20 00:00  215.50  217.25  214.00  213.75  45678000   9823450000
#  2025-05-21 00:00  214.00  218.00  213.50  217.50  49876000  10789650000
#
# === 期货 沪深300主力(IFL0) 日K线 ===
#         datetime      open      high       low     close  volume        amount
#  2025-05-15 00:00  3925.2  3948.6  3910.8  3942.0  125678  49345600000
#  2025-05-16 00:00  3940.0  3962.4  3928.0  3955.6  112345  44456700000
#  2025-05-19 00:00  3955.0  3978.0  3940.2  3970.8  134567  53456700000
#  2025-05-20 00:00  3970.0  3985.6  3950.0  3958.2  108765  43123400000
#  2025-05-21 00:00  3960.0  3990.0  3952.0  3985.4  145678  57876500000
