"""笔计算。

笔的定义：
- 由相邻的顶底分型连接而成
- 顶→底 = 向下笔，底→顶 = 向上笔
- 新笔规则：分型之间至少有 1 根独立缠论 K 线（即分型中间 K 线的 index 差 > 2）
- 老笔规则：分型之间至少有 3 根缠论 K 线
- 简单笔规则：只要顶底交替即可
"""

from __future__ import annotations

from easy_tdx.chanlun.config import ChanlunConfig
from easy_tdx.chanlun.types import BI, FX, Direction, FXType


def _can_form_bi(
    start: FX,
    end: FX,
    config: ChanlunConfig,
) -> bool:
    """判断两个分型是否可以构成一笔。"""
    # 顶底必须交替
    if start.fx_type == end.fx_type:
        return False

    # 分型之间缠论 K 线的间距
    # 分型由三根 K 线组成：[left, mid, right]
    # 独立 K 线数 = end.left.index - start.right.index + 1（如果 >0）
    gap = end.klines[0].index - start.klines[2].index + 1

    if config.bi_type == "new":
        # 新笔：至少1根独立K线
        return gap >= 1
    elif config.bi_type == "old":
        # 老笔：至少3根缠论K线在分型之间
        return gap >= 3
    else:
        # simple：只要顶底交替即可
        return True


def find_bis(
    fxs: list[FX],
    config: ChanlunConfig | None = None,
) -> list[BI]:
    """从分型列表中计算笔。

    算法（贪心）：
    1. 遍历分型列表，维护最后一个有效分型
    2. 如果当前分型与最后一个有效分型可以成笔，形成新笔
    3. 如果当前分型与最后一个有效分型同类型（同为顶或同为底），
       取更极端的那个替换（顶取更高的，底取更低的）

    Args:
        fxs: 分型列表
        config: 缠论配置

    Returns:
        笔列表
    """
    if config is None:
        config = ChanlunConfig()

    if len(fxs) < 2:
        return []

    bis: list[BI] = []

    # 用一个指针追踪当前笔的起始分型
    start_fx = fxs[0]

    for i in range(1, len(fxs)):
        current_fx = fxs[i]

        # 同类型分型：取更极端的
        if current_fx.fx_type == start_fx.fx_type:
            if start_fx.fx_type == FXType.DING and current_fx.val > start_fx.val:
                start_fx = current_fx
            elif start_fx.fx_type == FXType.DI and current_fx.val < start_fx.val:
                start_fx = current_fx
            continue

        # 异类型分型，检查是否可以成笔
        if _can_form_bi(start_fx, current_fx, config):
            direction = Direction.UP if start_fx.fx_type == FXType.DI else Direction.DOWN
            high = max(start_fx.val, current_fx.val)
            low = min(start_fx.val, current_fx.val)

            bi = BI(
                start=start_fx,
                end=current_fx,
                direction=direction,
                index=len(bis),
                high=high,
                low=low,
            )
            bis.append(bi)
            start_fx = current_fx
        # 如果不能成笔（间距不够），继续搜索

    return bis
