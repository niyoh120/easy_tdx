"""演示：K 线偏移信息。

通过 MacClient 的 get_kline_offset() 获取 K 线数据的偏移量信息，用于确定当前可用
K 线总数和数据偏移位置。通常用于确认服务器上的 K 线数据总量。

参数:
    offset  -- 偏移量（默认 0）
    count   -- 请求数量（默认 128000）

返回 DataFrame 列说明:
    total     int   服务器上可用的 K 线总数
    returned  int   本次返回的条数
"""

from easy_tdx import MacClient

with MacClient.from_best_host() as c:
    df = c.get_kline_offset()
    print(df.to_string(index=False))

# 运行结果:
#  total  returned
# 128000         2
