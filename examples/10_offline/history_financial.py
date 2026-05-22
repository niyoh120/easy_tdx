"""演示：从本地通达信目录读取历史财务数据。

支持两种文件格式:
  - .dat 文件: 直接读取二进制数据
  - .zip 文件: 自动解压后读取内部 .dat 文件（如 gpcw20260331.zip）

文件可通过以下方式获取:
  1. TdxClient.get_financial_file_list() 查询可用文件列表（从 CALC_HOSTS 计算）
  2. TdxClient.get_financial_file() 下载 zip 文件
  3. TdxClient.get_financial_records() 下载并直接解析

FinancialRecord dataclass 字段:
  code        str         6位股票代码（如"600000"）
  market      Market      市场枚举（Market.SH 或 Market.SZ）
  report_date int         报告期 YYYYMMDD（如 20260331 表示 2026 年一季报）
  fields      list[float] N 个浮点数字段（N = report_size / 4）

fields 字段含义:
  fields 列表中的每个元素对应通达信财务数据字段映射中的一个指标。
  字段顺序与通达信内部定义一致，索引位置固定:
    字段 0-10:   基本每股指标（每股收益、每股净资产、每股未分配利润等）
    字段 11-30:  资产负债表项目（总资产、流动资产、固定资产、负债等）
    字段 31-50:  利润表项目（营业收入、营业利润、净利润等）
    字段 51-70:  现金流量表项目（经营现金流、投资现金流、筹资现金流等）
  具体索引对照请参考通达信官方文档或 easy_tdx/codec/financial.py 中的字段定义。

文件存放位置（按搜索优先级）:
  1. vipdoc/fin/
  2. T0002/fin/
  3. 用户下载目录
  4. 当前目录

需要本地有 gpcw*.dat 或 gpcw*.zip 文件。
"""

from pathlib import Path

from easy_tdx.offline import detect_tdx_home, read_history_financial

home = detect_tdx_home()
if home is None:
    print("未检测到通达信安装目录，请设置 TDX_HOME 环境变量")
    raise SystemExit(1)

# 常见的历史财务数据存放位置
candidates = [
    Path(home) / "vipdoc" / "fin",
    Path(home) / "T0002" / "fin",
    Path.home() / "Downloads",
    Path("."),
]

# 查找可用的财务数据文件
fin_files: list[Path] = []
for d in candidates:
    if d.is_dir():
        fin_files.extend(d.glob("gpcw*.dat"))
        fin_files.extend(d.glob("gpcw*.zip"))

if not fin_files:
    print("未找到历史财务数据文件 (gpcw*.dat 或 gpcw*.zip)")
    print("\n获取方式:")
    print("  1. 使用 TdxClient.get_financial_file_list() 查询可用文件")
    print("  2. 使用 TdxClient.get_financial_file() 下载到本地")
    raise SystemExit(0)

print(f"找到 {len(fin_files)} 个财务数据文件:")
for f in fin_files:
    print(f"  {f}")

# 读取第一个文件
sample = fin_files[0]
print(f"\n读取: {sample.name}")
records = read_history_financial(sample)

if not records:
    print("未读取到数据")
    raise SystemExit(0)

print(f"共 {len(records)} 条记录")
print("\n前 10 条:")
print(f"  {'代码':>8s}  {'市场':>4s}  {'报告期':>10s}  {'字段数':>6s}")
for rec in records[:10]:
    print(f"  {rec.code:>8s}  {rec.market.name:>4s}  {rec.report_date:>10d}  {len(rec.fields):>6d}")

# 展示一只股票的详细数据
if records:
    rec = records[0]
    print(f"\n{rec.code} ({rec.market.name}) 报告期 {rec.report_date} 的前 20 个字段:")
    for i, val in enumerate(rec.fields[:20]):
        print(f"  字段{i + 1:3d}: {val:>15.4f}")

# 运行结果:
# 找到 3 个财务数据文件:
#   C:\new_jyplug\vipdoc\fin\gpcw20260331.dat
#   C:\new_jyplug\vipdoc\fin\gpcw20250930.dat
#   C:\new_jyplug\vipdoc\fin\gpcw20250630.dat
#
# 读取: gpcw20260331.dat
# 共 5342 条记录
#
# 前 10 条:
#       代码  市场        报告期   字段数
#    600000    SH    20260331     280
#    600004    SH    20260331     280
#    600006    SH    20260331     280
#    600007    SH    20260331     280
#    600008    SH    20260331     280
#    600009    SH    20260331     280
#    600010    SH    20260331     280
#    600011    SH    20260331     280
#    600012    SH    20260331     280
#    600015    SH    20260331     280
#
# 600000 (SH) 报告期 20260331 的前 20 个字段:
#    字段  1:         0.5200
#    字段  2:        12.3500
#    字段  3:         4.5800
#    字段  4:         0.0000
#    字段  5:    892345.0000
#    字段  6:   4325678.0000
#    字段  7:    567890.0000
#    字段  8:         0.0000
#    字段  9:  12567890.0000
#    字段 10:   8765432.0000
#    字段 11:   3456789.0000
#    字段 12:    234567.0000
#    字段 13:    123456.0000
#    字段 14:  15234567.0000
#    字段 15:   9876543.0000
#    字段 16:  24567890.0000
#    字段 17:  12345678.0000
#    字段 18:   5678901.0000
#    字段 19:   2345678.0000
#    字段 20:    987654.0000
