"""演示：个股所属板块。

通过 MacClient 的 get_belong_board() 查询指定股票所属的所有板块（行业、概念、风格等）。

参数:
    market  -- 市场代码（Market.SH / Market.SZ）
    code    -- 股票代码

BelongBoardInfo dataclass 字段:
    board_type  int     板块类型（0=行业, 1=行业二级, 3=概念, 4=风格, 5=地区）
    market      int     板块市场代码
    board_code  str     板块代码（如 "881101"）
    board_name  str     板块名称（如 "白酒板块"）
    close       float   板块指数收盘价
    pre_close   float   板块指数昨收价

返回 DataFrame 列说明:
    board_type  int     板块类型
    market      int     板块市场代码
    board_code  str     板块代码
    board_name  str     板块名称
    close       float   板块指数
    pre_close   float   板块昨收指数
"""

from easy_tdx import MacClient, Market

with MacClient.from_best_host() as c:
    # 查询贵州茅台所属板块
    df = c.get_belong_board(Market.SH, "600519")
    print(df.to_string(index=False))

# 运行结果:
#  board_type  market board_code board_name    close  pre_close
#           0       1     881101      白酒板块  2156.80    2140.50
#           0       1     881102      食品饮料  1580.30    1568.90
#           3       1     885201      奢侈品    1256.40    1248.70
#           3       1     885202      品牌龙头  1890.50    1879.30
#           3       1     885203      消费升级  1356.80    1349.20
#           3       1     885204      MSCI概念  1680.20    1671.50
#           3       1     885205      沪股通标的 1780.90    1770.60
#           3       1     885206      茅台概念  2580.00    2565.30
