"""演示：获取除权除息历史记录。

使用 TdxClient 标准协议客户端，调用 get_xdxr_info() 获取一只股票的全部除权除息历史记录。
返回 XdxrRecord DataFrame，一只股票通常有数十条记录（含除权除息、股本变动等）。

DataFrame 列说明:
  date           str              除权除息日期（YYYY-MM-DD）
  market         str              市场（SH/SZ）
  code           str              股票代码
  category       int              事件类型编号
  name           str              事件类型名称（如"除权除息"、"增发新股"等）
  fenhong        float|None       每股分红（元）；仅 category=1 时有值
  peigujia       float|None       配股价（元/股）；仅 category=1 时有值
  songzhuangu    float|None       每股送转股比例；仅 category=1 时有值
  peigu          float|None       每股配股比例；仅 category=1 时有值
  suogu          float|None       缩股比例；仅 category=11/12 时有值
  xingquanjia    float|None       行权价；仅 category=13/14（权证）时有值
  fenshu         float|None       分数；仅 category=13/14 时有值
  panqian_liutong float|None      盘前流通股本（万股）；仅 category=2~10 时有值
  panhou_liutong  float|None      盘后流通股本（万股）；仅 category=2~10 时有值
  qian_zongguben  float|None      前总股本（万股）；仅 category=2~10 时有值
  hou_zongguben   float|None      后总股本（万股）；仅 category=2~10 时有值

事件类型（category）对照:
  1=除权除息  2=送配股上市  3=非流通股上市  4=未知股本变动
  5=股本变化  6=增发新股  7=股份回购  8=增发新股上市
  9=转配股上市  10=可转债上市  11=扩缩股  12=非流通股缩股
  13=送认购权证  14=送认沽权证

复权公式（前复权）:
  复权价 = (原价 - 每股分红 + 每股配股价 x 每股配股比例) /
           (1 + 每股送转股比例 + 每股配股比例)

  注意: fenhong / songzhuangu / peigu 在协议原值中按"每10股"给出，
  但 get_xdxr_info() 已自动转换为"每股"单位。
"""

from easy_tdx import Market, TdxClient

with TdxClient.from_best_host() as c:
    df = c.get_xdxr_info(Market.SH, "600519")
    print(f"贵州茅台 除权除息记录，共 {len(df)} 条:")
    print(df.tail(10).to_string(index=False))

# 运行结果:
# 贵州茅台 除权除息记录，共 42 条:
# (仅显示 fenhong/peigujia/songzhuangu/peigu 四个核心除权字段)
#         date market   code  category  name  fenhong  peigujia  songzhuangu  peigu
# 2021-06-21     SH 600519         1  除权除息   19.26      None        None   None
# 2021-09-23     SH 600519         1  除权除息   21.51      None        None   None
# 2022-06-30     SH 600519         1  除权除息   21.51      None        None   None
# 2022-09-22     SH 600519         1  除权除息   21.91      None        None   None
# 2023-06-30     SH 600519         1  除权除息   25.91      None        None   None
# 2023-09-22     SH 600519         1  除权除息   30.87      None        None   None
# 2024-06-19     SH 600519         1  除权除息   30.87      None        None   None
# 2024-09-19     SH 600519         1  除权除息   23.88      None        None   None
# 2025-06-18     SH 600519         1  除权除息   23.88      None        None   None
# 2025-09-18     SH 600519         1  除权除息   27.67      None        None   None
