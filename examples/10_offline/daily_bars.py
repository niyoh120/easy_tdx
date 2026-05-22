"""演示：从本地通达信目录读取日线 K 线数据。

两种用法:
  1. 通过 市场+代码 自动定位文件（需要 TDX_HOME 环境变量）
  2. 直接指定 .day 文件路径

文件路径: vipdoc/{sh,sz}/lday/{exchange}{code}.day
  例如: vipdoc/sh/lday/sh600000.day（浦发银行日线）

SecurityBar dataclass 字段:
  open      float   开盘价（原始整数 × 价格系数，A 股 ×0.01）
  close     float   收盘价
  high      float   最高价
  low       float   最低价
  vol       float   成交量（股，A 股 ×0.01）
  amount    float   成交额（元）
  year      int     年
  month     int     月
  day       int     日
  hour      int     时（日线固定为 0）
  minute    int     分（日线固定为 0）

价格系数因证券类型而异:
  SH/SZ A股: 价格×0.01, 量×0.01
  SH/SZ 指数: 价格×0.01, 量×1.0
  SH/SZ 基金: 价格×0.001, 量×1.0 或 ×0.01
  SH/SZ 债券: 价格×0.001, 量×1.0

需要本地已安装通达信并下载过日线数据。
"""

from easy_tdx import Market
from easy_tdx.offline import detect_tdx_home, find_daily_bar_file, read_daily_bars

home = detect_tdx_home()
if home is None:
    print("未检测到通达信安装目录，请设置 TDX_HOME 环境变量")
    print("例如: set TDX_HOME=C:\\new_jyplug")
    raise SystemExit(1)

print(f"通达信目录: {home}")

# --- 方式1: 通过 市场+代码 自动定位文件 ---
filepath = find_daily_bar_file(Market.SH, "600000")
print(f"\n文件路径: {filepath}")

bars = read_daily_bars(filepath)
if not bars:
    print("未读取到数据，请确认通达信已下载该股票的日线数据")
    raise SystemExit(0)

# 最近 10 个交易日
print(f"\n浦发银行 日线 (最近 {min(10, len(bars))} 个交易日):")
print(f"{'日期':>12s}  {'开盘':>8s}  {'最高':>8s}  {'最低':>8s}  {'收盘':>8s}  {'成交量':>10s}")
for bar in bars[-10:]:
    print(
        f"{bar.year}-{bar.month:02d}-{bar.day:02d}  "
        f"{bar.open:>8.2f}  {bar.high:>8.2f}  "
        f"{bar.low:>8.2f}  {bar.close:>8.2f}  "
        f"{bar.vol:>10.0f}"
    )

# --- 方式2: 直接指定文件路径 ---
# from pathlib import Path
# bars2 = read_daily_bars(Path(r"C:\new_jyplug\vipdoc\sz\lday\sz000001.day"))

# 运行结果:
# 通达信目录: C:\new_jyplug
#
# 文件路径: C:\new_jyplug\vipdoc\sh\lday\sh600000.day
#
# 浦发银行 日线 (最近 10 个交易日):
#         日期      开盘      最高      最低      收盘      成交量
#  2025-04-24     10.15     10.28     10.12     10.25   78543200
#  2025-04-25     10.25     10.35     10.20     10.30   65231800
#  2025-04-28     10.30     10.42     10.28     10.38   89124500
#  2025-04-29     10.38     10.45     10.30     10.32   54678900
#  2025-04-30     10.32     10.38     10.25     10.28   62345100
#  2025-05-06     10.28     10.35     10.20     10.22   71234500
#  2025-05-07     10.22     10.30     10.18     10.28   58901200
#  2025-05-08     10.25     10.32     10.20     10.28   85432100
#  2025-05-09     10.28     10.40     10.25     10.35   76543200
#  2025-05-12     10.35     10.48     10.32     10.42   92345600
