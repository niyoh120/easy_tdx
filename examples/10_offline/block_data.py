"""演示：板块数据读取（本地 .dat 文件 + 网络自动回退）。

系统板块获取优先级:
  1. 本地 .dat 文件（离线读取，速度快）
  2. TDX 服务器在线获取（自动回退，需要网络）

自定义板块仅支持本地读取（存储在通达信本地目录中）。

TdxBlock dataclass 字段（系统板块）:
  name        str     板块名称（如"房地产"）
  category    int     板块分类（0=行业, 1=地域, 2=概念, 3=风格）
  count       int     板块包含的股票数量
  codes       list    股票代码列表（6位数字字符串，如"600000"）

CustomerBlock dataclass 字段（自定义板块）:
  blockname   str     板块名称（用户自定义，如"我的自选"）
  block_type  str     板块类型标识（对应 .blk 文件名）
  codes       list    股票代码列表（6位数字字符串）

板块文件位置:
  系统板块: vipdoc/block_zs.dat（行业）、vipdoc/block_gn.dat（概念）、vipdoc/block_fg.dat（风格）
  自定义板块: TDX_HOME/T0002/blocknew/blocknew.cfg + *.blk

自定义板块目录结构:
  blocknew/
  ├── blocknew.cfg    板块索引（120 字节/条：50B 名称 + 70B 文件名）
  ├── TDXBlock0.blk   板块内容文件（每行一个代码，首位为市场标识）
  ├── TDXBlock1.blk
  └── ...
"""

from pathlib import Path

from easy_tdx import TdxClient
from easy_tdx.models.finance import TdxBlock
from easy_tdx.offline import detect_tdx_home, read_block_dat, read_customer_blocks


def _print_blocks(blocks: list[TdxBlock], title: str) -> None:
    print(f"\n{title} ({len(blocks)} 个板块):")
    for block in blocks[:5]:
        codes_preview = ", ".join(block.codes[:5])
        suffix = "..." if len(block.codes) > 5 else ""
        print(f"  {block.name} ({block.count}只): {codes_preview}{suffix}")
    if len(blocks) > 5:
        print(f"  ... 还有 {len(blocks) - 5} 个板块")


home = detect_tdx_home()

# --- 系统板块 ---
print("=" * 60)
print("系统板块")
print("=" * 60)

vipdoc = Path(home) / "vipdoc" if home else None
block_names = ["block_zs.dat", "block_gn.dat", "block_fg.dat"]
block_labels = {
    "block_zs.dat": "行业板块",
    "block_gn.dat": "概念板块",
    "block_fg.dat": "风格板块",
}

need_fetch = []
for name in block_names:
    local_path = vipdoc / name if vipdoc else None
    if local_path and local_path.is_file():
        blocks = read_block_dat(local_path)
        _print_blocks(blocks, f"{block_labels[name]} ({name}, 本地)")
    else:
        print(f"\n{block_labels[name]}: 本地文件不存在，将从服务器获取")
        need_fetch.append(name)

# 本地没有的板块，通过网络获取
if need_fetch:
    print(f"\n正在连接服务器获取 {len(need_fetch)} 个板块文件...")
    with TdxClient.from_best_host() as c:
        for name in need_fetch:
            df = c.get_block_info(name)
            print(f"\n{block_labels[name]} ({name}, 网络) ({len(df)} 个板块):")
            for _, row in df.head(5).iterrows():
                codes = row["codes"]
                codes_preview = ", ".join(str(c) for c in codes[:5])
                suffix = "..." if len(codes) > 5 else ""
                print(f"  {row['name']} ({row['count']}只): {codes_preview}{suffix}")
            if len(df) > 5:
                print(f"  ... 还有 {len(df) - 5} 个板块")

# --- 自定义板块 ---
print(f"\n{'=' * 60}")
print("自定义板块")
print("=" * 60)

if home:
    blocknew_dir = Path(home) / "T0002" / "blocknew"
    if blocknew_dir.is_dir():
        blocks = read_customer_blocks(blocknew_dir)
        if blocks:
            print(f"\n共 {len(blocks)} 个自定义板块:")
            for block in blocks[:10]:
                codes_preview = ", ".join(block.codes[:5])
                suffix = "..." if len(block.codes) > 5 else ""
                print(f"  {block.blockname} ({len(block.codes)}只): {codes_preview}{suffix}")
        else:
            print("未找到自定义板块数据")
    else:
        print(f"自定义板块目录不存在: {blocknew_dir}")
else:
    print("需要本地通达信安装目录才能读取自定义板块")

# 运行结果:
# ============================================================
# 系统板块
# ============================================================
#
# 行业板块 (block_zs.dat, 本地) (82 个板块):
#   房地产 (78只): 000002, 000006, 000011, 000014, 000029...
#   电力行业 (62只): 000027, 000037, 000426, 000539, 000543...
#   计算机设备 (43只): 000066, 000977, 002236, 002415, 002416...
#   电子元件 (112只): 000045, 000050, 000725, 000727, 000823...
#   通信服务 (46只): 000035, 000063, 000069, 000547, 000555...
#   ... 还有 77 个板块
#
# 概念板块 (block_gn.dat, 本地) (412 个板块):
#   IPv6 (38只): 000063, 000938, 000948, 000977, 002089...
#   AI智能体 (56只): 300033, 300052, 300418, 300454, 300496...
#   BCH概念 (18只): 000063, 000938, 002123, 002152, 002177...
#   C2M概念 (22只): 000725, 000823, 002095, 002131, 002154...
#   IPO受益 (35只): 000031, 000063, 000415, 000532, 000540...
#   ... 还有 407 个板块
#
# ============================================================
# 自定义板块
# ============================================================
#
# 共 3 个自定义板块:
#   自选股 (8只): 600000, 000001, 000002, 600036, 601318...
#   中字头 (5只): 601857, 601988, 601398, 601288, 601328
#   龙头股 (12只): 600519, 000858, 600036, 601318, 000333...
