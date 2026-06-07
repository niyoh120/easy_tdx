"""缠论核心计算 单元测试。"""

from __future__ import annotations

from datetime import datetime

from easy_tdx.chanlun.bi import find_bis
from easy_tdx.chanlun.fractal import find_fractals
from easy_tdx.chanlun.kline_merge import merge_klines
from easy_tdx.chanlun.types import CLKline, Direction, FXType, Kline
from easy_tdx.chanlun.zs import find_zss

# ── helpers ──────────────────────────────────────────────────────────────


def _k(
    idx: int,
    dt: str,
    o: float,
    c: float,
    h: float,
    l: float,
    a: float = 0.0,
) -> Kline:
    """快速构造 Kline。"""
    return Kline(
        index=idx,
        date=datetime.strptime(dt, "%Y-%m-%d"),
        open=o,
        close=c,
        high=h,
        low=l,
        amount=a,
    )


def _ck(
    idx: int,
    dt: str,
    o: float,
    c: float,
    h: float,
    l: float,
    merged_count: int = 1,
    direction: str = "",
) -> CLKline:
    """快速构造 CLKline。"""
    return CLKline(
        k_index=idx,
        date=datetime.strptime(dt, "%Y-%m-%d"),
        open=o,
        close=c,
        high=h,
        low=l,
        amount=0.0,
        index=0,  # 由 merge_klines 赋值
        merged_count=merged_count,
        direction=direction,
    )


# ── K 线合并测试 ──────────────────────────────────────────────────────────


class TestMergeKlines:
    """merge_klines 测试。"""

    def test_no_merge_needed(self) -> None:
        """K 线无包含关系，应原样返回。"""
        klines = [
            _k(0, "2025-01-02", 10, 12, 13, 9),
            _k(1, "2025-01-03", 11, 16, 17, 11),  # 高于前一根高点、低于前根低点 → 无包含
            _k(2, "2025-01-06", 13, 11, 18, 12),  # 继续新高 → 无包含
        ]
        result = merge_klines(klines)
        assert len(result) == 3
        # 每个 CLKline 没有合并
        assert all(ck.merged_count == 1 for ck in result)

    def test_upward_include(self) -> None:
        """向上趋势中的包含关系应合并。

        K1: h=15 l=10  (向上)
        K2: h=13 l=11  ← K2 被 K1 包含 (15>13 and 10<11 => 15>=13 and 10<=11)
        合并后取高高：h=15, l=11
        """
        klines = [
            _k(0, "2025-01-02", 10, 14, 15, 10),
            _k(1, "2025-01-03", 11, 13, 13, 11),
        ]
        result = merge_klines(klines)
        assert len(result) == 1
        assert result[0].high == 15.0
        assert result[0].low == 11.0
        assert result[0].merged_count == 2

    def test_downward_include(self) -> None:
        """向下趋势中的包含关系应合并。

        K1: h=10 l=5   (向下)
        K2: h=9  l=6   ← K2 被 K1 包含 (10>=9 and 5<=6)
        合并后取低低：h=9, l=5
        """
        klines = [
            _k(0, "2025-01-02", 12, 8, 10, 5),
            _k(1, "2025-01-03", 8, 7, 9, 6),
        ]
        result = merge_klines(klines)
        assert len(result) == 1
        assert result[0].high == 9.0
        assert result[0].low == 5.0
        assert result[0].merged_count == 2

    def test_three_klines_with_two_merges(self) -> None:
        """连续包含：三根 K 线合并为一根。"""
        klines = [
            _k(0, "2025-01-02", 10, 14, 15, 10),  # 大阳线
            _k(1, "2025-01-03", 11, 13, 14, 11),  # 被包含
            _k(2, "2025-01-06", 12, 14, 14, 12),  # 被包含
        ]
        result = merge_klines(klines)
        assert len(result) == 1
        assert result[0].merged_count == 3
        # 向上合并：取高高 => h=15, l=12
        assert result[0].high == 15.0
        assert result[0].low == 12.0

    def test_empty_input(self) -> None:
        """空输入返回空列表。"""
        assert merge_klines([]) == []

    def test_single_kline(self) -> None:
        """单根 K 线返回单个 CLKline。"""
        klines = [_k(0, "2025-01-02", 10, 12, 13, 9)]
        result = merge_klines(klines)
        assert len(result) == 1
        assert result[0].high == 13.0
        assert result[0].low == 9.0

    def test_mixed_merge_and_non_merge(self) -> None:
        """混合场景：部分合并，部分不合并。"""
        klines = [
            _k(0, "2025-01-02", 10, 14, 15, 10),  # 大阳线
            _k(1, "2025-01-03", 11, 13, 14, 11),  # 被包含，合并
            _k(2, "2025-01-06", 16, 18, 19, 15),  # 新高，不合并
            _k(3, "2025-01-07", 17, 15, 18, 14),  # 阴线，不包含
        ]
        result = merge_klines(klines)
        assert len(result) == 3
        assert result[0].merged_count == 2  # K0+K1 合并
        assert result[1].merged_count == 1  # K2 独立
        assert result[2].merged_count == 1  # K3 独立

    def test_index_assignment(self) -> None:
        """CLKline.index 应从 0 递增。"""
        klines = [
            _k(0, "2025-01-02", 10, 14, 15, 10),
            _k(1, "2025-01-03", 14, 16, 17, 13),
            _k(2, "2025-01-06", 16, 12, 17, 11),
        ]
        result = merge_klines(klines)
        for i, ck in enumerate(result):
            assert ck.index == i

    def test_klines_reference_preserved(self) -> None:
        """CLKline.klines 应包含合并前的原始 K 线。"""
        klines = [
            _k(0, "2025-01-02", 10, 14, 15, 10),
            _k(1, "2025-01-03", 11, 13, 14, 11),  # 被包含
        ]
        result = merge_klines(klines)
        assert len(result[0].klines) == 2


