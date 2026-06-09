"""回测绩效分析器。

计算资金曲线和交易记录的各项绩效指标。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt
import pandas as pd

if TYPE_CHECKING:
    NDArray = npt.NDArray[np.float64]
else:
    NDArray = np.ndarray


class PerformanceAnalyzer:
    """绩效分析器。

    从资金曲线和交易记录计算 19 项绩效指标。

    Attributes:
        ANNUAL_DAYS: 年化交易日数（默认 252）
        RISK_FREE_RATE: 无风险利率（默认 3%）
    """

    ANNUAL_DAYS = 252
    RISK_FREE_RATE = 0.03

    def __init__(
        self,
        equity_curve: pd.DataFrame,
        trades: pd.DataFrame,
        risk_free_rate: float = 0.03,
    ) -> None:
        """初始化分析器。

        Args:
            equity_curve: 资金曲线 DataFrame，必须包含 total 和 drawdown 列
            trades: 交易记录 DataFrame，必须包含 direction, pnl, rejected 列
            risk_free_rate: 无风险利率（默认 3%）
        """
        self._equity_curve = equity_curve
        self._trades = trades
        self._risk_free_rate = risk_free_rate

    def compute(self) -> dict[str, float]:
        """计算绩效指标。

        Returns:
            包含 19 项指标的字典：
            - total_return: 总收益率
            - annual_return: 年化收益率
            - max_drawdown: 最大回撤
            - max_dd_duration: 最大回撤持续时间（bar 数）
            - sharpe: 夏普比率
            - sortino: 索提诺比率
            - calmar: 卡玛比率
            - total_trades: 总交易次数
            - win_trades: 盈利交易次数
            - lose_trades: 亏损交易次数
            - rejected_trades: 被拒绝的交易次数
            - win_rate: 胜率
            - profit_factor: 盈亏比
            - avg_win: 平均盈利
            - avg_loss: 平均亏损
            - max_win: 最大盈利
            - max_loss: 最大亏损
            - avg_holding_days: 平均持仓天数（简化为固定值 5.0）
            - volatility: 年化波动率
        """
        # 边界检查
        if len(self._equity_curve) < 2:
            return self._empty_metrics()

        total = self._equity_curve["total"].to_numpy()
        drawdown = self._equity_curve["drawdown"].to_numpy()

        # 计算日收益率
        daily_ret = np.diff(total) / total[:-1]
        daily_ret = daily_ret[~np.isnan(daily_ret)]

        # 日收益率数量太少时返回空指标
        if len(daily_ret) < 2:
            return self._empty_metrics()

        # 1. 总收益率
        total_return = (total[-1] / total[0]) - 1

        # 2. 年化收益率
        n = len(daily_ret)
        annual_return = (1 + total_return) ** (self.ANNUAL_DAYS / n) - 1

        # 3. 最大回撤
        max_drawdown_value = np.max(drawdown)
        max_drawdown = max_drawdown_value / total[0] if total[0] != 0 else 0

        # 4. 最大回撤持续时间
        max_dd_duration = self._compute_max_dd_duration(total, drawdown)

        # 5. 夏普比率
        rf_daily = self._risk_free_rate / self.ANNUAL_DAYS
        excess_ret = daily_ret - rf_daily
        sharpe = (
            np.mean(excess_ret) / np.std(daily_ret) * np.sqrt(self.ANNUAL_DAYS)
            if np.std(daily_ret) != 0
            else 0
        )

        # 6. 索提诺比率（分母只用负收益标准差）
        neg_ret = excess_ret[excess_ret < 0]
        if len(neg_ret) > 0 and np.std(neg_ret) != 0:
            sortino = np.mean(excess_ret) / np.std(neg_ret) * np.sqrt(self.ANNUAL_DAYS)
        elif len(neg_ret) == 0 and np.mean(excess_ret) > 0:
            # 没有负收益时，返回一个很大的值表示表现优异
            sortino = 999.0
        else:
            sortino = 0.0

        # 7. 卡玛比率
        # 使用小阈值避免除以极小值
        if max_drawdown > 1e-10:
            calmar = annual_return / max_drawdown
        elif annual_return > 0:
            # 无回撤且有正收益时，返回一个很大的值
            calmar = 999.0
        else:
            calmar = 0.0

        # 交易统计
        sell_trades = self._trades[self._trades["direction"] == "SELL"]
        win_trades_mask = sell_trades["pnl"] > 0
        lose_trades_mask = sell_trades["pnl"] <= 0

        # 8. 总交易次数
        total_trades = len(sell_trades)

        # 9. 盈利交易次数
        win_count = np.sum(win_trades_mask)

        # 10. 亏损交易次数
        lose_count = np.sum(lose_trades_mask)

        # 11. 被拒绝的交易次数
        rejected_trades = self._trades["rejected"].sum()

        # 12. 胜率
        win_rate = win_count / (win_count + lose_count) if (win_count + lose_count) > 0 else 0

        # 13. 盈亏比
        win_pnl = sell_trades.loc[win_trades_mask, "pnl"]
        lose_pnl = sell_trades.loc[lose_trades_mask, "pnl"]

        if len(win_pnl) > 0 and len(lose_pnl) > 0:
            profit_factor = win_pnl.sum() / abs(lose_pnl.sum())
            # 限制 inf
            if np.isinf(profit_factor):
                profit_factor = 999.0
        else:
            profit_factor = 0.0

        # 14. 平均盈利
        avg_win = win_pnl.mean() if len(win_pnl) > 0 else 0.0

        # 15. 平均亏损
        avg_loss = lose_pnl.mean() if len(lose_pnl) > 0 else 0.0

        # 16. 最大盈利
        max_win = win_pnl.max() if len(win_pnl) > 0 else 0.0

        # 17. 最大亏损
        max_loss = lose_pnl.min() if len(lose_pnl) > 0 else 0.0

        # 18. 平均持仓天数（简化为固定值）
        avg_holding_days = 5.0

        # 19. 年化波动率
        volatility = np.std(daily_ret) * np.sqrt(self.ANNUAL_DAYS)

        return {
            "total_return": total_return,
            "annual_return": annual_return,
            "max_drawdown": max_drawdown,
            "max_dd_duration": max_dd_duration,
            "sharpe": sharpe,
            "sortino": sortino,
            "calmar": calmar,
            "total_trades": total_trades,
            "win_trades": win_count,
            "lose_trades": lose_count,
            "rejected_trades": rejected_trades,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "max_win": max_win,
            "max_loss": max_loss,
            "avg_holding_days": avg_holding_days,
            "volatility": volatility,
        }

    def _compute_max_dd_duration(self, total: NDArray, drawdown: NDArray) -> int:
        """计算最大回撤持续时间。

        找到最大回撤点，然后计算从回撤前的高点到该点的 bar 数。

        Args:
            total: 总权益数组
            drawdown: 回撤数组

        Returns:
            最大回撤持续时间（bar 数）
        """
        if len(drawdown) == 0:
            return 0

        max_dd_idx: int = int(np.argmax(drawdown))
        max_dd_value = drawdown[max_dd_idx]

        # 如果没有回撤，返回 0
        if max_dd_value == 0:
            return 0

        # 找到回撤前的高点
        peak_idx: int = max_dd_idx
        for i in range(max_dd_idx - 1, -1, -1):
            if total[i] > total[max_dd_idx]:
                peak_idx = i
                break

        return int(max_dd_idx - peak_idx)

    def _empty_metrics(self) -> dict[str, float]:
        """返回全零指标字典。

        用于数据不足时的默认返回值。

        Returns:
            全零的绩效指标字典
        """
        return {
            "total_return": 0.0,
            "annual_return": 0.0,
            "max_drawdown": 0.0,
            "max_dd_duration": 0,
            "sharpe": 0.0,
            "sortino": 0.0,
            "calmar": 0.0,
            "total_trades": 0,
            "win_trades": 0,
            "lose_trades": 0,
            "rejected_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "max_win": 0.0,
            "max_loss": 0.0,
            "avg_holding_days": 0.0,
            "volatility": 0.0,
        }
