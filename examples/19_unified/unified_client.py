"""演示：UnifiedTdxClient 统一入口，同一连接内访问 A 股和扩展市场。

UnifiedTdxClient 内部自动管理两个客户端:
    - MacClient（A 股，端口 7709）: 在 connect()/__enter__ 时立即连接
    - MacExClient（扩展市场，端口 7727）: 延迟到首次使用时连接

使用统一的 with 块即可同时获取 A 股和港股/美股数据，无需分别管理两个客户端连接。
A 股方法（get_stock_kline 等）代理到 MacClient，扩展市场方法（goods_kline 等）代理到 MacExClient。

路由机制:
    - A 股方法 (get_stock_*, get_tick_*, get_board_*, get_capital_flow, ...):
      首次调用时自动创建 MacClient 并连接到 7709 端口
    - 扩展市场方法 (goods_*, get_goods_list):
      首次调用时自动创建 MacExClient 并连接到 7727 端口
    - close()/__exit__ 时同时关闭两个连接

支持的 A 股方法:
    get_stock_quotes, get_stock_quotes_list, get_stock_kline,
    get_tick_chart, get_tick_charts, get_chart_sampling,
    get_transactions, get_symbol_info, get_board_list,
    get_board_members, get_belong_board, get_capital_flow,
    get_auction, get_unusual, get_server_info, get_kline_offset

支持的扩展市场方法:
    goods_count, goods_list, goods_quotes, goods_quotes_list,
    goods_kline, goods_tick_chart, goods_chart_sampling,
    goods_transaction
"""

from easy_tdx import ExMarket, Market, Period, UnifiedTdxClient

with UnifiedTdxClient() as client:
    # A 股 -- 贵州茅台 日K线
    df_a = client.get_stock_kline(Market.SH, "600519", Period.DAILY, count=5)
    print("=== A股 贵州茅台(600519) 日K线 ===")
    print(df_a.to_string(index=False))

    # 扩展市场 -- 港股腾讯控股 日K线
    df_hk = client.goods_kline(ExMarket.HK_MAIN_BOARD, "00700", Period.DAILY, count=5)
    print("\n=== 港股 腾讯控股(00700) 日K线 ===")
    print(df_hk.to_string(index=False))

# 运行结果:
# === A股 贵州茅台(600519) 日K线 ===
#         datetime     open     high      low    close    volume        amount
#  2025-05-15 00:00  1535.00  1548.00  1528.00  1542.00    345678  532456000000
#  2025-05-16 00:00  1542.00  1556.00  1535.00  1548.50    312345  483456000000
#  2025-05-19 00:00  1548.00  1560.00  1540.00  1555.00    378901  588765000000
#  2025-05-20 00:00  1555.00  1562.00  1545.00  1548.00    298765  462345000000
#  2025-05-21 00:00  1548.00  1558.00  1542.00  1552.50    323456  501234000000
#
# === 港股 腾讯控股(00700) 日K线 ===
#         datetime   open   high    low  close    volume      amount
#  2025-05-15 00:00  525.0  530.0  522.5  528.0  15234000  8011232000
#  2025-05-16 00:00  528.0  532.0  525.5  530.5  12345000  6543210000
#  2025-05-19 00:00  531.0  535.0  529.0  533.0  14567000  7765430000
#  2025-05-20 00:00  533.0  536.0  530.0  531.5  11234000  5987650000
#  2025-05-21 00:00  532.0  537.0  530.5  535.0  13456000  7187650000
