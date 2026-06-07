"""多级别联立分析。

支持同时分析多个 K 线周期（如日线 + 30 分钟）的缠论数据，
查看高级别笔在低级别中的走势结构，辅助判断买卖点的有效性。
"""

from __future__ import annotations

from easy_tdx.chanlun.analyser import ChanlunAnalyser, ChanlunResult
from easy_tdx.chanlun.types import BI


class MultiLevelAnalyser:
    """多级别缠论分析器。

    管理多个 ChanlunAnalyser 实例，每个对应一个 K 线周期。
    支持跨级别查询：高级别笔对应的低级别走势信息。

    用法::

        mla = MultiLevelAnalyser()
        mla.add_level("daily", ChanlunAnalyser("SZ000001", "DAILY"))
        mla.add_level("30min", ChanlunAnalyser("SZ000001", "30MIN"))
        mla.process("daily", df_daily)
        mla.process("30min", df_30min)

        # 查看日线最后一笔在 30 分钟级别中的走势
        info = mla.query_low_level_qs("daily", "30min", last_bi)
    """

    def __init__(self) -> None:
        self._analysers: dict[str, ChanlunAnalyser] = {}

    def add_level(self, name: str, analyser: ChanlunAnalyser) -> None:
        """添加一个分析级别。

        Args:
            name: 级别名称（如 "daily", "30min"）
            analyser: 对应的 ChanlunAnalyser 实例
        """
        self._analysers[name] = analyser

    def process(self, level: str, df: object) -> ChanlunResult:
        """处理指定级别的 K 线数据。

        Args:
            level: 级别名称
            df: K 线 DataFrame

        Returns:
            该级别的缠论分析结果
        """
        import pandas as pd

        if level not in self._analysers:
            raise KeyError(f"未注册的级别: {level}，可用: {list(self._analysers.keys())}")
        assert isinstance(df, pd.DataFrame)
        return self._analysers[level].process_klines(df)

    def get_result(self, level: str) -> ChanlunResult | None:
        """获取指定级别的分析结果。"""
        if level in self._analysers:
            return self._analysers[level].result
        return None

    def results(self) -> dict[str, ChanlunResult]:
        """获取所有级别的分析结果。"""
        return {name: a.result for name, a in self._analysers.items()}

    def query_low_level_qs(
        self,
        high_level: str,
        low_level: str,
        high_bi: BI,
    ) -> dict[str, int]:
        """查询高级别笔在低级别中的走势信息。

        查找低级别中时间范围落在高级别笔内的所有笔和中枢，
        统计形成趋势/盘整的情况。

        Args:
            high_level: 高级别名称
            low_level: 低级别名称
            high_bi: 高级别的笔

        Returns:
            {"bi_count": 低级别笔数, "zs_count": 低级别中枢数,
             "has_trend": 是否形成趋势, "has_consolidation": 是否形成盘整}
        """
        high_result = self.get_result(high_level)
        low_result = self.get_result(low_level)

        if high_result is None or low_result is None:
            return {"bi_count": 0, "zs_count": 0, "has_trend": False, "has_consolidation": False}

        # 高级别笔的时间范围
        start_date = high_bi.start.k.date
        end_date = high_bi.end.k.date

        # 筛选低级别中时间范围内的笔
        low_bis = [
            bi
            for bi in low_result.bis
            if bi.start.k.date >= start_date and bi.end.k.date <= end_date
        ]

        # 筛选低级别中枢
        low_zss = [
            zs
            for zs in low_result.zss
            if zs.start is not None
            and zs.end is not None
            and zs.start.k.date >= start_date
            and zs.end.k.date <= end_date
        ]

        has_trend = len(low_zss) >= 2
        has_consolidation = len(low_zss) >= 1

        return {
            "bi_count": len(low_bis),
            "zs_count": len(low_zss),
            "has_trend": has_trend,
            "has_consolidation": has_consolidation,
        }
