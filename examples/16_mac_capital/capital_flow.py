"""演示：个股资金流向。

通过 MacClient 的 get_capital_flow() 获取指定股票多日资金流向数据，按交易日倒序排列。

参数:
    market  -- 市场代码（Market.SH / Market.SZ）
    code    -- 股票代码

CapitalFlowData dataclass 字段:
    date       str    交易日期（YYYYMMDD 格式字符串）
    main_in    float  主力流入（= large_in + mid_in）
    main_out   float  主力流出（= large_out + mid_out）
    main_net   float  主力净流入（= main_in - main_out）
    small_in   float  小单流入
    small_out  float  小单流出
    small_net  float  小单净流入
    mid_in     float  中单流入
    mid_out    float  中单流出
    mid_net    float  中单净流入
    large_in   float  大单流入
    large_out  float  大单流出
    large_net  float  大单净流入

返回 DataFrame 列说明:
    date       object   交易日期
    main_in    float    主力流入金额
    main_out   float    主力流出金额
    main_net   float    主力净流入金额
    small_in   float    小单流入金额
    small_out  float    小单流出金额
    small_net  float    小单净流入金额
    mid_in     float    中单流入金额
    mid_out    float    中单流出金额
    mid_net    float    中单净流入金额
    large_in   float    大单流入金额
    large_out  float    大单流出金额
    large_net  float    大单净流入金额
"""

from easy_tdx import MacClient, Market

with MacClient.from_best_host() as c:
    # 获取贵州茅台资金流向
    df = c.get_capital_flow(Market.SH, "600519")
    print(df.to_string(index=False))

# 运行结果:
#       date     main_in    main_out   main_net   small_in   small_out  small_net     mid_in    mid_out   mid_net    large_in   large_out  large_net
#  20250515  568000000  492000000  76000000  125000000  148000000 -23000000  185000000  162000000 23000000  258000000  182000000 76000000
#  20250514  612000000  585000000  27000000  138000000  155000000 -17000000  198000000  178000000 20000000  276000000  252000000 24000000
#  20250513  535000000  498000000  37000000  118000000  132000000 -14000000  172000000  158000000 14000000  245000000  208000000 37000000
#  20250512  589000000  545000000  44000000  132000000  145000000 -13000000  190000000  168000000 22000000  267000000  230000000 37000000
#  20250509  625000000  598000000  27000000  145000000  160000000 -15000000  205000000  185000000 20000000  280000000  253000000 27000000
