"""权重优化器。"""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd


class WeightOptimizer(ABC):
    """权重优化器基类。"""

    @abstractmethod
    def optimize(
        self,
        factor_scores: pd.DataFrame,
        n_stocks: int = 50,
        **kwargs: object,
    ) -> dict[str, float]:
        """返回 {code: weight}，权重和为 1.0。"""
        ...


_OPTIMIZER_REGISTRY: dict[str, type[WeightOptimizer]] = {}


def register_optimizer(name: str) -> type[WeightOptimizer]:
    """注册优化器。"""

    def wrapper(cls: type[WeightOptimizer]) -> type[WeightOptimizer]:
        _OPTIMIZER_REGISTRY[name] = cls
        return cls

    return wrapper


def get_optimizer(name: str) -> WeightOptimizer:
    """按名称获取优化器实例。"""
    if name not in _OPTIMIZER_REGISTRY:
        raise ValueError(f"未知优化器: {name!r}。可用: {sorted(_OPTIMIZER_REGISTRY.keys())}")
    return _OPTIMIZER_REGISTRY[name]()


@register_optimizer("equal")
class EqualWeightOptimizer(WeightOptimizer):
    """等权 — 取 top-N 等权分配。"""

    def optimize(
        self,
        factor_scores: pd.DataFrame,
        n_stocks: int = 50,
        **kwargs: object,
    ) -> dict[str, float]:
        if factor_scores.empty or "score" not in factor_scores.columns:
            return {}
        top = factor_scores.nlargest(n_stocks, "score")
        if len(top) == 0:
            return {}
        w = 1.0 / len(top)
        return {row["code"]: w for _, row in top.iterrows()}


@register_optimizer("factor_weighted")
class FactorWeightedOptimizer(WeightOptimizer):
    """因子加权 — 按因子得分加权。"""

    def optimize(
        self,
        factor_scores: pd.DataFrame,
        n_stocks: int = 50,
        **kwargs: object,
    ) -> dict[str, float]:
        top = factor_scores.nlargest(n_stocks, "score")
        if len(top) == 0:
            return {}
        scores = top["score"].to_numpy(dtype=np.float64)
        if len(scores) > 10:
            q95 = np.percentile(scores, 95)
            q05 = np.percentile(scores, 5)
            scores = np.clip(scores, q05, q95)
        scores = scores - scores.min() + 1e-8
        total = scores.sum()
        if total == 0:
            w = 1.0 / len(top)
            return {row["code"]: w for _, row in top.iterrows()}
        weights = scores / total
        return {row["code"]: float(weights[i]) for i, (_, row) in enumerate(top.iterrows())}


@register_optimizer("risk_parity")
class RiskParityOptimizer(WeightOptimizer):
    """风险平价 — 每只股票贡献相等风险。"""

    def optimize(
        self,
        factor_scores: pd.DataFrame,
        n_stocks: int = 50,
        **kwargs: object,
    ) -> dict[str, float]:
        top = factor_scores.nlargest(n_stocks, "score")
        if len(top) == 0:
            return {}
        if "volatility" in top.columns:
            vol = top["volatility"].to_numpy(dtype=np.float64)
        else:
            scores = top["score"].abs().to_numpy(dtype=np.float64)
            vol = 1.0 / (scores + 1e-8)
        vol = np.maximum(vol, 1e-8)
        inv_vol = 1.0 / vol
        total = inv_vol.sum()
        weights = inv_vol / total
        return {row["code"]: float(weights[i]) for i, (_, row) in enumerate(top.iterrows())}


@register_optimizer("mean_variance")
class MeanVarianceOptimizer(WeightOptimizer):
    """均值方差优化 — Markowitz 模型（可选 scipy）。"""

    def optimize(
        self,
        factor_scores: pd.DataFrame,
        n_stocks: int = 50,
        **kwargs: object,
    ) -> dict[str, float]:
        try:
            from scipy.optimize import minimize  # noqa: F401

            return self._optimize_with_scipy(factor_scores, n_stocks)
        except ImportError:
            fallback = EqualWeightOptimizer()
            return fallback.optimize(factor_scores, n_stocks)

    def _optimize_with_scipy(
        self,
        factor_scores: pd.DataFrame,
        n_stocks: int,
    ) -> dict[str, float]:
        from scipy.optimize import minimize as _minimize  # type: ignore[import]

        top = factor_scores.nlargest(n_stocks, "score")
        if len(top) == 0:
            return {}
        n = len(top)
        scores = top["score"].to_numpy(dtype=np.float64)
        variances = 1.0 / (np.abs(scores) + 1e-8) ** 2
        cov = np.diag(variances)

        def objective(w: np.ndarray) -> float:
            return float(w @ cov @ w)

        constraints = {"type": "eq", "fun": lambda w: float(np.sum(w) - 1.0)}
        bounds = [(0.0, 0.1)] * n
        x0 = np.ones(n) / n
        result = _minimize(objective, x0, method="SLSQP", bounds=bounds, constraints=constraints)
        weights = result.x if result.success else np.ones(n) / n
        return {row["code"]: float(weights[i]) for i, (_, row) in enumerate(top.iterrows())}
