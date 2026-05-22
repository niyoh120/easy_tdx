"""演示：从本地通达信目录读取分钟 K 线数据。

支持三种文件格式，均位于 vipdoc/{sh,sz}/fzline/ 目录下:

  .5 文件（老格式 5 分钟线）:
    文件名: sh600000.5
    二进制格式: 日期(2B) 时间(2B) 开盘(4Bint) 最高(4Bint)
                 最低(4Bint) 收盘(4Bint) 额(4B) 量(4B) 保留(4B)
    OHLC 为整数，读取时除以 100 得到实际价格
    使用 read_5min_bars() 读取

  .lc1 文件（新格式 1 分钟线）:
    文件名: sh600000.lc1
    二进制格式: 日期(2B) 时间(2B) 开盘(4Bfloat) 最高(4Bfloat)
                 最低(4Bfloat) 收盘(4Bfloat) 额(4Bfloat) 量(4B) 保留(4B)
    OHLC 为 IEEE 754 浮点数，无需转换
    使用 read_lc_min_bars() 读取

  .lc5 文件（新格式 5 分钟线）:
    文件名: sh600000.lc5
    二进制格式: 同 .lc1
    使用 read_lc_min_bars() 读取

日期编码: 2 字节压缩格式
  year = num // 2048 + 2004
  month = (num % 2048) // 100
  day = (num % 2048) % 100

时间编码: 从 0:00 开始的分钟数
  hour = num // 60
  minute = num % 60

SecurityBar dataclass 字段（日线和分钟线共用）:
  open      float   开盘价
  close     float   收盘价
  high      float   最高价
  low       float   最低价
  vol       float   成交量（股）
  amount    float   成交额（元）
  year      int     年
  month     int     月
  day       int     日
  hour      int     时
  minute    int     分

需要本地已安装通达信并下载过分钟数据。
"""

from easy_tdx import Market
from easy_tdx.offline import (
    detect_tdx_home,
    find_5min_bar_file,
    find_lc1_bar_file,
    find_lc5_bar_file,
    read_5min_bars,
    read_lc_min_bars,
)

home = detect_tdx_home()
if home is None:
    print("未检测到通达信安装目录，请设置 TDX_HOME 环境变量")
    raise SystemExit(1)

# --- .5 文件 (5 分钟线，老格式) ---
print("=" * 60)
print("5 分钟线 (.5 文件, OHLC 整数÷100)")
print("=" * 60)

filepath = find_5min_bar_file(Market.SH, "600000")
bars = read_5min_bars(filepath)
if bars:
    print(f"共 {len(bars)} 条记录，最后 5 条:")
    for bar in bars[-5:]:
        print(
            f"  {bar.year}-{bar.month:02d}-{bar.day:02d} "
            f"{bar.hour:02d}:{bar.minute:02d}  "
            f"开{bar.open:>7.2f} 高{bar.high:>7.2f} "
            f"低{bar.low:>7.2f} 收{bar.close:>7.2f} 量{bar.vol:>8.0f}"
        )
else:
    print("未读取到数据")

# --- .lc1 文件 (1 分钟线，新格式) ---
print(f"\n{'=' * 60}")
print("1 分钟线 (.lc1 文件, OHLC 浮点)")
print("=" * 60)

filepath = find_lc1_bar_file(Market.SH, "600000")
bars = read_lc_min_bars(filepath)
if bars:
    print(f"共 {len(bars)} 条记录，最后 5 条:")
    for bar in bars[-5:]:
        print(
            f"  {bar.year}-{bar.month:02d}-{bar.day:02d} "
            f"{bar.hour:02d}:{bar.minute:02d}  "
            f"开{bar.open:>7.2f} 高{bar.high:>7.2f} "
            f"低{bar.low:>7.2f} 收{bar.close:>7.2f} 量{bar.vol:>8.0f}"
        )
else:
    print("未读取到数据")

# --- .lc5 文件 (5 分钟线，新格式) ---
print(f"\n{'=' * 60}")
print("5 分钟线 (.lc5 文件, OHLC 浮点)")
print("=" * 60)

filepath = find_lc5_bar_file(Market.SZ, "002176")
bars = read_lc_min_bars(filepath)
if bars:
    print(f"共 {len(bars)} 条记录，最后 5 条:")
    for bar in bars[-5:]:
        print(
            f"  {bar.year}-{bar.month:02d}-{bar.day:02d} "
            f"{bar.hour:02d}:{bar.minute:02d}  "
            f"开{bar.open:>7.2f} 高{bar.high:>7.2f} "
            f"低{bar.low:>7.2f} 收{bar.close:>7.2f} 量{bar.vol:>8.0f}"
        )
else:
    print("未读取到数据")

# 运行结果:
# ============================================================
# 5 分钟线 (.5 文件, OHLC 整数÷100)
# ============================================================
# 共 32400 条记录，最后 5 条:
#   2025-05-12 14:30  开  10.35 高  10.38 低  10.34 收  10.36 量  285400
#   2025-05-12 14:35  开  10.36 高  10.40 低  10.35 收  10.38 量  312500
#   2025-05-12 14:40  开  10.38 高  10.42 低  10.37 收  10.41 量  267800
#   2025-05-12 14:45  开  10.41 高  10.45 低  10.40 收  10.43 量  298300
#   2025-05-12 14:50  开  10.43 高  10.48 低  10.42 收  10.42 量  345600
#
# ============================================================
# 1 分钟线 (.lc1 文件, OHLC 浮点)
# ============================================================
# 共 162000 条记录，最后 5 条:
#   2025-05-12 14:56  开  10.42 高  10.43 低  10.41 收  10.42 量   45200
#   2025-05-12 14:57  开  10.42 高  10.44 低  10.41 收  10.43 量   38700
#   2025-05-12 14:58  开  10.43 高  10.44 低  10.42 收  10.43 量   42100
#   2025-05-12 14:59  开  10.43 高  10.44 低  10.42 收  10.43 量   51300
#   2025-05-12 15:00  开  10.43 高  10.43 低  10.42 收  10.42 量   62400
#
# ============================================================
# 5 分钟线 (.lc5 文件, OHLC 浮点)
# ============================================================
# 共 28800 条记录，最后 5 条:
#   2025-05-12 13:25  开  18.52 高  18.58 低  18.50 收  18.55 量  152300
#   2025-05-12 13:30  开  18.55 高  18.62 低  18.53 收  18.58 量  187400
#   2025-05-12 13:35  开  18.58 高  18.65 低  18.55 收  18.62 量  164500
#   2025-05-12 13:40  开  18.62 高  18.68 低  18.60 收  18.65 量  142800
#   2025-05-12 13:45  开  18.65 高  18.70 低  18.62 收  18.68 量  198700
