"""演示：服务器交易时段信息。

通过 MacClient 的 get_server_info() 获取当前服务器的交易日期和交易时段配置。

ServerSession dataclass 字段:
    today           str              当前日期（YYYYMMDD 格式）
    last_trading_day str             上一交易日（YYYYMMDD 格式）
    sessions_1      list[dict]       第一组交易时段配置，每个 dict 含:
                                         start  str   开始时间（如 "09:15"）
                                         end    str   结束时间（如 "09:20"）
                                         type   int   时段类型:
                                                      1=连续竞价, 5=集合竞价(可撤单),
                                                      6=集合竞价(不可撤单), 7=撮合
    sessions_2      list[dict]       第二组交易时段配置（结构与 sessions_1 相同）
    market_param_1  int              市场参数 1
    market_param_2  int              市场参数 2

返回 DataFrame 列说明: 同 ServerSession 字段（单行 DataFrame，sessions 为嵌套结构）。
"""

from easy_tdx import MacClient

with MacClient.from_best_host() as c:
    df = c.get_server_info()
    print(df.to_string(index=False))

# 运行结果:
#       today last_trading_day                                                                                                                                                                                                                                      sessions_1                                                                                                                                                                                                                                    sessions_2  market_param_1  market_param_2
#  20250517       20250516  [{'start': '09:15', 'end': '09:20', 'type': 5}, {'start': '09:20', 'end': '09:25', 'type': 6}, {'start': '09:25', 'end': '09:30', 'type': 7}, {'start': '09:30', 'end': '11:30', 'type': 1}, {'start': '13:00', 'end': '15:00', 'type': 1}]  [{'start': '09:15', 'end': '09:20', 'type': 5}, {'start': '09:20', 'end': '09:25', 'type': 6}, {'start': '09:25', 'end': '09:30', 'type': 7}, {'start': '09:30', 'end': '11:30', 'type': 1}, {'start': '13:00', 'end': '15:00', 'type': 1}]              192           192
