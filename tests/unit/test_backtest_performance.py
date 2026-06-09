"""单元测试：绩效分析器。

测试 PerformanceAnalyzer 的各项指标计算。
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from easy_tdx.backtest.performance import PerformanceAnalyzer


def _make_equity_curve(n: int = 252, total_return: float = 0.1) -> pd.DataFrame:
    """创建测试用资金曲线。

    Args:
        n: bar 数量
        total_return: 总收益率（例如 0.1 表示 10%）

    Returns:
        包含 datetime, total, drawdown 的 DataFrame
    """
    # 计算每日收益率
    daily_ret = (1 + total_return) ** (1 / n) - 1

    # 生成权益曲线
    initial = 100000
    total = initial * np.cumprod(np.full(n, 1 + daily_ret))

    # 计算回撤
    peak = np.maximum.accumulate(total)
    drawdown = peak - total

    return pd.DataFrame({
        "datetime": np.arange(n),
        "total": total,
        "drawdown": drawdown,
    })


def _make_trades() -> pd.DataFrame:
    """创建测试用交易记录。

    Returns:
        包含 direction, pnl, rejected 的 DataFrame
        4 条交易: BUY@100, SELL@105(pnl=500), BUY@95, SELL@90(pnl=-500)
    """
    return pd.DataFrame({
        "direction": ["BUY", "SELL", "BUY", "SELL"],
        "pnl": [0, 500, 0, -500],
        "rejected": [False, False, False, False],
    })


def test_total_return() -> None:
    """测试总收益率计算。"""
    equity = _make_equity_curve(n=252, total_return=0.1)
    trades = _make_trades()

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 总收益率应接近 0.1（10%）
    assert abs(metrics["total_return"] - 0.1) < 0.01


def test_max_drawdown_zero_when_monotonic() -> None:
    """测试单调递增时最大回撤接近 0。"""
    equity = _make_equity_curve(n=252, total_return=0.1)
    trades = _make_trades()

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 单调递增时回撤应很小（浮点误差）
    assert metrics["max_drawdown"] < 0.01


def test_sharpe_positive_for_profit() -> None:
    """测试正收益时夏普比率为正。"""
    equity = _make_equity_curve(n=252, total_return=0.1)
    trades = _make_trades()

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 正收益时夏普比率应大于 0
    assert metrics["sharpe"] > 0


def test_win_rate() -> None:
    """测试胜率计算。"""
    equity = _make_equity_curve(n=252, total_return=0.1)
    trades = _make_trades()

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 1 赢 1 输，胜率应接近 0.5
    assert abs(metrics["win_rate"] - 0.5) < 0.01


def test_total_trades() -> None:
    """测试总交易次数。"""
    equity = _make_equity_curve(n=252, total_return=0.1)
    trades = _make_trades()

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 只有 SELL 交易才算完整交易
    assert metrics["total_trades"] == 2


def test_empty_trades() -> None:
    """测试空交易记录。"""
    equity = _make_equity_curve(n=252, total_return=0.1)
    trades = pd.DataFrame({"direction": [], "pnl": [], "rejected": []})

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 空 trades 时交易相关指标应为 0
    assert metrics["total_trades"] == 0
    assert metrics["win_trades"] == 0
    assert metrics["lose_trades"] == 0
    assert metrics["win_rate"] == 0


def test_all_keys_present() -> None:
    """测试所有 19 个指标都存在。"""
    equity = _make_equity_curve(n=252, total_return=0.1)
    trades = _make_trades()

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    expected_keys = {
        "total_return",
        "annual_return",
        "max_drawdown",
        "max_dd_duration",
        "sharpe",
        "sortino",
        "calmar",
        "total_trades",
        "win_trades",
        "lose_trades",
        "rejected_trades",
        "win_rate",
        "profit_factor",
        "avg_win",
        "avg_loss",
        "max_win",
        "max_loss",
        "avg_holding_days",
        "volatility",
    }

    assert set(metrics.keys()) == expected_keys


def test_empty_equity_curve() -> None:
    """测试空资金曲线返回全零指标。"""
    equity = pd.DataFrame({"total": [], "drawdown": []})
    trades = _make_trades()

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 所有指标应为 0
    assert all(v == 0 for v in metrics.values())


def test_single_point_equity_curve() -> None:
    """测试只有一个点的资金曲线返回全零指标。"""
    equity = pd.DataFrame({"total": [100000], "drawdown": [0]})
    trades = _make_trades()

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 所有指标应为 0（需要至少 2 个点才能计算收益率）
    assert all(v == 0 for v in metrics.values())


def test_profit_factor() -> None:
    """测试盈亏比计算。"""
    equity = _make_equity_curve(n=252, total_return=0.1)
    trades = _make_trades()

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 盈利 500，亏损 500，盈亏比应为 1.0
    assert abs(metrics["profit_factor"] - 1.0) < 0.01


def test_avg_win_and_loss() -> None:
    """测试平均盈亏计算。"""
    equity = _make_equity_curve(n=252, total_return=0.1)
    trades = _make_trades()

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 1 笔盈利 500，平均盈利应接近 500
    assert abs(metrics["avg_win"] - 500) < 0.01

    # 1 笔亏损 500，平均亏损应接近 -500
    assert abs(metrics["avg_loss"] - (-500)) < 0.01


def test_max_win_and_loss() -> None:
    """测试最大盈亏计算。"""
    equity = _make_equity_curve(n=252, total_return=0.1)
    trades = _make_trades()

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 最大盈利应接近 500
    assert abs(metrics["max_win"] - 500) < 0.01

    # 最大亏损应接近 -500
    assert abs(metrics["max_loss"] - (-500)) < 0.01


def test_annual_return() -> None:
    """测试年化收益率计算。"""
    equity = _make_equity_curve(n=252, total_return=0.1)
    trades = _make_trades()

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 252 天 10% 收益，年化收益率应接近 0.1
    assert abs(metrics["annual_return"] - 0.1) < 0.01


def test_volatility() -> None:
    """测试年化波动率计算。"""
    equity = _make_equity_curve(n=252, total_return=0.1)
    trades = _make_trades()

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 波动率应大于 0
    assert metrics["volatility"] > 0


def test_rejected_trades() -> None:
    """测试被拒绝交易计数。"""
    equity = _make_equity_curve(n=252, total_return=0.1)

    # 创建包含被拒绝交易的记录
    trades = pd.DataFrame({
        "direction": ["BUY", "SELL", "SELL", "SELL"],
        "pnl": [0, 500, 0, -500],
        "rejected": [False, False, True, False],
    })

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 应有 1 笔被拒绝的交易
    assert metrics["rejected_trades"] == 1


def test_win_trades_and_lose_trades_count() -> None:
    """测试盈亏交易计数。"""
    equity = _make_equity_curve(n=252, total_return=0.1)
    trades = _make_trades()

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 1 笔盈利，1 笔亏损
    assert metrics["win_trades"] == 1
    assert metrics["lose_trades"] == 1


def test_avg_holding_days() -> None:
    """测试平均持仓天数（固定值）。"""
    equity = _make_equity_curve(n=252, total_return=0.1)
    trades = _make_trades()

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 平均持仓天数应为固定值 5.0
    assert metrics["avg_holding_days"] == 5.0


def test_max_dd_duration() -> None:
    """测试最大回撤持续时间计算。"""
    equity = _make_equity_curve(n=252, total_return=0.1)
    trades = _make_trades()

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 单调递增时最大回撤持续时间应为 0
    assert metrics["max_dd_duration"] == 0


def test_sortino() -> None:
    """测试索提诺比率计算。"""
    equity = _make_equity_curve(n=252, total_return=0.1)
    trades = _make_trades()

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 正收益时索提诺比率应大于 0
    assert metrics["sortino"] > 0


def test_calmar() -> None:
    """测试卡玛比率计算。"""
    equity = _make_equity_curve(n=252, total_return=0.1)
    trades = _make_trades()

    analyzer = PerformanceAnalyzer(equity, trades)
    metrics = analyzer.compute()

    # 卡玛比率 = annual_return / max_drawdown
    # 由于 max_drawdown 很小，calmar 会很大
    assert metrics["calmar"] > 0
