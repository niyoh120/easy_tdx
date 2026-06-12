"""可插拔执行仿真引擎。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from easy_tdx.backtest.types import Trade

if TYPE_CHECKING:
    from easy_tdx.backtest.slippage import SlippageModel
    from easy_tdx.backtest.types import Signal


class ExecutionModel(ABC):
    """执行仿真基类。"""

    @abstractmethod
    def execute(
        self,
        signal: Signal,
        df: pd.DataFrame,
        bar_idx: int,
        cash: float,
        position: float,
        position_mode: str,
        commission: float,
        min_commission: float,
        stamp_tax: float,
        slippage_model: SlippageModel | None,
    ) -> list[Trade]:
        """将信号转换为一笔或多笔成交。"""
        ...

    def _calc_commission(
        self,
        size: float,
        price: float,
        is_sell: bool,
        commission: float,
        min_commission: float,
        stamp_tax: float,
    ) -> float:
        """计算手续费。"""
        comm = max(size * price * commission, min_commission)
        if is_sell:
            comm += size * price * stamp_tax
        return comm

    def _calc_slippage(
        self,
        size: float,
        price: float,
        is_sell: bool,
        slippage_model: SlippageModel | None,
        df: pd.DataFrame,
    ) -> float:
        """计算滑点。"""
        if slippage_model is None:
            return 0.0
        volume = float(df["volume"].iloc[-1]) if "volume" in df.columns else 0.0
        volatility = self._estimate_volatility(df)
        return slippage_model.compute(
            price=price,
            size=size,
            volume=volume,
            volatility=volatility,
            direction="SELL" if is_sell else "BUY",
        )

    def _estimate_volatility(self, df: pd.DataFrame) -> float:
        """从收盘价估计近期年化波动率。"""
        if "close" not in df.columns or len(df) < 2:
            return 0.0
        close = df["close"].to_numpy()
        returns = np.diff(close) / close[:-1]
        if len(returns) < 2:
            return 0.0
        return float(np.std(returns)) * np.sqrt(252)

    def _calc_buy_size(
        self,
        signal_size: float,
        price: float,
        cash: float,
        position_mode: str,
        commission: float,
    ) -> float:
        """计算买入数量。"""
        if position_mode == "full" or signal_size == 0:
            max_cost = price * (1 + commission)
            max_shares = int(cash / max_cost / 100) * 100
            return float(max_shares)
        elif position_mode == "percent":
            target_value = cash * signal_size
            return float(int(target_value / price / 100) * 100)
        return signal_size

    def _get_datetime_int(self, df: pd.DataFrame, idx: int) -> int:
        """获取指定 index 的 datetime int。"""
        dt_raw = df["datetime"].iloc[idx]
        if hasattr(dt_raw, "strftime"):
            return int(dt_raw.strftime("%Y%m%d"))
        return int(dt_raw)


class ImmediateExecution(ExecutionModel):
    """即时成交（向后兼容，与现有 OrderSimulator 行为一致）。"""

    def execute(
        self,
        signal: Signal,
        df: pd.DataFrame,
        bar_idx: int,
        cash: float,
        position: float,
        position_mode: str,
        commission: float,
        min_commission: float,
        stamp_tax: float,
        slippage_model: SlippageModel | None,
    ) -> list[Trade]:
        exec_idx = bar_idx + 1
        if exec_idx >= len(df):
            return []

        price = float(df["open"].iloc[exec_idx])

        if signal.direction == "BUY":
            size = self._calc_buy_size(
                signal.size,
                price,
                cash,
                position_mode,
                commission,
            )
            if size <= 0:
                return []
            comm = self._calc_commission(
                size,
                price,
                False,
                commission,
                min_commission,
                stamp_tax,
            )
            slip = self._calc_slippage(size, price, False, slippage_model, df)
            return [
                Trade(
                    datetime=self._get_datetime_int(df, exec_idx),
                    direction="BUY",
                    size=size,
                    price=price,
                    commission=comm,
                    slippage=slip,
                )
            ]
        elif signal.direction == "SELL":
            size = signal.size if signal.size > 0 else position
            if size <= 0:
                return []
            if size > position:
                size = position
            comm = self._calc_commission(
                size,
                price,
                True,
                commission,
                min_commission,
                stamp_tax,
            )
            slip = self._calc_slippage(size, price, True, slippage_model, df)
            return [
                Trade(
                    datetime=self._get_datetime_int(df, exec_idx),
                    direction="SELL",
                    size=size,
                    price=price,
                    commission=comm,
                    slippage=slip,
                )
            ]

        return []


class TWAPExecution(ExecutionModel):
    """时间加权平均价格执行。

    将订单均匀拆分为 n_bars 份，在连续 n_bars 根 K 线上执行。
    """

    def __init__(self, n_bars: int = 5) -> None:
        self._n_bars = max(1, n_bars)

    def execute(
        self,
        signal: Signal,
        df: pd.DataFrame,
        bar_idx: int,
        cash: float,
        position: float,
        position_mode: str,
        commission: float,
        min_commission: float,
        stamp_tax: float,
        slippage_model: SlippageModel | None,
    ) -> list[Trade]:
        if signal.direction == "BUY":
            return self._execute_buy(
                signal,
                df,
                bar_idx,
                cash,
                position_mode,
                commission,
                min_commission,
                stamp_tax,
                slippage_model,
            )
        return self._execute_sell(
            signal,
            df,
            bar_idx,
            position,
            commission,
            min_commission,
            stamp_tax,
            slippage_model,
        )

    def _execute_buy(
        self,
        signal: Signal,
        df: pd.DataFrame,
        bar_idx: int,
        cash: float,
        position_mode: str,
        commission: float,
        min_commission: float,
        stamp_tax: float,
        slippage_model: SlippageModel | None,
    ) -> list[Trade]:
        first_price = float(df["open"].iloc[bar_idx + 1]) if bar_idx + 1 < len(df) else 0
        if first_price <= 0:
            return []
        total_size = self._calc_buy_size(
            signal.size,
            first_price,
            cash,
            position_mode,
            commission,
        )
        if total_size <= 0:
            return []

        sub_size = int(total_size / self._n_bars / 100) * 100
        if sub_size <= 0:
            sub_size = 100

        trades: list[Trade] = []
        for i in range(self._n_bars):
            exec_idx = bar_idx + 1 + i
            if exec_idx >= len(df):
                break
            price = float(df["close"].iloc[exec_idx])
            remaining = total_size - sum(t.size for t in trades)
            actual_size = min(sub_size, remaining)
            actual_size = int(actual_size / 100) * 100
            if actual_size <= 0:
                break
            comm = self._calc_commission(
                actual_size,
                price,
                False,
                commission,
                min_commission,
                stamp_tax,
            )
            slip = self._calc_slippage(actual_size, price, False, slippage_model, df)
            trades.append(
                Trade(
                    datetime=self._get_datetime_int(df, exec_idx),
                    direction="BUY",
                    size=float(actual_size),
                    price=price,
                    commission=comm,
                    slippage=slip,
                )
            )
        return trades

    def _execute_sell(
        self,
        signal: Signal,
        df: pd.DataFrame,
        bar_idx: int,
        position: float,
        commission: float,
        min_commission: float,
        stamp_tax: float,
        slippage_model: SlippageModel | None,
    ) -> list[Trade]:
        total_size = signal.size if signal.size > 0 else position
        if total_size <= 0:
            return []

        sub_size = int(total_size / self._n_bars / 100) * 100
        if sub_size <= 0:
            sub_size = 100

        trades: list[Trade] = []
        for i in range(self._n_bars):
            exec_idx = bar_idx + 1 + i
            if exec_idx >= len(df):
                break
            price = float(df["close"].iloc[exec_idx])
            remaining = total_size - sum(t.size for t in trades)
            actual_size = min(sub_size, remaining)
            actual_size = int(actual_size / 100) * 100
            if actual_size <= 0:
                break
            comm = self._calc_commission(
                actual_size,
                price,
                True,
                commission,
                min_commission,
                stamp_tax,
            )
            slip = self._calc_slippage(actual_size, price, True, slippage_model, df)
            trades.append(
                Trade(
                    datetime=self._get_datetime_int(df, exec_idx),
                    direction="SELL",
                    size=float(actual_size),
                    price=price,
                    commission=comm,
                    slippage=slip,
                )
            )
        return trades


class VWAPExecution(ExecutionModel):
    """成交量加权平均价格执行。

    按历史成交量分布比例拆分订单。
    """

    def __init__(self, n_bars: int = 5, volume_lookback: int = 20) -> None:
        self._n_bars = max(1, n_bars)
        self._volume_lookback = max(1, volume_lookback)

    def execute(
        self,
        signal: Signal,
        df: pd.DataFrame,
        bar_idx: int,
        cash: float,
        position: float,
        position_mode: str,
        commission: float,
        min_commission: float,
        stamp_tax: float,
        slippage_model: SlippageModel | None,
    ) -> list[Trade]:
        if signal.direction == "BUY":
            return self._execute_buy(
                signal,
                df,
                bar_idx,
                cash,
                position_mode,
                commission,
                min_commission,
                stamp_tax,
                slippage_model,
            )
        return self._execute_sell(
            signal,
            df,
            bar_idx,
            position,
            commission,
            min_commission,
            stamp_tax,
            slippage_model,
        )

    def _get_volume_weights(self, df: pd.DataFrame, bar_idx: int) -> list[float]:
        """获取成交量权重分布。"""
        start = max(0, bar_idx - self._volume_lookback + 1)
        lookback = df.iloc[start : bar_idx + 1]
        if "volume" not in lookback.columns or len(lookback) == 0:
            return [1.0 / self._n_bars] * self._n_bars

        volumes = lookback["volume"].to_numpy()
        total_vol = float(volumes.sum())
        if total_vol <= 0:
            return [1.0 / self._n_bars] * self._n_bars

        weights: list[float] = []
        for i in range(self._n_bars):
            idx = max(0, len(volumes) - 1 - (i % max(1, len(volumes))))
            weights.append(float(volumes[idx]) / total_vol)
        total_w = sum(weights)
        if total_w <= 0:
            return [1.0 / self._n_bars] * self._n_bars
        return [w / total_w for w in weights]

    def _execute_buy(
        self,
        signal: Signal,
        df: pd.DataFrame,
        bar_idx: int,
        cash: float,
        position_mode: str,
        commission: float,
        min_commission: float,
        stamp_tax: float,
        slippage_model: SlippageModel | None,
    ) -> list[Trade]:
        first_price = float(df["open"].iloc[bar_idx + 1]) if bar_idx + 1 < len(df) else 0
        if first_price <= 0:
            return []
        total_size = self._calc_buy_size(
            signal.size,
            first_price,
            cash,
            position_mode,
            commission,
        )
        if total_size <= 0:
            return []

        weights = self._get_volume_weights(df, bar_idx)
        trades: list[Trade] = []
        for i in range(self._n_bars):
            exec_idx = bar_idx + 1 + i
            if exec_idx >= len(df):
                break
            price = float(df["close"].iloc[exec_idx])
            w = weights[i] if i < len(weights) else 1.0 / self._n_bars
            target = int(total_size * w / 100) * 100
            remaining = total_size - sum(t.size for t in trades)
            actual_size = min(target, remaining)
            actual_size = int(actual_size / 100) * 100
            if actual_size <= 0:
                continue
            comm = self._calc_commission(
                actual_size,
                price,
                False,
                commission,
                min_commission,
                stamp_tax,
            )
            slip = self._calc_slippage(actual_size, price, False, slippage_model, df)
            trades.append(
                Trade(
                    datetime=self._get_datetime_int(df, exec_idx),
                    direction="BUY",
                    size=float(actual_size),
                    price=price,
                    commission=comm,
                    slippage=slip,
                )
            )
        return trades

    def _execute_sell(
        self,
        signal: Signal,
        df: pd.DataFrame,
        bar_idx: int,
        position: float,
        commission: float,
        min_commission: float,
        stamp_tax: float,
        slippage_model: SlippageModel | None,
    ) -> list[Trade]:
        total_size = signal.size if signal.size > 0 else position
        if total_size <= 0:
            return []

        weights = self._get_volume_weights(df, bar_idx)
        trades: list[Trade] = []
        for i in range(self._n_bars):
            exec_idx = bar_idx + 1 + i
            if exec_idx >= len(df):
                break
            price = float(df["close"].iloc[exec_idx])
            w = weights[i] if i < len(weights) else 1.0 / self._n_bars
            target = int(total_size * w / 100) * 100
            remaining = total_size - sum(t.size for t in trades)
            actual_size = min(target, remaining)
            actual_size = int(actual_size / 100) * 100
            if actual_size <= 0:
                continue
            comm = self._calc_commission(
                actual_size,
                price,
                True,
                commission,
                min_commission,
                stamp_tax,
            )
            slip = self._calc_slippage(actual_size, price, True, slippage_model, df)
            trades.append(
                Trade(
                    datetime=self._get_datetime_int(df, exec_idx),
                    direction="SELL",
                    size=float(actual_size),
                    price=price,
                    commission=comm,
                    slippage=slip,
                )
            )
        return trades


class LimitExecution(ExecutionModel):
    """限价单执行。

    在目标价位挂单，仅当 bar_low <= price（买入）或 bar_high >= price（卖出）时成交。
    无限价时退化为 ImmediateExecution。
    """

    def __init__(self, ttl_bars: int = 5) -> None:
        self._ttl_bars = max(1, ttl_bars)
        self._fallback = ImmediateExecution()

    def execute(
        self,
        signal: Signal,
        df: pd.DataFrame,
        bar_idx: int,
        cash: float,
        position: float,
        position_mode: str,
        commission: float,
        min_commission: float,
        stamp_tax: float,
        slippage_model: SlippageModel | None,
    ) -> list[Trade]:
        if signal.price is None:
            return self._fallback.execute(
                signal,
                df,
                bar_idx,
                cash,
                position,
                position_mode,
                commission,
                min_commission,
                stamp_tax,
                slippage_model,
            )

        target_price = signal.price

        for i in range(self._ttl_bars):
            exec_idx = bar_idx + 1 + i
            if exec_idx >= len(df):
                break
            row = df.iloc[exec_idx]
            triggered = False
            if signal.direction == "BUY" and float(row["low"]) <= target_price:
                triggered = True
            elif signal.direction == "SELL" and float(row["high"]) >= target_price:
                triggered = True

            if triggered:
                if signal.direction == "BUY":
                    size = self._calc_buy_size(
                        signal.size,
                        target_price,
                        cash,
                        position_mode,
                        commission,
                    )
                    if size <= 0:
                        return []
                    comm = self._calc_commission(
                        size,
                        target_price,
                        False,
                        commission,
                        min_commission,
                        stamp_tax,
                    )
                    slip = self._calc_slippage(
                        size,
                        target_price,
                        False,
                        slippage_model,
                        df,
                    )
                else:
                    size = signal.size if signal.size > 0 else position
                    if size <= 0:
                        return []
                    if size > position:
                        size = position
                    comm = self._calc_commission(
                        size,
                        target_price,
                        True,
                        commission,
                        min_commission,
                        stamp_tax,
                    )
                    slip = self._calc_slippage(
                        size,
                        target_price,
                        True,
                        slippage_model,
                        df,
                    )

                return [
                    Trade(
                        datetime=self._get_datetime_int(df, exec_idx),
                        direction=signal.direction,
                        size=float(size),
                        price=target_price,
                        commission=comm,
                        slippage=slip,
                    )
                ]

        return []
