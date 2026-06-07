"""缠论分析器主入口。

ChanlunAnalyser 接收 easy_tdx 的 K 线 DataFrame，
内部执行完整的缠论计算管道：
K线合并 → 分型识别 → 笔计算 → 中枢计算 → 线段 → 买卖点 → 背驰。
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from easy_tdx.chanlun.beichi import check_bi_beichi  # noqa: F401
from easy_tdx.chanlun.bi import find_bis
from easy_tdx.chanlun.config import ChanlunConfig
from easy_tdx.chanlun.fractal import find_fractals
from easy_tdx.chanlun.kline_merge import merge_klines
from easy_tdx.chanlun.macd import calc_macd  # noqa: F401
from easy_tdx.chanlun.mmd import find_mmds  # noqa: F401
from easy_tdx.chanlun.types import BC, BI, FX, MMD, XD, ZS, CLKline, Kline
from easy_tdx.chanlun.xd import find_xds  # noqa: F401
from easy_tdx.chanlun.zs import find_zss


def _df_to_klines(df: pd.DataFrame) -> list[Kline]:
    """将 easy_tdx K 线 DataFrame 转为缠论 Kline 列表。

    期望 DataFrame 包含列：datetime, open, close, high, low, vol
    """
    klines: list[Kline] = []
    for i, row in enumerate(df.itertuples()):
        dt = getattr(row, "datetime", None) or getattr(row, "date", None)
        if dt is None:
            continue
        vol = getattr(row, "vol", 0.0) or 0.0
        klines.append(
            Kline(
                index=i,
                date=dt,
                open=float(row.open),
                close=float(row.close),
                high=float(row.high),
                low=float(row.low),
                amount=float(vol),
            )
        )
    return klines


@dataclass
class ChanlunResult:
    """缠论分析结果。"""

    code: str = ""
    frequency: str = ""
    klines: list[Kline] = field(default_factory=list)
    cklines: list[CLKline] = field(default_factory=list)
    fractals: list[FX] = field(default_factory=list)
    bis: list[BI] = field(default_factory=list)
    zss: list[ZS] = field(default_factory=list)
    xds: list[XD] = field(default_factory=list)
    mmds: list[MMD] = field(default_factory=list)
    bcs: list[BC] = field(default_factory=list)
    macd: dict[str, list[float]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """将结果转为可序列化的字典（用于 JSON 输出）。"""
        return {
            "code": self.code,
            "frequency": self.frequency,
            "kline_count": len(self.klines),
            "ckline_count": len(self.cklines),
            "fractal_count": len(self.fractals),
            "bi_count": len(self.bis),
            "zs_count": len(self.zss),
            "xd_count": len(self.xds),
            "mmd_count": len(self.mmds),
            "bc_count": len(self.bcs),
            "bis": [
                {
                    "index": bi.index,
                    "direction": bi.direction.value,
                    "start_date": bi.start.k.date.strftime("%Y-%m-%d"),
                    "end_date": bi.end.k.date.strftime("%Y-%m-%d"),
                    "high": round(bi.high, 2),
                    "low": round(bi.low, 2),
                    "done": bi.is_done(),
                }
                for bi in self.bis
            ],
            "zss": [
                {
                    "index": zs.index,
                    "zg": round(zs.zg, 2),
                    "zd": round(zs.zd, 2),
                    "gg": round(zs.gg, 2),
                    "dd": round(zs.dd, 2),
                    "line_count": zs.line_count,
                    "done": zs.done,
                }
                for zs in self.zss
            ],
            "xds": [
                {
                    "index": xd.index,
                    "direction": xd.direction.value,
                    "start_date": xd.start.k.date.strftime("%Y-%m-%d"),
                    "end_date": xd.end.k.date.strftime("%Y-%m-%d"),
                    "high": round(xd.high, 2),
                    "low": round(xd.low, 2),
                }
                for xd in self.xds
            ],
            "mmds": [
                {
                    "type": mmd.mmd_type.value,
                    "msg": mmd.msg,
                }
                for mmd in self.mmds
            ],
            "bcs": [
                {
                    "type": bc.bc_type.value,
                    "bc": bc.bc,
                    "msg": bc.msg,
                }
                for bc in self.bcs
            ],
        }


class ChanlunAnalyser:
    """缠论分析器。

    接收 easy_tdx K 线 DataFrame，执行缠论计算管道。

    用法：
        analyser = ChanlunAnalyser("SZ000001", "DAILY")
        analyser.process_klines(df)
        result = analyser.result
    """

    def __init__(
        self,
        code: str = "",
        frequency: str = "",
        config: ChanlunConfig | None = None,
    ) -> None:
        self._code = code
        self._frequency = frequency
        self._config = config or ChanlunConfig()
        self._result = ChanlunResult(
            code=code,
            frequency=frequency,
        )

    @property
    def config(self) -> ChanlunConfig:
        return self._config

    @property
    def result(self) -> ChanlunResult:
        return self._result

    def process_klines(self, df: pd.DataFrame) -> ChanlunResult:
        """处理 K 线 DataFrame，执行缠论计算管道。

        Args:
            df: easy_tdx 返回的 K 线 DataFrame

        Returns:
            ChanlunResult 包含所有缠论计算结果
        """
        # Step 1: DataFrame → Kline 列表
        klines = _df_to_klines(df)
        self._result.klines = klines

        if not klines:
            return self._result

        # Step 2: K线包含处理
        cklines = merge_klines(klines)
        self._result.cklines = cklines

        # Step 3: 分型识别
        fractals = find_fractals(cklines, self._config)
        self._result.fractals = fractals

        # Step 4: 笔计算
        bis = find_bis(fractals, self._config)
        self._result.bis = bis

        # Step 5: 中枢计算
        zss = find_zss(bis, self._config)
        self._result.zss = zss

        # Step 6: MACD 计算
        closes = [k.close for k in klines]
        self._result.macd = calc_macd(
            closes, self._config.macd_fast, self._config.macd_slow, self._config.macd_signal
        )

        # Step 7: 线段计算
        xds = find_xds(bis, self._config)
        self._result.xds = xds

        # Step 8: 买卖点识别
        mmds = find_mmds(bis, zss, self._config)
        self._result.mmds = mmds

        # Step 9: 背驰判断
        bcs = check_bi_beichi(bis, zss, self._config)
        self._result.bcs = bcs

        return self._result

    def get_bis(self) -> list[BI]:
        return self._result.bis

    def get_zss(self) -> list[ZS]:
        return self._result.zss

    def get_fxs(self) -> list[FX]:
        return self._result.fractals

    def get_klines(self) -> list[Kline]:
        return self._result.klines

    def get_cklines(self) -> list[CLKline]:
        return self._result.cklines
