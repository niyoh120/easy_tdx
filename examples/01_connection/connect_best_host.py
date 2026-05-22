"""演示：TdxClient 三种连接方式 -- 默认配置 / 自动优选 / 手动指定。

TdxClient 是 easy_tdx 的同步行情客户端，通过 TCP 长连接访问通达信行情服务器。

1. 使用默认配置（推荐日常使用）：
   TdxClient() -- 从 ~/.easy_tdx/config.json 读取 best_host。
   首次使用前先运行一次 from_best_host() 建立配置即可。

2. 自动优选（首次或需要刷新时）：
   TdxClient.from_best_host() -- 并发 ping 所有候选服务器，
   选择延迟最低的一台，并自动保存到 config.json。
   后续 TdxClient() 将直接使用保存的最佳地址。

3. 手动指定服务器：
   TdxClient(host) -- 直接连接指定 IP。

所有方式均支持 with 上下文管理器，退出时自动关闭连接和心跳线程。
"""

from easy_tdx import Market, TdxClient

# 方式一：使用 config.json 中的 best_host（推荐日常使用）
# 首次需要先运行一次 from_best_host() 生成配置。
with TdxClient() as c:
    print(f"[默认] 已连接到 {c._host}:{c._port}")
    count = c.get_security_count(Market.SH)
    print(f"沪市证券总数: {count}")

# 方式二：自动优选最低延迟服务器并保存到 config.json
# from_best_host() 内部流程：
#   1. 对候选列表中所有 IP 并发 TCP ping
#   2. 按延迟从低到高排序
#   3. 取延迟最低的一台创建 TdxClient 实例
#   4. 自动保存最佳地址到 ~/.easy_tdx/config.json
with TdxClient.from_best_host() as c:
    print(f"[优选] 已自动选择最优服务器: {c._host}:{c._port}")
    count = c.get_security_count(Market.SH)
    print(f"沪市证券总数: {count}")