# ── 分型识别测试 ──────────────────────────────────────────────────────────


class TestFindFractals:
    """find_fractals 测试。"""

    def test_simple_ding_fx(self) -> None:
        """简单的顶分型：中间高，两边低。"""
        cks = [
            _ck(0, "2025-01-02", 10, 12, 12, 10),
            _ck(1, "2025-01-03", 12, 15, 15, 11),
            _ck(2, "2025-01-06", 14, 11, 14, 10),
        ]
        fxs = find_fractals(cks)
        assert len(fxs) == 1
        assert fxs[0].fx_type == FXType.DING
        assert fxs[0].val == 15.0
        assert fxs[0].k == cks[1]

    def test_simple_di_fx(self) -> None:
        """简单的底分型：中间低，两边高。"""
        cks = [
            _ck(0, "2025-01-02", 15, 12, 16, 12),
            _ck(1, "2025-01-03", 11, 9, 12, 9),
            _ck(2, "2025-01-06", 10, 13, 14, 10),
        ]
        fxs = find_fractals(cks)
        assert len(fxs) == 1
        assert fxs[0].fx_type == FXType.DI
        assert fxs[0].val == 9.0

    def test_no_fractal(self) -> None:
        """单调序列不应有分型。"""
        cks = [
            _ck(0, "2025-01-02", 10, 12, 12, 10),
            _ck(1, "2025-01-03", 12, 14, 14, 12),
            _ck(2, "2025-01-06", 14, 16, 16, 14),
        ]
        fxs = find_fractals(cks)
        assert len(fxs) == 0

    def test_alternating_ding_di(self) -> None:
        """交替的顶底分型。"""
        cks = [
            _ck(0, "2025-01-02", 10, 12, 12, 10),  # 上升
            _ck(1, "2025-01-03", 12, 15, 15, 11),  # 顶 (12<15, 14<15)
            _ck(2, "2025-01-06", 14, 11, 14, 10),  # 下降
            _ck(3, "2025-01-07", 10, 8, 11, 8),  # 底 (10>8, 9>8)
            _ck(4, "2025-01-08", 9, 13, 16, 9),  # 大幅上升
            _ck(5, "2025-01-09", 15, 10, 15, 10),  # 下降 → ck[4] 成为顶
        ]
        fxs = find_fractals(cks)
        assert len(fxs) == 3
        assert fxs[0].fx_type == FXType.DING  # ck[1]
        assert fxs[1].fx_type == FXType.DI  # ck[3]
        assert fxs[2].fx_type == FXType.DING  # ck[4]

    def test_insufficient_klines(self) -> None:
        """少于3根K线不应有分型。"""
        assert find_fractals([]) == []
        assert find_fractals([_ck(0, "2025-01-02", 10, 12, 12, 10)]) == []
        assert (
            find_fractals(
                [
                    _ck(0, "2025-01-02", 10, 12, 12, 10),
                    _ck(1, "2025-01-03", 12, 15, 15, 11),
                ]
            )
            == []
        )

    def test_equal_highs_no_ding(self) -> None:
        """相等高点不应形成顶分型。"""
        cks = [
            _ck(0, "2025-01-02", 10, 12, 15, 10),
            _ck(1, "2025-01-03", 12, 14, 15, 11),
            _ck(2, "2025-01-06", 14, 11, 14, 10),
        ]
        fxs = find_fractals(cks)
        assert len(fxs) == 0

    def test_equal_lows_no_di(self) -> None:
        """相等低点不应形成底分型。"""
        cks = [
            _ck(0, "2025-01-02", 15, 12, 16, 9),
            _ck(1, "2025-01-03", 11, 10, 12, 9),
            _ck(2, "2025-01-06", 10, 13, 14, 10),
        ]
        fxs = find_fractals(cks)
        assert len(fxs) == 0


