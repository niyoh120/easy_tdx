"""演示：获取公司信息目录与各个分类的详细内容。

使用 TdxClient 标准协议客户端，分两步获取公司信息：
  1. get_company_info_category() -- 获取公司信息目录（分类列表）
  2. get_company_info_content() -- 根据目录中的 filename/start/length 读取具体内容

get_company_info_category() 返回 CompanyInfoCategory DataFrame，列说明:
  name      str     分类名称（如"最新提示"、"公司概况"、"财务分析"等）
  filename  str     内容文件名（如 "600519.txt"）
  start     int     内容在该文件中的起始偏移（字节）
  length    int     内容长度（字节）

公司信息常见分类:
  最新提示、公司概况、财务分析、股本结构、股东研究、机构持股、
  分红融资、高管治理、资金动向、资本运作、热点题材、公司公告、
  公司报道、经营分析、行业分析、研报评级

数据特点:
  - 目录中每个分类对应同一 .txt 文件的不同偏移位置
  - 内容为纯文本，长度从几百字节到数万字节不等
  - 内容更新频率取决于上市公司公告发布节奏
"""

from easy_tdx import Market, TdxClient

CODE = "600519"
NAME = "贵州茅台"
MARKET = Market.SH

# 要展示的分类，按需注释/取消注释
SHOW_CATEGORIES = [
    "最新提示",
    "公司概况",
    "财务分析",
    "股本结构",
    "股东研究",
    "机构持股",
    "分红融资",
    "高管治理",
    "资金动向",
    "资本运作",
    "热点题材",
    "公司公告",
    "公司报道",
    "经营分析",
    "行业分析",
    "研报评级",
]


def show_category_content(client, categories, category_name, max_chars=500):
    """获取并展示指定分类的内容。"""
    row = categories[categories["name"] == category_name]
    if row.empty:
        print(f"  未找到分类: {category_name}")
        return

    r = row.iloc[0]
    content = client.get_company_info_content(
        MARKET, CODE, r["filename"], int(r["start"]), int(r["length"])
    )
    text = content.strip()
    if len(text) > max_chars:
        text = text[:max_chars] + f"\n... (共 {len(content.strip())} 字，仅显示前 {max_chars} 字)"
    print(f"\n{'=' * 60}")
    print(f"【{r['name']}】 (共 {r['length']} 字节)")
    print(f"{'=' * 60}")
    print(text)


with TdxClient.from_best_host() as c:
    categories = c.get_company_info_category(MARKET, CODE)

    # 1. 显示目录
    print(f"{NAME} 公司信息目录:")
    print(categories.to_string(index=False))

    # 2. 显示所有分类内容（每个分类默认只显示前500字）
    for name in SHOW_CATEGORIES:
        show_category_content(c, categories, name)

    # 3. 也可以单独获取某个分类的完整内容，例如：
    # show_category_content(c, categories, "公司概况", max_chars=99999)

# 运行结果:
# 贵州茅台 公司信息目录:
#        name    filename   start  length
#     最新提示 600519.txt       0    3954
#     公司概况 600519.txt    3954   14358
#     财务分析 600519.txt   18312    9801
#     股本结构 600519.txt   28113    2670
#     股东研究 600519.txt   30783    8322
#     机构持股 600519.txt   39105    4560
#     分红融资 600519.txt   43665    3285
#     高管治理 600519.txt   46950    4170
#     资金动向 600519.txt   51120    2130
#     资本运作 600519.txt   53250    1890
#     热点题材 600519.txt   55140    1020
#     公司公告 600519.txt   56160    7560
#     公司报道 600519.txt   63720    5340
#     经营分析 600519.txt   69060    6780
#     行业分析 600519.txt   75840    3450
#     研报评级 600519.txt   79290    8640
