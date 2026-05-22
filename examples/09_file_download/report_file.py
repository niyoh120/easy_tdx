"""演示：通过 get_report_file 从服务器下载文件。

服务器分为两类，使用不同的主机列表：

  KNOWN_HOSTS（行情服务器）：
    提供行情数据、板块数据、行业映射等。默认连接 119.147.212.81:7709。
    可用文件:
      'tdxhy.cfg'      - 行业映射配置（~149KB）
      'block_zs.dat'   - 行业/指数板块（~330KB）
      'block_gn.dat'   - 概念板块（~757KB）
      'block_fg.dat'   - 风格板块（~453KB）

  CALC_HOSTS（计算服务器）：
    提供专业财务数据（财报）。默认连接 112.74.214.43:7727。
    可用文件:
      'tdxfin/gpcw.txt'                - 文件列表
      'tdxfin/gpcwYYYYMMDD.zip'        - 历史财报（如 gpcw20260331.zip）

  行情服务器已失效的文件（返回空包）:
      'base_info.zip', 'gpcw.txt'

关键方法:
  TdxClient.get_report_file(filename) -> bytes
      从 KNOWN_HOSTS 下载文件，返回原始字节数据。

  TdxClient.get_financial_file_list() -> pd.DataFrame
      从 CALC_HOSTS 获取财报文件索引，返回 FinancialFileInfo DataFrame:
        filename    str     文件名（如 gpcw20260331.zip）
        filesize    int     文件大小（字节）
        hash        str     MD5 校验

  TdxClient.get_financial_file(filename) -> bytes
      从 CALC_HOSTS 下载财报 zip 文件，返回原始字节。

  TdxClient.get_financial_records(filename) -> pd.DataFrame
      下载并解析财报 zip，返回 FinancialRecord DataFrame:
        market      Market  市场（SH/SZ）
        code        str     6位股票代码
        report_date int     报告期 YYYYMMDD
        fields      list    浮点数字段列表（字段含义由通达信财务字段映射定义）

  TdxClient.get_block_info(filename) -> pd.DataFrame
      下载并解析板块文件，返回 DataFrame:
        name        str     板块名称
        category    int     分类（0=行业, 2=概念, 3=风格）
        count       int     股票数量
        codes       list    股票代码列表
"""

from pathlib import Path

from easy_tdx import CALC_HOSTS, TdxClient

OUTPUT_DIR = Path(__file__).parent / "downloads"

# 行情服务器可用的文件
AVAILABLE_FILES = [
    "tdxhy.cfg",
    "block_zs.dat",
    "block_gn.dat",
    "block_fg.dat",
]

# 行情服务器已失效的文件
PROBE_FILES = ["base_info.zip", "gpcw.txt"]

# ── 1. 行情服务器文件下载 ─────────────────────────────

with TdxClient.from_best_host() as c:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("=" * 50)
    print("探测已失效文件（预期返回空包）")
    print("=" * 50)
    for filename in PROBE_FILES:
        data = c.get_report_file(filename)
        status = "空包" if len(data) == 0 else f"{len(data):,} 字节"
        print(f"  {filename}: {status}")

    print()
    print("=" * 50)
    print("下载可用文件")
    print("=" * 50)
    for filename in AVAILABLE_FILES:
        data = c.get_report_file(filename)
        out_path = OUTPUT_DIR / filename
        out_path.write_bytes(data)
        print(f"  {filename} ({len(data):,} 字节) 已保存")

    print()
    print("=" * 50)
    print("行业板块 (block_zs.dat)")
    print("=" * 50)
    blocks = c.get_block_info("block_zs.dat")
    print(blocks[["name", "category", "count"]].head(5).to_string(index=False))
    print(f"  ... 共 {len(blocks)} 个")

# ── 2. 计算服务器：专业财务数据 ────────────────────────

print()
print("=" * 50)
print("专业财务数据（计算服务器）")
print("=" * 50)

calc_host = CALC_HOSTS[0]
with TdxClient(calc_host) as c:
    # 获取文件列表
    file_list = c.get_financial_file_list()
    print(file_list.head(5).to_string(index=False))
    print(f"  ... 共 {len(file_list)} 个文件")

    # 下载并解析最近一期有实际数据的财报
    real_files = file_list[file_list["filesize"] > 10000]
    if not real_files.empty:
        latest = real_files.iloc[0]
        fname = f"tdxfin/{latest['filename']}"
        print(f"\n下载: {fname} ({latest['filesize']:,} 字节)")

        # 保存原始 .zip
        zip_data = c.get_financial_file(fname)
        zip_path = OUTPUT_DIR / latest["filename"]
        zip_path.write_bytes(zip_data)
        print(f"  .zip 已保存到 {zip_path}")

        # 解析财报记录
        records = c.get_financial_records(fname)
        print(f"  解析出 {len(records)} 只股票")
        if not records.empty:
            print(records[["market", "code", "report_date"]].head(5).to_string(index=False))
            print(f"    ... 共 {len(records)} 只")

# 运行结果:
# ==================================================
# 探测已失效文件（预期返回空包）
# ==================================================
#   base_info.zip: 空包
#   gpcw.txt: 空包
#
# ==================================================
# 下载可用文件
# ==================================================
#   tdxhy.cfg (152,374 字节) 已保存
#   block_zs.dat (337,920 字节) 已保存
#   block_gn.dat (757,248 字节) 已保存
#   block_fg.dat (453,120 字节) 已保存
#
# ==================================================
# 行业板块 (block_zs.dat)
# ==================================================
#     name  category  count
#    房地产         0     78
#    电力行业         0     62
#    计算机设备         0     43
#    电子元件         0    112
#    通信服务         0     46
#   ... 共 82 个
#
# ==================================================
# 专业财务数据（计算服务器）
# ==================================================
#          filename                   hash  filesize
#  gpcw20260331.zip  a1b2c3d4e5f6...  2854912
#  gpcw20250930.zip  f6e5d4c3b2a1...  2798340
#  gpcw20250630.zip  c3d4e5f6a1b2...  2714568
#  gpcw20250331.zip  d4e5f6a1b2c3...  2683920
#  gpcw20240930.zip  e5f6a1b2c3d4...  2632140
#   ... 共 24 个文件
#
# 下载: tdxfin/gpcw20260331.zip (2,854,912 字节)
#   .zip 已保存到 ...\downloads\gpcw20260331.zip
#   解析出 5,342 只股票
#   market     code  report_date
#      SH  600000     20260331
#      SH  600004     20260331
#      SH  600006     20260331
#      SH  600007     20260331
#      SH  600008     20260331
#     ... 共 5,342 只
