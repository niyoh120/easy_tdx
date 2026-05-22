"""演示：市场异动数据。

通过 MacClient 的 get_unusual() 获取全市场的异动股票数据。

参数:
    market  -- 市场代码（Market.SH / Market.SZ）
    start   -- 起始偏移（默认 0）
    count   -- 请求数量（默认 0，即 600）

UnusualItem dataclass 字段:
    index         int     异动序号
    market        int     市场代码
    code          str     证券代码
    name          str     证券名称
    time          time    异动时间
    desc          str     异动描述（如 "5分钟涨幅>3%"、"快速拉升"、"大笔买入"）
    value         str     异动数值（如 "3.52%"、"5000手"）
    unusual_type  int     异动类型代码（1=5分钟涨幅, 2=5分钟跌幅, 3=快速拉升, 4=大笔成交等）

返回 DataFrame 列说明:
    index         int      异动序号
    market        int      市场代码
    code          str      证券代码
    name          str      证券名称
    time          object   异动时间（HH:MM:SS 格式）
    desc          str      异动描述
    value         str      异动数值
    unusual_type  int      异动类型代码
"""

from easy_tdx import MacClient, Market

with MacClient.from_best_host() as c:
    # 获取沪市异动数据（最近 20 条）
    df = c.get_unusual(Market.SH, count=20)
    print(df.to_string(index=False))

# 运行结果:
#  index  market  code   name       time          desc       value  unusual_type
#      1       1  600XXX  XX科技  09:45:00     5分钟涨幅>3%        3.52%             1
#      2       1  601XXX  XX银行  09:52:00     5分钟涨幅>3%        3.15%             1
#      3       1  600XXX  XX能源  10:05:00     5分钟跌幅>3%       -3.28%             2
#      4       1  603XXX  XX医药  10:18:00     快速拉升            5.20%             3
#      5       1  600XXX  XX电子  10:30:00     大笔买入         5000手             4
#      6       1  601XXX  XX钢铁  10:45:00     5分钟涨幅>3%        3.80%             1
#      7       1  600XXX  XX化工  11:00:00     5分钟跌幅>3%       -3.65%             2
#      8       1  603XXX  XX通信  13:15:00     快速拉升            4.85%             3
#      9       1  600XXX  XX地产  13:30:00     大笔买入         3000手             4
#     10       1  601XXX  XX汽车  13:45:00     5分钟涨幅>3%        3.42%             1
