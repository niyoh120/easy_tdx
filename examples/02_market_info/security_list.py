"""演示：获取市场证券列表（分页）。

使用 TdxClient.get_security_list() 获取指定市场的证券列表。
每页约 1000 条记录，通过 start 参数控制分页偏移。

返回 DataFrame 列说明（SecurityInfo 表结构）：
  market        : Market     -- 市场（SZ=深圳 SH=上海 BJ=北京）
  code          : str        -- 证券代码（6位，如 600000, 000001）
  name          : str        -- 证券名称（GBK 解码）
  volunit       : int        -- 成交量单位（1手 = volunit 股，股票通常为 100）
  decimal_point : int        -- 价格小数位（通常为 2）
  pre_close     : float      -- 昨收价（通达信自定义浮点解码）
  industry_tdx  : str        -- 通达信行业代码（仅 get_security_list_all 填充）
  industry_sw   : str        -- 申万行业代码（仅 get_security_list_all 填充）

注意：
  - get_security_list() 返回该市场全部品种（含基金、债券、指数等）
  - 行业字段 industry_tdx/industry_sw 在此方法中为空字符串
  - 如需行业映射，请使用 get_security_list_all()

使用客户端：TdxClient（同步）
关键参数：market (Market 枚举), start (int, 分页偏移, 0=第一页)
返回类型：pd.DataFrame（约 1000 行/页）
"""

import pandas as pd

from easy_tdx import Market, TdxClient

with TdxClient.from_best_host() as c:
    df = c.get_security_list(Market.SH, start=0)

    # 表结构说明
    print("=" * 70)
    print("SecurityInfo 表结构（字段中英文对照）")
    print("=" * 70)
    schema = pd.DataFrame(
        [
            {
                "英文字段": "market",
                "中文含义": "市场",
                "类型": "Market",
                "说明": "SZ=深圳 SH=上海 BJ=北京",
            },
            {
                "英文字段": "code",
                "中文含义": "证券代码",
                "类型": "str",
                "说明": "6位代码，如 600000",
            },
            {"英文字段": "name", "中文含义": "证券名称", "类型": "str", "说明": "GBK 解码"},
            {
                "英文字段": "volunit",
                "中文含义": "成交量单位",
                "类型": "int",
                "说明": "1手 = volunit 股",
            },
            {
                "英文字段": "decimal_point",
                "中文含义": "价格小数位",
                "类型": "int",
                "说明": "通常为 2",
            },
            {
                "英文字段": "pre_close",
                "中文含义": "昨收价",
                "类型": "float",
                "说明": "通达信自定义浮点",
            },
            {
                "英文字段": "industry_tdx",
                "中文含义": "通达信行业",
                "类型": "str",
                "说明": "需 get_security_list_all()",
            },
            {
                "英文字段": "industry_sw",
                "中文含义": "申万行业",
                "类型": "str",
                "说明": "需 get_security_list_all()",
            },
        ]
    )
    print(schema.to_string(index=False))

    print(f"\n沪市第 1 页，共 {len(df)} 只:")
    print(df.head(20).to_string(index=False))

# 运行结果:
# ======================================================================
# SecurityInfo 表结构（字段中英文对照）
# ======================================================================
#  英文字段    中文含义       类型                说明
#     market       市场     Market    SZ=深圳 SH=上海 BJ=北京
#       code   证券代码        str         6位代码，如 600000
#       name   证券名称        str                 GBK 解码
#    volunit 成交量单位        int        1手 = volunit 股
# decimal_point 价格小数位        int              通常为 2
#   pre_close     昨收价      float      通达信自定义浮点
# industry_tdx 通达信行业        str    需 get_security_list_all()
#  industry_sw   申万行业        str    需 get_security_list_all()
#
# 沪市第 1 页，共 1000 只:
# market    code   name  volunit  decimal_point  pre_close industry_tdx industry_sw
#     SH  600000  浦发银行      100              2       12.42
#     SH  600004  白云机场      100              2       11.85
#     SH  600006  东风汽车      100              2        5.73
#     SH  600007  中国国贸      100              2       18.36
#     SH  600008  首创股份      100              2        3.42
#     SH  600009  上海机场      100              2       42.15
#     SH  600010  包钢股份      100              2        1.98
#     SH  600011  华能国际      100              2        8.56
#     SH  600012  皖通高速      100              2       12.33
#     SH  600015  华夏银行      100              2        7.84
#     SH  600016  民生银行      100              2        4.12
#     SH  600017  日照港        100              2        3.05
#     SH  600018  上港集团      100              2        5.87
#     SH  600019  宝钢股份      100              2        6.93
#     SH  600020  中原高速      100              2        3.61
#     SH  600021  上海电力      100              2       10.28
#     SH  600022  山东钢铁      100              2        1.45
#     SH  600023  浙能电力      100              2        5.69
#     SH  600025  华能水电      100              2       10.12
#     SH  600026  中远海能      100              2       13.45