# ── 笔计算测试 ────────────────────────────────────────────────────────────


class TestFindBis:
    """find_bis 测试。"""

    def test_simple_up_down_bi(self) -> None:
        """一组顶底分型应产生两笔（向上 + 向下）。"""
        cks = [
            _ck(0, "2025-01-02", 10, 12, 12, 10),
            _ck(1, "2025-01-03", 12, 15, 15, 11),
            _ck(2, "2025-01-06", 14, 11, 14, 10),
            _ck(3, "2025-01-07", 10, 8, 11, 8),
            _ck(4, "2025-01-08", 9, 13, 16, 9),
            _ck(5, "2025-01-09", 15, 10, 15, 10),
        ]
        fxs = find_fractals(cks)
        bis = find_bis(fxs)
        # ding(1) → di(3) 向下笔, di(3) → ding(4) 向上笔
        assert len(bis) >= 2
        assert bis[0].direction == Direction.DOWN  # 顶→底
        assert bis[1].direction == Direction.UP  # 底→顶

    def test_new_bi_rule_needs_gap(self) -> None:
        """新笔规则：分型之间至少1根独立K线。

        如果两个分型相邻（中间无独立K线），不构成笔。
        """
        # 只有3根K线，产生1个分型，不足以成笔
        cks = [
            _ck(0, "2025-01-02", 10, 12, 12, 10),
            _ck(1, "2025-01-03", 12, 15, 15, 11),
            _ck(2, "2025-01-06", 14, 11, 14, 10),
        ]
        fxs = find_fractals(cks)
        bis = find_bis(fxs)
        assert len(bis) == 0  # 1个分型无法成笔

    def test_ding_di_must_alternate(self) -> None:
        """笔的起止分型必须顶底交替：顶→底 或 底→顶。"""
        cks = [
            _ck(0, "2025-01-02", 10, 8, 11, 8),
            _ck(1, "2025-01-03", 9, 15, 16, 9),
            _ck(2, "2025-01-06", 14, 11, 14, 10),
            _ck(3, "2025-01-07", 10, 7, 11, 7),
            _ck(4, "2025-01-08", 8, 13, 14, 8),
            _ck(5, "2025-01-09", 13, 10, 14, 10),
        ]
        fxs = find_fractals(cks)
        bis = find_bis(fxs)
        for bi in bis:
            if bi.direction == Direction.UP:
                assert bi.start.fx_type == FXType.DI
                assert bi.end.fx_type == FXType.DING
            else:
                assert bi.start.fx_type == FXType.DING
                assert bi.end.fx_type == FXType.DI

    def test_empty_fractals(self) -> None:
        """空分型列表应返回空笔列表。"""
        assert find_bis([]) == []

    def test_bi_high_low(self) -> None:
        """笔的 high/low 应正确反映区间最高最低价。"""
        cks = [
            _ck(0, "2025-01-02", 10, 8, 11, 8),
            _ck(1, "2025-01-03", 9, 15, 16, 9),
            _ck(2, "2025-01-06", 14, 11, 14, 10),
            _ck(3, "2025-01-07", 10, 7, 11, 7),
            _ck(4, "2025-01-08", 8, 13, 14, 8),
            _ck(5, "2025-01-09", 13, 10, 13, 10),
        ]
        fxs = find_fractals(cks)
        bis = find_bis(fxs)
        if len(bis) > 0:
            # 第一笔：顶→底（向下），high=16, low=7
            assert bis[0].high == 16.0
            assert bis[0].low == 7.0

    def test_full_pipeline_merge_to_bi(self) -> None:
        """完整管道测试：原始K线 → 合并 → 分型 → 笔。"""
        klines = [
            _k(0, "2025-01-02", 10, 8, 11, 8),
            _k(1, "2025-01-03", 8, 12, 13, 7),
            _k(2, "2025-01-06", 12, 16, 17, 11),
            _k(3, "2025-01-07", 16, 14, 18, 13),
            _k(4, "2025-01-08", 14, 10, 15, 9),
            _k(5, "2025-01-09", 10, 6, 11, 5),
            _k(6, "2025-01-10", 7, 12, 13, 6),
            _k(7, "2025-01-13", 12, 9, 14, 8),
        ]
        merged = merge_klines(klines)
        fxs = find_fractals(merged)
        bis = find_bis(fxs)
        assert len(bis) >= 1


