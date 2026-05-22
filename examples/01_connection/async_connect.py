"""演示：AsyncTdxClient 异步客户端连接与基本用法。

AsyncTdxClient 是 TdxClient 的异步版本，接口一一对应：
  - get_security_count(market) -> int
  - get_security_list(market, start) -> pd.DataFrame
  - get_security_bars(market, code, category, start, count) -> pd.DataFrame
  - get_security_quotes(stocks) -> pd.DataFrame
  - ...

所有方法均为 async，需在 asyncio 事件循环中运行。

注意事项：
  - 单个 AsyncTdxClient 仅维护一条 TCP 连接
  - 并发调用会在连接内串行执行（内部有 asyncio.Lock）
  - 支持 async with 上下文管理器，退出时自动关闭连接和心跳任务
  - 心跳间隔默认 60 秒（TdxClient 同步版默认 15 秒）

K 线返回 DataFrame 列说明（日线及以上周期）：
  date      : datetime64 -- 日期（日线/周线/月线/年线只有 date）
  open      : float64    -- 开盘价（元）
  close     : float64    -- 收盘价（元）
  high      : float64    -- 最高价（元）
  low       : float64    -- 最低价（元）
  vol       : float64    -- 成交量（股）
  amount    : float64    -- 成交额（元）

K 线返回 DataFrame 列说明（分钟线周期）：
  datetime  : datetime64 -- 日期时间（分钟线有完整 datetime）
  open      : float64    -- 开盘价（元）
  close     : float64    -- 收盘价（元）
  high      : float64    -- 最高价（元）
  low       : float64    -- 最低价（元）
  vol       : float64    -- 成交量（股）
  amount    : float64    -- 成交额（元）

使用客户端：AsyncTdxClient（异步）
关键参数：host (str), port (int, 默认7709), timeout (float, 默认15.0s)
"""

import asyncio

from easy_tdx import AsyncTdxClient, KlineCategory, Market


async def main():
    # 手动指定服务器
    async with AsyncTdxClient("180.153.18.170") as c:
        count = await c.get_security_count(Market.SH)
        print(f"沪市证券总数: {count}")

    # 自动优选服务器
    async with AsyncTdxClient.from_best_host() as c:
        # 获取浦发银行(600000)最近 5 条日 K 线
        df = await c.get_security_bars(Market.SH, "600000", KlineCategory.DAY, 0, 5)
        print(df.to_string(index=False))


asyncio.run(main())

# 运行结果:
# 沪市证券总数: 2847
#       date   open  close   high    low      vol       amount
# 2026-05-18  12.35  12.41  12.48  12.30  485236.0  599203456.0
# 2026-05-19  12.40  12.38  12.45  12.32  392184.0  485723200.0
# 2026-05-20  12.36  12.50  12.55  12.33  561087.0  699841536.0
# 2026-05-21  12.52  12.45  12.58  12.40  423891.0  529074688.0
# 2026-05-22  12.46  12.51  12.56  12.42  315670.0  394515840.0
