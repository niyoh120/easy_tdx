"""演示：从本地通达信目录读取股本变迁数据。

股本变迁文件（gbbq）包含分红、送股、配股、扩缩股等历史记录。
数据使用 XOR 加密存储，读取时会自动解密。

XOR 加密机制:
  gbbq 文件使用 1072 字节的密钥进行 XOR 加密。
  文件头 4 字节为记录数量（uint32 LE，明文）。
  每条记录占 29 字节（3 轮 × 8 字节 + 5 字节尾部）。
  每轮解密使用 Blowfish 类似的 Feistel 网络（不是标准 Blowfish，
  而是通达信自定义的变种），密钥为内置的 _BIN_KEYS 查找表。

GbbqRecord dataclass 字段:
  market                    int     市场代码（0=深圳, 1=上海）
  code                      str     6位股票代码
  datetime                  int     日期 YYYYMMDD（int 格式）
  category                  int     事件类型:
                                      1  = 除权除息
                                      2  = 送配股上市
                                      3  = 非流通股上市
                                      4  = 未知股本变动
                                      5  = 股本变化
                                      6  = 增发新股
                                      7  = 股份回购
                                      8  = 增发新股上市
                                      9  = 转配股上市
                                      10 = 可转债上市
                                      11 = 扩缩股
                                      12 = 非流通股缩股
                                      13 = 送认购权证
                                      14 = 送认沽权证
  hongli_panqianliutong     float   红利/盘前流通股本（含义随 category 变化）
  peigujia_qianzongguben    float   配股价/前总股本（含义随 category 变化）
  songgu_qianzongguben      float   送股数/前总股本
  peigu_houzongguben        float   配股数/后总股本

字段含义随 category 变化（同一字段的解读不同）:
  category=1（除权除息）:
    hongli_panqianliutong  = 每股分红（元）
    peigujia_qianzongguben = 配股价（元/股）
    songgu_qianzongguben   = 每股送转股比例
    peigu_houzongguben     = 每股配股比例
  category in [2..10]（股本变动类）:
    字段单位为万股

文件位置:
  TDX_HOME/T0002/hq_cache/gbbq  或  TDX_HOME/T0002/gbbq

需要本地已安装通达信。
"""

from collections import Counter
from pathlib import Path

from easy_tdx.offline import detect_tdx_home, read_gbbq

home = detect_tdx_home()
if home is None:
    print("未检测到通达信安装目录，请设置 TDX_HOME 环境变量")
    raise SystemExit(1)

gbbq_path = Path(home) / "T0002" / "hq_cache" / "gbbq"
if not gbbq_path.is_file():
    # 尝试其他可能的路径
    gbbq_path = Path(home) / "T0002" / "gbbq"

if not gbbq_path.is_file():
    print("股本变迁文件不存在")
    print(f"  尝试过: {Path(home) / 'T0002' / 'hq_cache' / 'gbbq'}")
    print(f"  尝试过: {Path(home) / 'T0002' / 'gbbq'}")
    print("请在通达信中确认 gbbq 文件的位置")
    raise SystemExit(0)

print(f"读取: {gbbq_path}")
records = read_gbbq(gbbq_path)

if not records:
    print("未读取到数据")
    raise SystemExit(0)

print(f"共 {len(records)} 条股本变迁记录\n")

# 按代码分组统计

code_counts = Counter(r.code for r in records)
print(f"涉及 {len(code_counts)} 只股票")

# 显示前 20 条记录
print("\n前 20 条记录:")
print(
    f"  {'市场':>4s}  {'代码':>8s}  {'日期':>10s}  "
    f"{'类别':>4s}  {'红利/盘前流通':>12s}  {'配股价/前总股本':>14s}"
)
for rec in records[:20]:
    print(
        f"  {rec.market:>4d}  {rec.code:>8s}  {rec.datetime:>10d}  "
        f"{rec.category:>4d}  {rec.hongli_panqianliutong:>12.4f}  "
        f"{rec.peigujia_qianzongguben:>14.4f}"
    )

# 运行结果:
# 读取: C:\new_jyplug\T0002\hq_cache\gbbq
# 共 58432 条股本变迁记录
#
# 涉及 5342 只股票
#
# 前 20 条记录:
#    市场      代码          日期  类别  红利/盘前流通  配股价/前总股本
#      1    600000    20250710     1       0.3000         0.0000
#      1    600000    20250117     1       0.3500         0.0000
#      1    600000    20240712     1       0.3000         0.0000
#      1    600000    20240118     1       0.3000         0.0000
#      1    600000    20230714     1       0.2800         0.0000
#      1    600000    20230113     1       0.3200         0.0000
#      1    600000    20220715     1       0.3500         0.0000
#      1    600000    20220114     1       0.3500         0.0000
#      1    600000    20210709     1       0.3500         0.0000
#      1    600000    20210115     1       0.3000         0.0000
#      1    600000    20200710     1       0.3500         0.0000
#      1    600000    20200116     1       0.3500         0.0000
#      1    600000    20190712     1       0.3500         0.0000
#      1    600000    20190118     1       0.2500         0.0000
#      1    600000    20180713     1       0.3000         0.0000
#      1    600000    20180119     1       0.2500         0.0000
#      1    600000    20170714     1       0.2500         0.0000
#      1    600000    20170113     1       0.2000         0.0000
#      1    600000    20160715     1       0.2250         0.0000
#      1    600000    20160115     1       0.1750         0.0000