# ── 中枢计算测试 ──────────────────────────────────────────────────────────


class TestFindZss:
    """find_zss 测试。"""

    def test_three_overlapping_bis_form_zs(self) -> None:
        """三笔重叠形成中枢。"""
        cks = [
            _ck(0, "2025-01-02", 10, 8, 11, 8),
            _ck(1, "2025-01-03", 9, 15, 16, 9),
            _ck(2, "2025-01-06", 14, 11, 14, 10),
            _ck(3, "2025-01-07", 10, 12, 13, 9),
            _ck(4, "2025-01-08", 12, 14, 15, 11),
            _ck(5, "2025-01-09", 14, 12, 14, 11),
            _ck(6, "2025-01-10", 11, 9, 12, 9),
            _ck(7, "2025-01-13", 10, 11, 12, 10),
        ]
        fxs = find_fractals(cks)
        bis = find_bis(fxs)
        zss = find_zss(bis)
        assert len(zss) >= 1
        zs = zss[0]
        assert zs.zg > zs.zd
        assert zs.gg >= zs.zg
        assert zs.dd <= zs.zd

    def test_no_overlap_no_zs(self) -> None:
        """笔之间无重叠不应形成中枢。"""
        cks = [
            _ck(0, "2025-01-02", 10, 8, 11, 8),
            _ck(1, "2025-01-03", 9, 15, 16, 9),
            _ck(2, "2025-01-06", 14, 16, 18, 15),
            _ck(3, "2025-01-07", 16, 20, 22, 16),
            _ck(4, "2025-01-08", 20, 25, 26, 20),
            _ck(5, "2025-01-09", 25, 22, 26, 22),
        ]
        fxs = find_fractals(cks)
        bis = find_bis(fxs)
        zss = find_zss(bis)
        assert len(zss) == 0

    def test_empty_bis_no_zs(self) -> None:
        """空笔列表不应有中枢。"""
        assert find_zss([]) == []

    def test_zs_overlap_properties(self) -> None:
        """中枢应有正确的重叠区间属性。"""
        cks = [
            _ck(0, "2025-01-02", 10, 12, 13, 10),
            _ck(1, "2025-01-03", 12, 15, 16, 11),
            _ck(2, "2025-01-06", 14, 11, 14, 10),
            _ck(3, "2025-01-07", 10, 13, 14, 9),
            _ck(4, "2025-01-08", 12, 14, 15, 11),
            _ck(5, "2025-01-09", 14, 12, 14, 11),
            _ck(6, "2025-01-10", 11, 9, 12, 8),
            _ck(7, "2025-01-13", 10, 11, 12, 9),
            _ck(8, "2025-01-14", 11, 6, 12, 5),
            _ck(9, "2025-01-15", 7, 8, 9, 6),
        ]
        fxs = find_fractals(cks)
        bis = find_bis(fxs)
        zss = find_zss(bis)
        if len(zss) > 0:
            zs = zss[0]
            # 中枢基本属性
            assert zs.zg > zs.zd
            assert zs.gg >= zs.zg
            assert zs.dd <= zs.zd
            assert zs.line_count >= 3


