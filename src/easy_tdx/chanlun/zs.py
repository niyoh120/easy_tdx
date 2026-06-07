"""中枢计算。

中枢定义：至少三笔（或线段）的价格区间有重叠。
- zg（上沿）= 重叠区间的最高点
- zd（下沿）= 重叠区间的最低点
- gg = 中枢内所有笔的最高价
- dd = 中枢内所有笔的最低价

标准中枢算法：
1. 逐笔扫描，维护当前中枢的 zg/zd
2. 新笔进入时，更新 gg/dd
3. 新笔离开（不再与 [zd, zg] 重叠）时，关闭中枢
"""

from __future__ import annotations

from easy_tdx.chanlun.config import ChanlunConfig
from easy_tdx.chanlun.types import BI, ZS


def find_zss(
    bis: list[BI],
    config: ChanlunConfig | None = None,
) -> list[ZS]:
    """从笔列表中计算中枢。

    算法：
    1. 逐笔扫描
    2. 维护当前中枢的 zg/zd（重叠区间）
    3. 新笔与 [zd, zg] 有重叠 → 加入中枢，更新重叠区间
    4. 新笔与 [zd, zg] 无重叠 → 关闭当前中枢，开始新中枢

    Args:
        bis: 笔列表
        config: 缠论配置

    Returns:
        中枢列表
    """
    if config is None:
        config = ChanlunConfig()

    if len(bis) < 3:
        return []

    zss: list[ZS] = []
    current_zs: ZS | None = None

    for bi in bis:
        if current_zs is None:
            # 尝试开始新中枢：需要至少前两笔有重叠
            # 中枢至少需要3笔，先累积
            if len(zss) == 0 or True:
                # 用当前笔初始化中枢候选
                current_zs = ZS(
                    lines=[bi],
                    zg=bi.high,
                    zd=bi.low,
                    gg=bi.high,
                    dd=bi.low,
                    start=bi.start,
                    end=bi.end,
                    index=len(zss),
                )
            continue

        # 当前笔与中枢是否有重叠
        overlap_high = min(current_zs.zg, bi.high)
        overlap_low = max(current_zs.zd, bi.low)

        if overlap_high > overlap_low:
            # 有重叠，加入中枢
            current_zs.add_line(bi)
            current_zs.zg = overlap_high
            current_zs.zd = overlap_low
            current_zs.gg = max(current_zs.gg, bi.high)
            current_zs.dd = min(current_zs.dd, bi.low)
            current_zs.end = bi.end
        else:
            # 无重叠
            if current_zs.line_count >= config.zs_min_lines:
                # 中枢成立
                current_zs.done = True
                zss.append(current_zs)
            current_zs = None
            # 当前笔作为新中枢的起始
            current_zs = ZS(
                lines=[bi],
                zg=bi.high,
                zd=bi.low,
                gg=bi.high,
                dd=bi.low,
                start=bi.start,
                end=bi.end,
                index=len(zss),
            )

    # 处理最后一个中枢
    if current_zs is not None and current_zs.line_count >= config.zs_min_lines:
        current_zs.done = False  # 最后一根K线未确定，中枢未完成
        zss.append(current_zs)

    return zss
