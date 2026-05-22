"""演示：板块成分股报价。

通过 MacClient 的 get_board_members() 获取指定板块的成分股实时报价，支持排序和过滤。
自动分页（每页最多 80 条）。

board_symbol 格式: 板块代码字符串，如 "881001"（酒店餐饮）。取自 BoardInfo.code 或 get_board_list()。

参数:
    board_symbol   -- 板块代码（如 "881001"）
    count          -- 请求总数（默认 100000）
    sort_type      -- 排序字段（SortType 枚举，默认 CHANGE_PCT 涨幅%）
    sort_order     -- 排序方向（SortOrder 枚举: DESC=1 降序, ASC=2 升序）
    fields         -- 字段选择（默认 None 即 PresetField.COMMON）
    exclude_flags  -- 过滤标志列表（FilterType 位掩码，可排除 ST、科创等）

SortType 枚举常用值:
    CHANGE_PCT=0x0E  涨幅%      VOLUME=0x09    成交量
    AMOUNT=0x0A      成交额     TURNOVER_RATE=0x24  换手%

SortOrder 枚举:
    NONE=0  默认      DESC=1  降序      ASC=2  升序

返回 DataFrame 列说明:
    market      int     市场代码（0=深圳, 1=上海）
    code        str     证券代码
    name        str     证券名称
    price       float   最新价
    last_close  float   昨收价
    open        float   开盘价
    high        float   最高价
    low         float   最低价
    change      float   涨跌额
    change_pct  float   涨跌幅(%)
    volume      int     成交量（股）
    amount      float   成交额
"""

from easy_tdx import MacClient, SortOrder, SortType

with MacClient.from_best_host() as c:
    # 获取行业板块 881001（酒店餐饮）的成分股，按涨幅降序
    df = c.get_board_members(
        "881001",
        count=10,
        sort_type=SortType.CHANGE_PCT,
        sort_order=SortOrder.DESC,
    )
    print(df.to_string(index=False))

# 运行结果:
# market  code   name  price  last_close  open  high   low  change  change_pct  volume    amount
#      1  603XXX  XX酒店  18.50      16.82  17.00  18.50  16.80    1.68        9.99  45200  80500000
#      0  000728  华天酒店   3.25       2.96   3.00   3.25   2.95    0.29        9.80 125600  39500000
#      0  002XXX  XX旅游  15.80      14.41  14.60  15.80  14.40    1.39        9.64  32100  49200000
#      1  600XXX  XX餐饮  12.30      11.26  11.30  12.30  11.20    1.04        9.24  28900  34600000
#      0  000XXX  XX酒店   8.90       8.16   8.20   8.90   8.10    0.74        9.07  56700  49800000
#      1  600054  黄山旅游  12.80      11.78  11.90  12.80  11.70    1.02        8.66  34500  42800000
#      0  002XXX  XX文旅  22.50      20.75  21.00  22.50  20.80    1.75        8.43  19800  43500000
#      1  601XXX  XX度假  10.50       9.72   9.80  10.50   9.70    0.78        8.02  41200  42200000
#      0  300XXX  XX餐饮   6.80       6.30   6.35   6.80   6.30    0.50        7.94  78900  52300000
#      1  600XXX  XX旅行   5.20       4.83   4.90   5.20   4.80    0.37        7.66  95600  48900000
