"""演示：计算个股涨跌停价格。

使用 TdxClient 标准协议客户端，调用 get_price_limits() 根据股票板块规则计算涨跌停价。
返回 tuple[float, float] -- (涨停价, 跌停价)，无涨跌幅限制时返回 (None, None)。

涨跌停价计算规则（基于 compute_price_limits）:
  普通A股:     昨收价 x (1 + 10%) / 昨收价 x (1 - 10%)
  ST / *ST:    昨收价 x (1 + 5%)  / 昨收价 x (1 - 5%)
  科创板(688): 昨收价 x (1 + 20%) / 昨收价 x (1 - 20%)
  创业板(300/301): 昨收价 x (1 + 20%) / 昨收价 x (1 - 20%)
  北交所(43/83/87/92): 昨收价 x (1 + 30%) / 昨收价 x (1 - 30%)

特殊情况:
  - 上市首日（及科创板/创业板前 5 个交易日）无涨跌幅限制，返回 (None, None)
  - 指数/板块类代码无涨跌幅限制
  - 结果按四舍五入保留两位小数
"""

from easy_tdx import Market, TdxClient

CODE = "600519"
NAME = "贵州茅台"

with TdxClient.from_best_host() as c:
    quotes = c.get_security_quotes([(Market.SH, CODE)])
    if not quotes.empty:
        q = quotes.iloc[0]
        limit_up, limit_down = c.get_price_limits(Market.SH, CODE, NAME, q["pre_close"])
        print(f"代码: {CODE}  名称: {NAME}")
        print(f"昨收: {q['pre_close']}")
        print(f"涨停价: {limit_up}")
        print(f"跌停价: {limit_down}")

# 运行结果:
# 代码: 600519  名称: 贵州茅台
# 昨收: 1498.00
# 涨停价: 1647.80
# 跌停价: 1348.20
