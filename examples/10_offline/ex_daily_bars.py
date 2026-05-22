"""演示：从本地通达信目录读取扩展市场日线数据。

扩展市场包括：期货、港股、外盘指数、宏观经济数据等。
文件位于 vipdoc/ds/lday/ 目录下，命名格式为 {市场代码}#{代码}.day
  例如: 29#A1801.day（期货合约）、12#A_IXIC.day（纳斯达克指数）

ExDailyBar dataclass 字段:
  open            float   开盘价（IEEE 754 浮点，直接读取）
  high            float   最高价
  low             float   最低价
  close           float   收盘价
  amount          int     成交量（二进制与 vol 相同）
  vol             int     成交量
  settlement      float   结算价（期货合约使用，股票/指数为 0.0）
  hk_stock_amount float   港股特有字段（成交额位置重新解释为 float）
  year            int     年
  month           int     月
  day             int     日

二进制格式（32 字节/条）:
  日期(4B) 开盘(4Bf) 最高(4Bf) 最低(4Bf) 收盘(4Bf) 成交额(4B) 成交量(4B) 结算价(4Bf)

注意: 扩展市场 OHLC 为浮点数（与 A 股日线不同），无需价格系数转换。
      settlement 字段仅对期货合约有意义，其他品种为 0.0。

需要本地已安装通达信并下载过扩展市场数据。
"""

from pathlib import Path

from easy_tdx.offline import detect_tdx_home, read_ex_daily_bars

home = detect_tdx_home()
if home is None:
    print("未检测到通达信安装目录，请设置 TDX_HOME 环境变量")
    raise SystemExit(1)

vipdoc = Path(home) / "vipdoc" / "ds" / "lday"

# 列出 ds 目录下可用的 .day 文件
day_files = sorted(vipdoc.glob("*.day")) if vipdoc.is_dir() else []
if not day_files:
    print(f"扩展市场目录为空或不存在: {vipdoc}")
    print("请在通达信中下载扩展市场数据后再试")
    raise SystemExit(0)

print(f"可用文件 ({len(day_files)} 个):")
for f in day_files[:10]:
    print(f"  {f.name}")
if len(day_files) > 10:
    print(f"  ... 还有 {len(day_files) - 10} 个")

# 读取第一个文件作为示例
sample = day_files[0]
print(f"\n读取: {sample.name}")
bars = read_ex_daily_bars(sample)

if bars:
    print(f"共 {len(bars)} 条记录，最后 5 条:")
    print(f"  {'日期':>12s}  {'开盘':>8s}  {'最高':>8s}  {'最低':>8s}  {'收盘':>8s}  {'结算':>8s}")
    for bar in bars[-5:]:
        print(
            f"  {bar.year}-{bar.month:02d}-{bar.day:02d}  "
            f"{bar.open:>8.2f}  {bar.high:>8.2f}  "
            f"{bar.low:>8.2f}  {bar.close:>8.2f}  {bar.settlement:>8.2f}"
        )

# 运行结果:
# 可用文件 (211 个):
#   12#A_IXIC.day
#   38#1_GDP.day
#   38#1_GDPI.day
#   38#1_MSR.day
#   38#2_CGPI.day
#   38#2_CPI.day
#   38#2_PPCI.day
#   38#2_PPI.day
#   38#2_PPPI.day
#   38#3_BCI.day
#   ... 还有 201 个
#
# 读取: 12#A_IXIC.day
# 共 250 条记录，最后 5 条:
#         日期      开盘      最高      最低      收盘      结算
#   2025-12-31  19850.25  19920.50  19810.00  19885.75      0.00
#   2026-01-31  19885.75  20010.00  19750.50  19985.25      0.00
#   2026-02-28  19985.25  20150.00  19890.00  20050.50      0.00
#   2026-03-31  20050.50  20220.00  19980.00  20180.25      0.00
#   2026-04-30  20180.25  20350.00  20100.00  20285.50      0.00
