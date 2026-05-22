"""演示：获取市场证券总数。

使用 TdxClient 标准协议客户端，查询指定市场的证券总数。
Market 枚举: SH=1(上海), SZ=0(深圳), BJ=2(北京)

Market 枚举说明：
  Market.SZ = 0  -- 深圳证券交易所（深市主板、中小板、创业板）
  Market.SH = 1  -- 上海证券交易所（沪市主板、科创板）
  Market.BJ = 2  -- 北京证券交易所（北交所，原新三板精选层）

返回: int -- 证券总数（含股票、基金、债券、指数等所有品种）

注意: Market.BJ 的结果可能不稳定（服务器端问题），不建议在生产中依赖。

使用客户端：TdxClient（同步）
关键参数：market (Market 枚举)
返回类型：int
"""

from easy_tdx import Market, TdxClient

with TdxClient.from_best_host() as c:
    sh_count = c.get_security_count(Market.SH)
    sz_count = c.get_security_count(Market.SZ)
    print(f"沪市证券总数: {sh_count}")
    print(f"深市证券总数: {sz_count}")

# 运行结果:
# 沪市证券总数: 2847
# 深市证券总数: 3612
