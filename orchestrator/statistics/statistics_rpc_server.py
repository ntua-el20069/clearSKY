import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from base_rpc import RpcClient


class StatisticsRpcClient(RpcClient):
    queue_name = "statistics_queue"


statistics_rpc_client = StatisticsRpcClient()
