"""演示：RealtimeDataFeed + RealtimeStrategy 实时行情轮询。

通达信协议没有服务端推送，只有请求/响应。本示例用 RealtimeDataFeed 轮询
``get_stock_quotes`` 的五档快照，封装成 MarketEvent 喂给 EventBus，驱动
RealtimeStrategy 的 on_tick 回调。

注意事项：
  - 「实时」是轮询快照近似（默认约 3 秒延迟），不是逐笔 tick。
  - 订阅 key 必须与 publish 内部拼的 f"{market}{code}" 一致，即 "SZ000001"。
  - 传给 subscribe 的必须是实例的绑定方法 strategy.on_tick。
  - 默认仅在 A 股交易时段（9:15-11:30 / 13:00-15:00）轮询；演示用 sessions=()
    全天轮询。

使用客户端：AsyncMacClient（异步）
关键参数：
  - symbols: [(Market.SZ, code), ...]，单批最多 80 只（协议上限）
  - interval: 轮询间隔（秒），默认 3.0
  - dedup: (price, volume) 未变的标的跳过发布，默认 True
"""

import asyncio

from easy_tdx import Market
from easy_tdx.mac.client import AsyncMacClient
from easy_tdx.realtime import EventBus, MarketEvent, RealtimeDataFeed, RealtimeStrategy


class MyStrategy(RealtimeStrategy):
    """示例策略：价格超过阈值时打印提醒。"""

    def __init__(self, threshold: float = 10.0) -> None:
        super().__init__()
        self.threshold = threshold

    def on_tick(self, event: MarketEvent) -> None:
        flag = " ⚡ 超阈值!" if event.price > self.threshold else ""
        print(
            f"{event.market}{event.code} price={event.price:.2f} "
            f"vol={int(event.volume)} name={event.data.get('name', '')}{flag}"
        )


async def main() -> None:
    bus = EventBus()
    strategy = MyStrategy(threshold=10.5)
    # 注意：key 带市场前缀，且传实例绑定方法
    bus.subscribe("SZ000001", strategy.on_tick)
    bus.subscribe("SH600519", strategy.on_tick)

    feed = RealtimeDataFeed(
        bus=bus,
        symbols=[(Market.SZ, "000001"), (Market.SH, "600519")],
        interval=3.0,
        dedup=True,
        sessions=(),  # 演示用，全天轮询；实盘删掉此行用默认交易时段
    )

    print("开始轮询（Ctrl+C 退出）...")
    async with AsyncMacClient.from_best_host() as client:
        await feed.run_async(client)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n已停止")

# 运行结果（示例）:
# 开始轮询（Ctrl+C 退出）...
# SZ000001 price=10.52 vol=102345 name=平安银行 ⚡ 超阈值!
# SH600519 price=1798.00 vol=5234 name=贵州茅台
# SZ000001 price=10.53 vol=102580 name=平安银行 ⚡ 超阈值!
