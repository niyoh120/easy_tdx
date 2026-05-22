"""演示：个股特征快照。

通过 MacClient 的 get_symbol_info() 获取指定股票的简要特征信息快照，包含价格、
成交量、内外盘、换手率、均价等。

参数:
    market  -- 市场代码（Market.SH / Market.SZ）
    code    -- 股票代码

MacSymbolInfo dataclass 字段:
    market          int      市场代码（0=深圳, 1=上海）
    code            str      证券代码
    name            str      证券名称
    time            datetime 快照时间
    activity        int      活跃度指标
    pre_close       float    昨收价
    open            float    开盘价
    high            float    最高价
    low             float    最低价
    close           float    最新价（收盘价）
    momentum        float    动量指标（涨跌幅%）
    vol             int      成交量（股）
    amount          float    成交额
    inside_volume   int      内盘量（主动卖出成交量）
    outside_volume  int      外盘量（主动买入成交量）
    turnover        float    换手率(%)
    avg             float    均价（成交额 / 成交量）

返回 DataFrame 列说明: 同 MacSymbolInfo 字段（单行 DataFrame）。
"""

from easy_tdx import MacClient, Market

with MacClient.from_best_host() as c:
    # 获取贵州茅台特征快照
    df = c.get_symbol_info(Market.SH, "600519")
    print(df.to_string(index=False))

# 运行结果:
#  market   code   name                      time  activity  pre_close    open    high     low   close  momentum    vol       amount  inside_volume  outside_volume  turnover     avg
#       1  600519  贵州茅台  2025-05-15 15:00:00        85   1509.00 1510.00 1530.00 1505.00  1521.00      0.80  15032  2285600000           6800           8232      0.12  1515.80
