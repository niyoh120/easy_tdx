"""K线 / 分时 / 逐笔成交路由。"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from easy_tdx.web.convert import category_from_str, market_from_str
from easy_tdx.web.deps import get_client
from easy_tdx.web.schemas import DataFrameResponse

router = APIRouter(tags=["bars"])


def _df_resp(df: Any) -> DataFrameResponse:
    return DataFrameResponse.from_dataframe(df)


@router.get("/bars", response_model=DataFrameResponse)
async def security_bars(
    market: str = Query(..., description="市场: SZ, SH, BJ"),
    code: str = Query(..., min_length=6, max_length=6),
    category: str = Query(
        "DAY",
        description="K线周期: MIN_1, MIN_5, MIN_15, MIN_30, MIN_60, DAY, WEEK, MONTH, YEAR",
    ),
    start: int = Query(0, ge=0),
    count: int = Query(800, ge=1, le=800),
    bar_time: str = Query(
        "start", description="时间戳: start=bar开始时间(默认) / end=bar结束时间(对齐Tushare)"
    ),
    client: Any = Depends(get_client),
) -> DataFrameResponse:
    """获取股票K线数据。"""
    df = await client.get_security_bars(
        market_from_str(market), code, category_from_str(category), start, count, bar_time=bar_time
    )
    return _df_resp(df)


@router.get("/bars/index", response_model=DataFrameResponse)
async def index_bars(
    market: str = Query(..., description="市场: SZ, SH"),
    code: str = Query(..., min_length=6, max_length=6),
    category: str = Query("DAY", description="K线周期"),
    start: int = Query(0, ge=0),
    count: int = Query(800, ge=1, le=800),
    bar_time: str = Query(
        "start", description="时间戳: start=bar开始时间(默认) / end=bar结束时间(对齐Tushare)"
    ),
    client: Any = Depends(get_client),
) -> DataFrameResponse:
    """获取指数K线数据。"""
    df = await client.get_index_bars(
        market_from_str(market), code, category_from_str(category), start, count, bar_time=bar_time
    )
    return _df_resp(df)


@router.get("/minute", response_model=DataFrameResponse)
async def minute_time(
    market: str = Query(..., description="市场: SZ, SH"),
    code: str = Query(..., min_length=6, max_length=6),
    client: Any = Depends(get_client),
) -> DataFrameResponse:
    """获取今日分时数据。"""
    df = await client.get_minute_time_data(market_from_str(market), code)
    return _df_resp(df)


@router.get("/minute/history", response_model=DataFrameResponse)
async def history_minute_time(
    market: str = Query(..., description="市场: SZ, SH"),
    code: str = Query(..., min_length=6, max_length=6),
    date: int = Query(..., description="日期 YYYYMMDD"),
    client: Any = Depends(get_client),
) -> DataFrameResponse:
    """获取历史某日分时数据。"""
    df = await client.get_history_minute_time_data(market_from_str(market), code, date)
    return _df_resp(df)


@router.get("/transaction", response_model=DataFrameResponse)
async def transaction_data(
    market: str = Query(..., description="市场: SZ, SH"),
    code: str = Query(..., min_length=6, max_length=6),
    start: int = Query(0, ge=0),
    count: int = Query(800, ge=1, le=800),
    client: Any = Depends(get_client),
) -> DataFrameResponse:
    """获取当日逐笔成交。"""
    df = await client.get_transaction_data(market_from_str(market), code, start, count)
    return _df_resp(df)


@router.get("/transaction/history", response_model=DataFrameResponse)
async def history_transaction_data(
    market: str = Query(..., description="市场: SZ, SH"),
    code: str = Query(..., min_length=6, max_length=6),
    date: int = Query(..., description="日期 YYYYMMDD"),
    start: int = Query(0, ge=0),
    count: int = Query(800, ge=1, le=800),
    client: Any = Depends(get_client),
) -> DataFrameResponse:
    """获取历史逐笔成交。"""
    df = await client.get_history_transaction_data(
        market_from_str(market), code, date, start, count
    )
    return _df_resp(df)
