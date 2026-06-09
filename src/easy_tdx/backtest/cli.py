"""回测 CLI 命令。"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import click


@click.command()
@click.argument("market")
@click.argument("code")
@click.option("--strategy", "strategy_str", default=None, help="DSL 策略表达式 (P1)")
@click.option("--strategy-file", "strategy_file", default=None, help="Python 策略文件路径")
@click.option("--cash", default=100000.0, type=float, help="初始资金")
@click.option("--commission", default=0.0003, type=float, help="佣金率")
@click.option(
    "--execution",
    default="next_open",
    type=click.Choice(["next_open", "next_close", "this_close", "worst", "best"]),
    help="成交价规则",
)
@click.option("--period", default="DAILY", help="K线周期")
@click.option("--adjust", default="NONE", help="复权: NONE/QFQ/HFQ")
@click.option("--count", default=500, type=int, help="K线数量")
@click.option("--indicators", default=None, help="预计算指标（逗号分隔）")
@click.option("--table", "use_table", is_flag=True, help="表格输出")
@click.option("--output", "output_fmt", type=click.Choice(["json", "table", "csv"]), default="json")
def backtest(
    market: str,
    code: str,
    strategy_str: str | None,
    strategy_file: str | None,
    cash: float,
    commission: float,
    execution: str,
    period: str,
    adjust: str,
    count: int,
    indicators: str | None,
    use_table: bool,
    output_fmt: str,
) -> None:
    """回测引擎：执行策略并返回绩效报告。

    示例：

      easy-tdx backtest SZ 000001 --strategy-file my_strategy.py

      easy-tdx backtest SH 600519 --strategy-file ma_cross.py --table

      easy-tdx backtest SZ 000001 --strategy-file my_strategy.py --indicators MACD,KDJ
    """
    from ..cli.conn import get_mac_client
    from ..cli.parsers import parse_adjust, parse_market, parse_period
    from ..backtest.engine import BacktestEngine
    from ..indicator import compute_indicators

    # 1. 加载策略
    strategy = _load_strategy(strategy_str, strategy_file)
    if strategy is None:
        click.echo("错误: 必须指定 --strategy-file 或 --strategy", err=True)
        raise SystemExit(1)

    # 2. 获取数据
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

    # 3. 预计算指标
    if indicators:
        indicator_list = [ind.strip() for ind in indicators.split(",")]
        df = compute_indicators(df, indicator_list)

    # 4. 创建引擎并运行
    engine = BacktestEngine(
        strategy=strategy,
        cash=cash,
        commission=commission,
        execution=execution,
    )
    result = engine.run(df)

    # 5. 输出结果
    fmt = "table" if use_table else output_fmt
    if fmt == "json":
        click.echo(result.to_json())
    elif fmt == "table":
        _print_table(result)
    else:
        click.echo(result.to_json())


def _load_strategy(
    strategy_str: str | None, strategy_file: str | None
) -> type | None:
    """加载策略类。

    优先从 Python 文件加载，其次从 DSL 表达式加载（未实现）。

    Args:
        strategy_str: DSL 策略表达式
        strategy_file: Python 策略文件路径

    Returns:
        Strategy 子类
    """
    from ..backtest.strategy import Strategy

    if strategy_file:
        return _load_strategy_from_file(strategy_file)

    if strategy_str:
        click.echo("错误: DSL 策略表达式尚未实现", err=True)
        return None

    return None


def _load_strategy_from_file(path: str) -> type:
    """从 Python 文件加载 Strategy 子类。

    Args:
        path: Python 文件路径

    Returns:
        Strategy 子类
    """
    from ..backtest.strategy import Strategy

    file_path = Path(path)
    if not file_path.exists():
        click.echo(f"错误: 文件不存在: {path}", err=True)
        raise SystemExit(1)

    spec = importlib.util.spec_from_file_location("strategy_module", file_path)
    if spec is None or spec.loader is None:
        click.echo(f"错误: 无法加载文件: {path}", err=True)
        raise SystemExit(1)

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # 查找 Strategy 子类
    strategy_classes = []
    for name in dir(module):
        obj = getattr(module, name)
        try:
            if (
                isinstance(obj, type)
                and issubclass(obj, Strategy)
                and obj is not Strategy
            ):
                strategy_classes.append(obj)
        except TypeError:
            pass

    if not strategy_classes:
        click.echo(f"错误: 文件中未找到 Strategy 子类: {path}", err=True)
        raise SystemExit(1)

    if len(strategy_classes) > 1:
        click.echo(f"警告: 文件包含多个 Strategy 子类，使用第一个: {path}", err=True)

    return strategy_classes[0]


def _print_table(result) -> None:
    """以表格形式输出回测结果。"""
    perf = result.performance
    config = result.config

    click.echo("=== 回测绩效概要 ===")
    click.echo(f"总收益率: {perf.get('total_return', 0):.2%}")
    click.echo(f"年化收益: {perf.get('annual_return', 0):.2%}")
    click.echo(f"最大回撤: {perf.get('max_drawdown', 0):.2%}")
    click.echo(f"夏普比率: {perf.get('sharpe_ratio', 0):.2f}")
    click.echo(f"胜率: {perf.get('win_rate', 0):.2%}")
    click.echo(f"交易次数: {perf.get('total_trades', 0)}")
    click.echo()

    click.echo("=== 配置参数 ===")
    click.echo(f"初始资金: {config.get('cash', 0):.2f}")
    click.echo(f"佣金率: {config.get('commission', 0):.4f}")
    click.echo(f"成交规则: {config.get('execution', 'next_open')}")
    click.echo()

    if config.get("future_leak_warning"):
        click.echo("!!! 警告: 策略可能存在未来函数（使用未来数据）")
        click.echo()

    if not result.trades.empty:
        click.echo("=== 最近交易记录 ===")
        recent_trades = result.trades.tail(10)
        for idx, trade in recent_trades.iterrows():
            direction = "买入" if trade["direction"] == "BUY" else "卖出"
            status = "拒绝" if trade["rejected"] else "成交"
            click.echo(
                f"  [{trade['datetime']}] {direction} "
                f"数量={trade['size']:.0f} 价格={trade['price']:.2f} "
                f"盈亏={trade['pnl']:.2f} [{status}]"
            )
    else:
        click.echo("无交易记录")