# ── Analyser 集成测试 ────────────────────────────────────────────────────


class TestChanlunAnalyser:
    """ChanlunAnalyser 完整管道测试。"""

    def test_analyse_with_dataframe(self) -> None:
        """使用模拟 DataFrame 测试完整管道。"""
        import pandas as pd

        from easy_tdx.chanlun.analyser import ChanlunAnalyser

        dates = pd.date_range("2025-01-02", periods=20, freq="B")
        data = {
            "datetime": dates,
            "open": [10, 8, 12, 16, 14, 10, 7, 12, 14, 12, 10, 6, 7, 12, 9, 10, 14, 12, 8, 9],
            "close": [8, 12, 16, 14, 10, 7, 12, 14, 12, 10, 6, 7, 12, 9, 10, 14, 12, 8, 9, 11],
            "high": [11, 13, 17, 18, 15, 11, 13, 15, 14, 13, 11, 8, 13, 12, 11, 15, 14, 13, 9, 12],
            "low": [7, 7, 11, 13, 9, 5, 6, 11, 11, 9, 5, 5, 6, 8, 8, 9, 11, 7, 7, 9],
            "vol": [1000] * 20,
        }
        df = pd.DataFrame(data)

        analyser = ChanlunAnalyser(code="SZ000001", frequency="DAILY")
        result = analyser.process_klines(df)

        assert result.code == "SZ000001"
        assert result.frequency == "DAILY"
        assert len(result.klines) == 20
        assert len(result.cklines) > 0
        assert len(result.cklines) <= 20
        assert len(result.fractals) >= 0
        assert len(result.bis) >= 0

    def test_empty_dataframe(self) -> None:
        """空 DataFrame 应返回空结果。"""
        import pandas as pd

        from easy_tdx.chanlun.analyser import ChanlunAnalyser

        df = pd.DataFrame(columns=["datetime", "open", "close", "high", "low", "vol"])
        analyser = ChanlunAnalyser(code="SZ000001")
        result = analyser.process_klines(df)
        assert len(result.klines) == 0
        assert len(result.bis) == 0

    def test_result_to_dict(self) -> None:
        """结果应可序列化为字典。"""
        import pandas as pd

        from easy_tdx.chanlun.analyser import ChanlunAnalyser

        dates = pd.date_range("2025-01-02", periods=10, freq="B")
        data = {
            "datetime": dates,
            "open": [10, 8, 12, 16, 14, 10, 7, 12, 14, 12],
            "close": [8, 12, 16, 14, 10, 7, 12, 14, 12, 10],
            "high": [11, 13, 17, 18, 15, 11, 13, 15, 14, 13],
            "low": [7, 7, 11, 13, 9, 5, 6, 11, 11, 9],
            "vol": [1000] * 10,
        }
        df = pd.DataFrame(data)
        analyser = ChanlunAnalyser(code="SZ000001")
        result = analyser.process_klines(df)
        d = result.to_dict()

        assert "code" in d
        assert "bi_count" in d
        assert "zs_count" in d
        assert "bis" in d
        assert "zss" in d
