"""演示：检测通达信安装目录与路径解析。

本脚本展示 offline 模块的路径检测和文件定位功能。

检测优先级:
  1. TDX_HOME 环境变量（最高优先级，适用于自定义安装路径）
  2. 平台常见路径猜测:
     Windows: C:\\new_jyplug, C:\\new_tdx, D:\\new_jyplug, D:\\new_tdx
     Linux/macOS: ~/new_jyplug, ~/new_tdx

vipdoc 完整目录结构:
  vipdoc/
  ├── sh/                   上海市场
  │   ├── lday/             日线目录
  │   │   ├── sh600000.day  浦发银行日线
  │   │   └── ...
  │   └── fzline/           分钟线目录
  │       ├── sh600000.5    5分钟线（OHLC 整数÷100）
  │       ├── sh600000.lc1  1分钟线（OHLC 浮点）
  │       └── sh600000.lc5  5分钟线（OHLC 浮点）
  ├── sz/                   深圳市场
  │   ├── lday/             日线目录
  │   │   ├── sz000001.day  平安银行日线
  │   │   └── ...
  │   └── fzline/           分钟线目录
  │       ├── sz000001.5
  │       ├── sz000001.lc1
  │       └── sz000001.lc5
  ├── ds/                   扩展市场（期货、港股等）
  │   └── lday/             日线目录
  │       ├── 29#A1801.day  期货合约
  │       └── ...
  ├── fin/                  历史财务数据（可选）
  │   └── gpcw*.dat
  ├── block_zs.dat          行业板块
  ├── block_gn.dat          概念板块
  └── block_fg.dat          风格板块

其他重要路径:
  TDX_HOME/T0002/hq_cache/gbbq    股本变迁数据（XOR 加密）
  TDX_HOME/T0002/blocknew/        自定义板块目录
  TDX_HOME/T0002/fin/             历史财务数据（备用位置）

关键函数:
  detect_tdx_home() -> Path | None
      按优先级检测通达信安装目录。

  resolve_vipdoc(path=None) -> Path
      解析 vipdoc 数据目录，可显式指定路径或自动检测。

  find_daily_bar_file(market, code) -> Path
      根据市场+代码定位 .day 日线文件。

  find_5min_bar_file(market, code) -> Path
      定位 .5 五分钟线文件。

  find_lc1_bar_file(market, code) -> Path
      定位 .lc1 一分钟线文件。

  find_lc5_bar_file(market, code) -> Path
      定位 .lc5 五分钟线文件。
"""

from easy_tdx import Market
from easy_tdx.offline import (
    detect_tdx_home,
    find_5min_bar_file,
    find_daily_bar_file,
    find_lc1_bar_file,
    resolve_vipdoc,
)

# --- 检测安装目录 ---
print("=" * 60)
print("通达信安装目录检测")
print("=" * 60)

home = detect_tdx_home()
if home:
    print(f"检测到: {home}")
else:
    print("未检测到，可通过以下方式指定:")
    print("  set TDX_HOME=C:\\new_jyplug")

# --- 手动指定路径 ---
print(f"\n{'=' * 60}")
print("手动指定 vipdoc 路径")
print("=" * 60)

if home:
    vipdoc = resolve_vipdoc()
    print(f"vipdoc 目录: {vipdoc}")

    # 列出 vipdoc 子目录
    if vipdoc.is_dir():
        for d in sorted(vipdoc.iterdir()):
            if d.is_dir():
                files = list(d.rglob("*"))
                print(f"  {d.name}/ ({len(files)} 个文件)")
else:
    print("(需要 TDX_HOME 才能自动解析)")

# --- 文件定位示例 ---
print(f"\n{'=' * 60}")
print("通过 市场+代码 定位文件")
print("=" * 60)

if home:
    examples = [
        ("浦发银行 日线", lambda: find_daily_bar_file(Market.SH, "600000")),
        ("平安银行 日线", lambda: find_daily_bar_file(Market.SZ, "000001")),
        ("浦发银行 5分钟", lambda: find_5min_bar_file(Market.SH, "600000")),
        ("平安银行 1分钟", lambda: find_lc1_bar_file(Market.SZ, "000001")),
    ]
    for label, finder in examples:
        p = finder()
        exists = "存在" if p.is_file() else "不存在"
        print(f"  {label}: {p} ({exists})")
else:
    print("(需要 TDX_HOME)")

# --- 设置环境变量的方式 ---
print(f"\n{'=' * 60}")
print("如何设置 TDX_HOME")
print("=" * 60)
print("  Windows CMD:  set TDX_HOME=C:\\new_jyplug")
print("  Windows PS:   $env:TDX_HOME = 'C:\\new_jyplug'")
print("  Linux/macOS:  export TDX_HOME=/opt/new_tdx")

# 运行结果:
# ============================================================
# 通达信安装目录检测
# ============================================================
# 检测到: C:\new_jyplug
#
# ============================================================
# 手动指定 vipdoc 路径
# ============================================================
# vipdoc 目录: C:\new_jyplug\vipdoc
#   ds/ (213 个文件)
#   sh/ (1824 个文件)
#   sz/ (1460 个文件)
#
# ============================================================
# 通过 市场+代码 定位文件
# ============================================================
#   浦发银行 日线: C:\new_jyplug\vipdoc\sh\lday\sh600000.day (存在)
#   平安银行 日线: C:\new_jyplug\vipdoc\sz\lday\sz000001.day (存在)
#   浦发银行 5分钟: C:\new_jyplug\vipdoc\sh\fzline\sh600000.5 (存在)
#   平安银行 1分钟: C:\new_jyplug\vipdoc\sz\fzline\sz000001.lc1 (存在)
#
# ============================================================
# 如何设置 TDX_HOME
# ============================================================
#   Windows CMD:  set TDX_HOME=C:\new_jyplug
#   Windows PS:   $env:TDX_HOME = 'C:\new_jyplug'
#   Linux/macOS:  export TDX_HOME=/opt/new_tdx
