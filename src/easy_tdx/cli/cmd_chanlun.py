"""缠论分析命令。"""

from __future__ import annotations

import json

import click


@click.command()
@click.argument("market")
@click.argument("code")
@click.option(
    "--period", default="DAILY", help="K线周期: DAILY/5MIN/15MIN/30MIN/60MIN/1MIN/WEEKLY/MONTHLY"
)
@click.option("--count", default=800, type=int, help="K线数量")
@click.option("--adjust", default="NONE", help="复权: NONE/QFQ/HFQ")
@click.option("--table", "use_table", is_flag=True, help="表格输出")
@click.option("--output", "output_fmt", type=click.Choice(["json", "table", "csv"]), default="json")
def chanlun(
    market: str,
    code: str,
    period: str,
    count: int,
    adjust: str,
    use_table: bool,
    output_fmt: str,
) -> None:
    """缠论分析：计算 K 线的笔、中枢等缠论指标。

    示例：

      easy-tdx chanlun SZ 000001

      easy-tdx chanlun SH 600519 --adjust QFQ --table

      easy-tdx chanlun SZ 000001 --period 30MIN
    """
    from ..chanlun.analyser import ChanlunAnalyser
    from .conn import get_mac_client
    from .parsers import parse_adjust, parse_market, parse_period

    mkt = parse_market(market)
    with get_mac_client() as client:
        df = client.get_stock_kline(
            mkt,
            code,
            period=parse_period(period),
            start=0,
            count=count,
            adjust=parse_adjust(adjust),
        )

    analyser = ChanlunAnalyser(code=code, frequency=period)
    result = analyser.process_klines(df)

    result_dict = result.to_dict()

    fmt = "table" if use_table else output_fmt
    if fmt == "json":
        click.echo(json.dumps(result_dict, ensure_ascii=False, indent=2))
    elif fmt == "table":
        _print_table(result_dict)
    else:
        click.echo(json.dumps(result_dict, ensure_ascii=False))


def _print_table(result: dict) -> None:
    """以表格形式输出缠论分析结果。"""
    click.echo(f"标的: {result['code']}  周期: {result['frequency']}")
    click.echo(f"原始K线: {result['kline_count']}  缠论K线: {result['ckline_count']}")
    click.echo(
        f"分型: {result['fractal_count']}  笔: {result['bi_count']}  "
        f"中枢: {result['zs_count']}  线段: {result.get('xd_count', 0)}"
    )
    mmd_count = result.get("mmd_count", 0)
    bc_count = result.get("bc_count", 0)
    if mmd_count or bc_count:
        click.echo(f"买卖点: {mmd_count}  背驰: {bc_count}")
    click.echo()

    if result["bis"]:
        click.echo("── 笔 ──")
        for bi in result["bis"]:
            direction = "↑" if bi["direction"] == "up" else "↓"
            done = "✓" if bi["done"] else "…"
            click.echo(
                f"  [{bi['index']}] {direction} "
                f"{bi['start_date']} → {bi['end_date']} "
                f"h={bi['high']} l={bi['low']} {done}"
            )
        click.echo()

    if result["zss"]:
        click.echo("── 中枢 ──")
        for zs in result["zss"]:
            done = "✓" if zs["done"] else "…"
            click.echo(
                f"  [{zs['index']}] "
                f"zg={zs['zg']} zd={zs['zd']} "
                f"gg={zs['gg']} dd={zs['dd']} "
                f"lines={zs['line_count']} {done}"
            )
        click.echo()

    if result.get("xds"):
        click.echo("── 线段 ──")
        for xd in result["xds"]:
            direction = "↑" if xd["direction"] == "up" else "↓"
            click.echo(
                f"  [{xd['index']}] {direction} "
                f"{xd['start_date']} → {xd['end_date']} "
                f"h={xd['high']} l={xd['low']}"
            )
        click.echo()

    if result.get("mmds"):
        click.echo("── 买卖点 ──")
        for mmd in result["mmds"]:
            click.echo(f"  {mmd['type']}: {mmd['msg']}")
        click.echo()

    if result.get("bcs"):
        click.echo("── 背驰 ──")
        for bc in result["bcs"]:
            status = "✓" if bc["bc"] else "✗"
            click.echo(f"  [{status}] {bc['type']}: {bc['msg']}")
