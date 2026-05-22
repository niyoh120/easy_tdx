"""财务数据命令（暂未实现）。"""

from __future__ import annotations

import click


@click.command("f10")
@click.argument("market")
@click.argument("code")
def f10(market: str, code: str) -> None:
    """获取 F10 财务数据（暂未实现）。

    示例：

      easy-tdx f10 SZ 000001
    """
    raise click.UsageError("f10 命令暂未实现，请使用 TdxClient.get_finance_info() API")


@click.command("fund-flow")
@click.argument("market")
@click.argument("code")
@click.option("--start", default=0, type=int, help="起始偏移")
@click.option("--count", default=30, type=int, help="请求数量")
def fund_flow(market: str, code: str, start: int, count: int) -> None:
    """获取历史资金流向（暂未实现）。

    示例：

      easy-tdx fund-flow SZ 000001
    """
    raise click.UsageError("fund-flow 命令暂未实现，请使用 TdxClient.get_history_fund_flow() API")
