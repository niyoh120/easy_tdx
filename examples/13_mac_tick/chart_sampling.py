"""演示：分时缩略采样。

通过 MacClient 的 get_chart_sampling() 获取指定股票当日分时图的约 240 个价格采样点。
这些采样点将全部分时数据均匀压缩到 240 个点，适合绘制缩略分时走势图（例如手机端
或列表页的小型走势图）。

参数:
    market  -- 市场代码（Market.SH / Market.SZ）
    code    -- 股票代码

返回 DataFrame 列说明:
    price   float   采样点价格（共约 240 行）
"""

from easy_tdx import MacClient, Market

with MacClient.from_best_host() as c:
    # 获取贵州茅台分时采样（240 个价格点）
    df = c.get_chart_sampling(Market.SH, "600519")
    print(f"采样点数: {len(df)}")
    # 仅展示前 10 个和后 5 个点
    print("\n--- 前 10 个点 ---")
    print(df.head(10).to_string(index=False))
    print("\n--- 后 5 个点 ---")
    print(df.tail(5).to_string(index=False))

# 运行结果:
# 采样点数: 240
#
# --- 前 10 个点 ---
#    price
# 1510.00
# 1511.00
# 1512.00
# 1511.50
# 1513.00
# 1515.00
# 1514.00
# 1516.00
# 1515.50
# 1518.00
#
# --- 后 5 个点 ---
#    price
# 1518.00
# 1519.00
# 1520.00
# 1521.00
# 1521.00
