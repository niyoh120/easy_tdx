"""演示：按市场分类获取排序报价列表。

通过 MacClient 的 get_stock_quotes_list() 获取指定分类的股票报价，支持排序。

Category 枚举常用值:
    SH=0    上证A        SZ=2    深证A        A=6     全部A股
    B=7     B股          KCB=8   科创板       BJ=12   北证A
    CYB=14  创业板       HGT     沪股通       SGT     深股通

SortType 枚举常用值:
    CHANGE_PCT=0x0E   涨幅%      VOLUME=0x09    成交量
    AMOUNT=0x0A       成交额     TURNOVER_RATE=0x24  换手%
    VOL_RATIO=0x23    量比       SPEED_PCT=0x2E     涨速%

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

from easy_tdx import Category, MacClient, SortOrder, SortType

with MacClient.from_best_host() as c:
    # 全部 A 股，按涨幅降序，取前 10 名
    print("=== 全部A股涨幅前10 ===")
    df = c.get_stock_quotes_list(
        Category.A,
        count=10,
        sort_type=SortType.CHANGE_PCT,
        sort_order=SortOrder.DESC,
    )
    print(df.to_string(index=False))

    # 科创板，按涨幅降序，取前 10 名
    print("\n=== 科创板涨幅前10 ===")
    df = c.get_stock_quotes_list(
        Category.KCB,
        count=10,
        sort_type=SortType.CHANGE_PCT,
        sort_order=SortOrder.DESC,
    )
    print(df.to_string(index=False))

# 运行结果:
# === 全部A股涨幅前10 ===
# market  code   name  price  last_close  open  high   low  change  change_pct   volume     amount
#      1  603XXX  XX科技  28.50      25.91  26.00  28.50  26.00    2.59       10.00  125800  345600000
#      0  300XXX  XX电子  45.20      41.09  42.00  45.20  41.50    4.11       10.00   89000  388000000
#      1  600XXX  XX股份  18.30      16.64  17.00  18.30  16.80    1.66        9.98   98700  175000000
#      0  002XXX  XX新材  33.60      30.55  31.00  33.60  30.80    3.05        9.98   67800  220000000
#      0  301XXX  XX医药  52.80      48.02  48.50  52.80  48.00    4.78        9.96   45600  230000000
#      1  601XXX  XX银行   6.25       5.69   5.75   6.25   5.70    0.56        9.84  234500  142000000
#      0  000XXX  XX能源  12.45      11.34  11.50  12.45  11.40    1.11        9.79  156000  189000000
#      0  300XXX  XX科技  27.90      25.42  25.80  27.90  25.50    2.48        9.76  112300  305000000
#      1  600XXX  XX电力   8.95       8.16   8.20   8.95   8.15    0.79        9.68  198700  173000000
#      0  002XXX  XX化学  19.80      18.05  18.20  19.80  18.10    1.75        9.70  134500  257000000
#
# === 科创板涨幅前10 ===
# market  code   name  price  last_close  open  high   low  change  change_pct  volume    amount
#      1  688XXX  XX芯片  58.30      53.00  54.00  58.30  53.50    5.30       10.00  34500  192000000
#      1  688XXX  XX生物  42.10      38.27  39.00  42.10  38.50    3.83       10.00  28900  117000000
#      1  688XXX  XX光电  35.60      32.36  33.00  35.60  32.50    3.24       10.01  42100  145000000
#      1  688XXX  XX半导体 91.50      83.18  84.50  91.50  83.50    8.32        9.99  19800  172000000
#      1  688XXX  XX医药  67.80      61.64  62.00  67.80  62.00    6.16        9.99  15600  101000000
#      1  688XXX  XX软件  43.20      39.27  40.00  43.20  39.50    3.93       10.01  31200  131000000
#      1  688XXX  XX材料  28.90      26.27  27.00  28.90  26.50    2.63       10.01  52300  144000000
#      1  688XXX  XX装备  55.40      50.36  51.00  55.40  50.50    5.04        9.99  23400  126000000
#      1  688XXX  XX电子  72.30      65.73  66.50  72.30  66.00    6.57        9.99  17800  124000000
#      1  688XXX  XX通信  39.50      35.91  36.50  39.50  35.80    3.59        9.99  38700  148000000
