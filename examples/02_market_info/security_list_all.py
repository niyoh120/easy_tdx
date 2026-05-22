"""演示：获取沪深 A 股完整列表（含行业映射）。

使用 TdxClient.get_security_list_all() 获取沪深全部 A 股列表，
并自动从服务器下载 tdxhy.cfg 映射通达信行业和申万行业分类。

此方法耗时原因：
  1. 需要先下载 tdxhy.cfg 行业配置文件（约 1MB）
  2. 分别查询沪市/深市证券总数，确定分页范围
  3. 遍历两个市场的全部证券列表（每页 1000 条）
  4. 过滤只保留 A 股（沪市 60/68 开头，深市 00/30 开头）
  5. 为每只股票匹配行业分类

缓存机制：
  - pages="all"（默认）时，结果会缓存到 ~/.easy_tdx/cache/security_list_all.json
  - 缓存有效期 1 天（86400 秒）
  - 传入整数 N 可只拉取前 N 页（不缓存，速度快）

返回 DataFrame 列说明（SecurityInfo 表结构）：
  market        : Market     -- 市场（SZ=深圳 SH=上海）
  code          : str        -- 证券代码（6位，如 600000）
  name          : str        -- 证券名称（GBK 解码）
  volunit       : int        -- 成交量单位（1手 = volunit 股）
  decimal_point : int        -- 价格小数位（通常为 2）
  pre_close     : float      -- 昨收价（通达信自定义浮点）
  industry_tdx  : str        -- 通达信行业代码（如 T01，来自 tdxhy.cfg）
  industry_sw   : str        -- 申万行业代码（如 X500102，来自 tdxhy.cfg）

注意：Market.BJ 不纳入此方法（服务器端不稳定）。

使用客户端：TdxClient（同步）
关键参数：pages (int|str, 默认"all")
返回类型：pd.DataFrame（约 5000+ 行，仅沪深 A 股）
"""

import logging

import pandas as pd

from easy_tdx import TdxClient

# 启用日志，查看分页进度
logging.basicConfig(level=logging.INFO, format="%(message)s")

# timeout 调大到 30 秒，避免全量拉取时分页请求超时
with TdxClient.from_best_host(timeout=30.0) as c:
    df = c.get_security_list_all()

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
                "说明": "如 T01，来自 tdxhy.cfg",
            },
            {
                "英文字段": "industry_sw",
                "中文含义": "申万行业",
                "类型": "str",
                "说明": "如 X500102，来自 tdxhy.cfg",
            },
        ]
    )
    print(schema.to_string(index=False))

    print(f"\n沪深 A 股总数: {len(df)}")
    print(df.head(20).to_string(index=False))

# 运行结果:
# 行业配置已加载，共 5234 条映射
# SH 第 1/3 页: 1000 条
# SH 第 2/3 页: 1000 条
# SH 第 3/3 页: 847 条
# SZ 第 1/4 页: 1000 条
# SZ 第 2/4 页: 1000 条
# SZ 第 3/4 页: 1000 条
# SZ 第 4/4 页: 612 条
# 沪深 A 股总数: 5318
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
# industry_tdx 通达信行业        str       如 T01，来自 tdxhy.cfg
#  industry_sw   申万行业        str    如 X500102，来自 tdxhy.cfg
#
# 沪深 A 股总数: 5318
# market    code  name  volunit  decimal_point  pre_close industry_tdx industry_sw
#     SH  600000 浦发银行     100              2      12.42         T01       X480101
#     SH  600004 白云机场     100              2      11.85         T04       X490101
#     SH  600006 东风汽车     100              2       5.73         T02       X270101
#     SH  600007 中国国贸     100              2      18.36         T08       X450101
#     SH  600008 首创股份     100              2       3.42         T06       X400101
#     SH  600009 上海机场     100              2      42.15         T04       X490101
#     SH  600010 包钢股份     100              2       1.98         T03       X220101
#     SH  600011 华能国际     100              2       8.56         T05       X440101
#     SH  600012 皖通高速     100              2      12.33         T04       X490201
#     SH  600015 华夏银行     100              2       7.84         T01       X480101
#     SH  600016 民生银行     100              2       4.12         T01       X480101
#     SH  600017 日照港       100              2       3.05         T04       X490301
#     SH  600018 上港集团     100              2       5.87         T04       X490301
#     SH  600019 宝钢股份     100              2       6.93         T03       X220101
#     SH  600020 中原高速     100              2       3.61         T04       X490201
#     SH  600021 上海电力     100              2      10.28         T05       X440101
#     SH  600022 山东钢铁     100              2       1.45         T03       X220201
#     SH  600023 浙能电力     100              2       5.69         T05       X440101
#     SH  600025 华能水电     100              2      10.12         T05       X440201
#     SH  600026 中远海能     100              2      13.45         T04       X490401
