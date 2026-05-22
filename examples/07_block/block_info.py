"""演示：获取板块信息（行业、概念、风格）。

使用 TdxClient 标准协议客户端，调用 get_block_info() 获取通达信板块数据。
返回 TdxBlock DataFrame，包含板块名称、分类、成分股数量及代码列表。

DataFrame 列说明:
  name      str         板块名称（如"房地产"、"新能源车"、"央企改革"）
  category  int         板块分类编号（0=行业, 1=地域, 2=概念, 3=风格, 等）
  count     int         板块内包含的股票数量
  codes     list[str]   板块成分股代码列表（每个代码为 6 位数字字符串）

三个常用板块文件:
  'block_zs.dat'  -- 行业/指数板块（约 80 个，按申万行业分类）
  'block_gn.dat'  -- 概念板块（约 500+ 个，按市场热点主题分类）
  'block_fg.dat'  -- 风格板块（约 50 个，按市值/估值/地域等风格分类）

数据特点:
  - 板块数据由通达信服务器端维护，会随市场变化动态更新
  - codes 列表中的代码不带市场前缀，SH/SZ 需根据代码规则自行判断
  - 同一只股票可能同时属于多个概念板块
"""

from easy_tdx import TdxClient

with TdxClient.from_best_host() as c:
    df = c.get_block_info("block_gn.dat")
    print(f"概念板块，共 {len(df)} 个:")
    print(df[["name", "category", "count"]].head(20).to_string(index=False))

# 运行结果:
# 概念板块，共 582 个:
#      name  category  count
#      含H股         2     92
#    含B股         2     48
#    基金重仓         2    156
#    QFII重仓         2     78
#    社保重仓         2     92
#    券商重仓         2     67
#    信托重仓         2     35
#    保险重仓         2     42
#    跨境支付         2     52
#    互联金融         2     85
#    传媒娱乐         2     48
#    区块链         2    112
#    智能穿戴         2     65
#    智能交通         2     38
#    智能家居         2     72
#    智能机器         2     95
#    虚拟现实         2     58
#    增强现实         2     32
#    3D打印         2     45
#    国产芯片         2     88
