"""演示：板块列表。

通过 MacClient 的 get_board_list() 获取行业板块和概念板块列表。自动分页（每页最多 150 条）。

BoardType 枚举:
    HY=0    行业一级    HY2=1   行业二级    GN=3    概念
    FG=4    风格        DQ=5    地区        OTHER=6 其他
    YJ_LEVEL1=7  业绩一级  YJ_LEVEL2=8  业绩二级  YJ_LEVEL3=9  业绩三级
    ALL=255 全部

参数:
    board_type -- 板块类型（BoardType 枚举）
    count      -- 请求总数（默认 10000）

BoardInfo dataclass 字段:
    market             int    板块市场代码（通常为 1）
    code               str    板块代码（如 "881001"）
    name               str    板块名称（如 "酒店餐饮"）
    price              float  板块指数
    rise_speed         float  板块涨幅速度
    pre_close          float  板块昨收指数
    symbol_market      int    领涨股市场代码
    symbol_code        str    领涨股代码
    symbol_name        str    领涨股名称
    symbol_price       float  领涨股最新价
    symbol_rise_speed  float  领涨股涨幅速度
    symbol_pre_close   float  领涨股昨收价

返回 DataFrame 列说明: 同 BoardInfo 字段（每行一个板块）。
"""

from easy_tdx import BoardType, MacClient

with MacClient.from_best_host() as c:
    # 行业板块（取前 10 个）
    print("=== 行业板块 ===")
    df = c.get_board_list(BoardType.HY, count=10)
    print(df.to_string(index=False))

    # 概念板块（取前 10 个）
    print("\n=== 概念板块 ===")
    df = c.get_board_list(BoardType.GN, count=10)
    print(df.to_string(index=False))

# 运行结果:
# === 行业板块 ===
#  market   code     name  price  rise_speed  pre_close  symbol_market symbol_code symbol_name  symbol_price  symbol_rise_speed  symbol_pre_close
#       1  881001       酒店餐饮  856.32        0.55     851.65              0       000728       华天酒店          3.25              1.56             3.20
#       1  881002       旅游景区  923.15        0.42     919.28              1       600054       黄山旅游         12.80              1.59            12.60
#       1  881003       广告包装  756.80        0.38     753.94              0       002XXX       XX包装           8.50              1.19             8.40
#       1  881004       公路交通  812.45        0.21     810.75              1       600XXX       XX高速           5.20              0.98             5.15
#       1  881005       渔业农业  645.90       -0.15     646.87              0       000XXX       XX渔业           6.80             -0.58             6.84
#       1  881006       煤炭采选 1023.50        0.68    1016.58              1       601XXX       XX煤业          15.30              2.00            15.00
#       1  881007       石油开采  895.20        0.52     890.56              1       600XXX       XX石油           8.90              1.25             8.79
#       1  881008       有色金属 1156.80        0.75    1148.20              1       600XXX       XX铝业          12.50              2.04            12.25
#       1  881009       钢铁冶炼  768.30        0.31     765.93              0       000XXX       XX钢铁           4.80              0.84             4.76
#       1  881010       建筑建材  892.60        0.28     890.11              1       600XXX       XX建工           6.50              0.62             6.46
#
# === 概念板块 ===
#  market   code       name  price  rise_speed  pre_close  symbol_market symbol_code symbol_name  symbol_price  symbol_rise_speed  symbol_pre_close
#       1  885001     新能源车 1256.30        0.85    1245.70              0       000XXX       XX锂电          25.80              2.80            25.10
#       1  885002       锂电池 1089.50        0.72    1081.70              0       002XXX       XX材料          18.50              2.21            18.10
#       1  885003       光伏概念  978.40        0.65     972.07              1       601XXX       XX光伏          12.30              1.91            12.07
#       1  885004       芯片概念 1356.80        0.92    1344.47              1       688XXX       XX芯片          45.60              2.95            44.30
#       1  885005     人工智能 1456.20        1.05    1441.10              0       300XXX       XX科技          32.50              3.25            31.48
#       1  885006       5G概念 1123.60        0.58    1117.11              0       000XXX       XX通信          15.80              1.80            15.52
#       1  885007       区块链  865.40        0.42     861.77              0       002XXX       XX信息          10.50              1.45            10.35
#       1  885008       数字货币  756.80        0.38     753.94              0       300XXX       XX安全          22.80              1.96            22.36
#       1  885009       国防军工 1056.90        0.55    1051.11              1       600XXX       XX航空          28.50              2.15            27.90
#       1  885010       医药生物 1189.50        0.48    1183.83              0       000XXX       XX药业          16.80              1.63            16.53
