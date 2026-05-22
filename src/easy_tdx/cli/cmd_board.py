"""板块命令：board-list, board-members, belong-board。"""

from __future__ import annotations

import click


@click.command("board-list")
@click.option("--type", "board_type", default="ALL", help="板块类型: ALL/HY/GN/FG/DQ/OTHER")
@click.option("--count", default=10000, type=int, help="请求数量")
@click.option("--table", "use_table", is_flag=True, help="表格输出")
@click.option("--output", "output_fmt", type=click.Choice(["json", "table", "csv"]), default="json")
def board_list(
    board_type: str,
    count: int,
    use_table: bool,
    output_fmt: str,
) -> None:
    """获取板块列表。

    示例：

      easy-tdx board-list --table

      easy-tdx board-list --type GN --count 200

      easy-tdx board-list --type HY
    """
    from .conn import get_mac_client
    from .output import print_output
    from .parsers import parse_board_type

    fmt = "table" if use_table else output_fmt
    bt = parse_board_type(board_type)
    with get_mac_client() as client:
        df = client.get_board_list(board_type=bt, count=count)
    print_output(df, fmt)


@click.command("board-members")
@click.argument("board_symbol")
@click.option("--count", default=100000, type=int, help="请求数量")
@click.option(
    "--sort", "sort_field", default="CHANGE_PCT", help="排序字段: CHANGE_PCT/CODE/PRICE/VOLUME"
)
@click.option("--order", "sort_order", default="DESC", help="排序方向: DESC/ASC")
@click.option("--table", "use_table", is_flag=True, help="表格输出")
@click.option("--output", "output_fmt", type=click.Choice(["json", "table", "csv"]), default="json")
def board_members(
    board_symbol: str,
    count: int,
    sort_field: str,
    sort_order: str,
    use_table: bool,
    output_fmt: str,
) -> None:
    """获取板块成分股报价。

    BOARD_SYMBOL: 板块代码（如 881001）

    示例：

      easy-tdx board-members 881001 --table

      easy-tdx board-members 881001 --sort VOLUME --count 20
    """
    from .conn import get_mac_client
    from .output import print_output
    from .parsers import parse_sort_order, parse_sort_type

    fmt = "table" if use_table else output_fmt
    st = parse_sort_type(sort_field)
    so = parse_sort_order(sort_order)
    with get_mac_client() as client:
        df = client.get_board_members(
            board_symbol,
            count=count,
            sort_type=st,
            sort_order=so,
        )
    print_output(df, fmt)


@click.command("belong-board")
@click.argument("market")
@click.argument("code")
@click.option("--table", "use_table", is_flag=True, help="表格输出")
@click.option("--output", "output_fmt", type=click.Choice(["json", "table", "csv"]), default="json")
def belong_board(market: str, code: str, use_table: bool, output_fmt: str) -> None:
    """获取个股所属板块列表。

    示例：

      easy-tdx belong-board SZ 000001

      easy-tdx belong-board SH 600519 --table
    """
    from .conn import get_mac_client
    from .output import print_output
    from .parsers import parse_market

    fmt = "table" if use_table else output_fmt
    mkt = parse_market(market)
    with get_mac_client() as client:
        df = client.get_belong_board(mkt, code)
    print_output(df, fmt)
