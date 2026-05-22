"""演示：扩展市场商品列表（港股主板）。

使用 MacExClient（MAC 协议扩展市场客户端，端口 7727）获取港股主板的商品列表和总数。
goods_list 返回 DataFrame，goods_count 返回整数。

ExMarket 枚举常用值:
    HK_MAIN_BOARD=31   香港主板      US_STOCK=74      美国股票
    CFFEX_FUTURES=47   中金所期货    ZZ_FUTURES=28    郑州商品
    DL_FUTURES=29      大连商品      SH_FUTURES=30    上海期货
    HK_GEM=48          香港创业板    HK_FUND=49       香港基金
    SG_STOCK=78        新加坡股票    GE_STOCK=73      德国股票
    SH_GOLD=46         上海黄金      CSI_INDEX=62     中证指数
    OPEN_END_FUND=33   开放式基金    MONETARY_FUND=34 货币型基金
    INTL_INDEX=12      国际指数      BASIC_FX=10      基本汇率

参数:
    market  -- ExMarket 枚举值
    start   -- 起始偏移（默认 0）
    count   -- 请求数量（最大 1000，默认 600）

goods_list 返回 DataFrame 列说明:
    code    str   证券代码（如 "00001"）
    name    str   证券名称（如 "长和"）
    market  int   市场代码（= ExMarket 枚举值，如 31）

goods_count 返回: int，该市场商品总数。
"""

from easy_tdx import ExMarket, MacExClient

with MacExClient.from_best_host() as client:
    # 获取港股主板前 20 只商品
    df = client.goods_list(ExMarket.HK_MAIN_BOARD, count=20)
    print("=== 港股主板商品列表（前20条）===")
    print(df.to_string(index=False))

    # 获取港股主板商品总数
    total = client.goods_count(ExMarket.HK_MAIN_BOARD)
    print(f"\n港股主板商品总数: {total}")

# 运行结果:
# === 港股主板商品列表（前20条）===
#        code           name  market
#      00001         长和      31
#      00002         中电控股    31
#      00003         香港中华煤气  31
#      00004         九龙仓集团   31
#      00005         汇丰控股    31
#      00006         电能实业    31
#      00007         高鑫零售    31
#      00008         新鸿基地产   31
#      00009         载通       31
#      00010         恒隆地产    31
#      00011         恒生银行    31
#      00012         恒基兆业地产  31
#      00013         和黄医药    31
#      00014         希慎兴业    31
#      00015         盈富基金    31
#      00016         新鸿基公司   31
#      00017         新世界发展   31
#      00018         东方报业集团  31
#      00019         太古股份公司A 31
#      00020         商汤集团    31
#
# 港股主板商品总数: 2846
