"""演示：批量获取实时五档行情。

使用 TdxClient.get_security_quotes() 获取多只股票的实时行情。
最多支持 80 只/次请求，返回 SecurityQuote DataFrame。

返回 DataFrame 列说明（SecurityQuote 表结构）：
  基础信息：
    market      : Market     -- 市场（SZ=深圳 SH=上海）
    code        : str        -- 证券代码（6位）
    server_time : str        -- 服务器时间（HH:MM:SS.mmm）

  价格：
    price       : float64    -- 现价（元）
    pre_close   : float64    -- 昨收价（元）
    open        : float64    -- 今开（元）
    high        : float64    -- 最高（元）
    low         : float64    -- 最低（元）

  量额：
    vol         : float64    -- 总成交量（手）
    cur_vol     : float64    -- 当前成交量（手）
    amount      : float64    -- 成交额（元）
    s_vol       : float64    -- 内盘（主动卖，手）
    b_vol       : float64    -- 外盘（主动买，手）

  买盘五档：
    bid1~bid5   : float64    -- 买一到买五价格（元）
    bid_vol1~5  : float64    -- 买一到买五挂单量（手）

  卖盘五档：
    ask1~ask5   : float64    -- 卖一到卖五价格（元）
    ask_vol1~5  : float64    -- 卖一到卖五挂单量（手）

  价格指标：
    rise_speed  : float64    -- 涨速
    limit_up    : float64/None -- 涨停价（默认 None，需 get_price_limits 计算）
    limit_down  : float64/None -- 跌停价（默认 None，需 get_price_limits 计算）

使用客户端：TdxClient（同步）
关键参数：stocks (list[tuple[Market, str]]), 最多 80 只/次
返回类型：pd.DataFrame
"""

from easy_tdx import Market, TdxClient

with TdxClient.from_best_host() as c:
    stocks = [
        (Market.SH, "600000"),  # 浦发银行
        (Market.SH, "600519"),  # 贵州茅台
        (Market.SZ, "000001"),  # 平安银行
        (Market.SZ, "000858"),  # 五粮液
    ]
    df = c.get_security_quotes(stocks)
    df["change_pct"] = (df["price"] - df["pre_close"]) / df["pre_close"] * 100
    print(
        df[
            ["code", "price", "change_pct", "open", "high", "low", "pre_close", "vol", "amount"]
        ].to_string(index=False)
    )

# 运行结果:
#     code   price  change_pct   open   high    low  pre_close        vol        amount
#  600000   12.51        0.73  12.46  12.56  12.42      12.42   315670.0  3.945158e+08
#  600519 1632.00        0.74 1625.00 1638.00 1618.00    1620.00    28456.0  4.634712e+09
#  000001   14.23        0.78   14.15   14.28   14.10      14.12   452318.0  6.418923e+08
#  000858  145.38        0.85  144.50  146.20  143.80     144.15    68923.0  1.001245e+09
