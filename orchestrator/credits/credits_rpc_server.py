import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from base_rpc import RpcClient


class CreditsRpcClient(RpcClient):
    queue_name = "credits_queue"


credits_rpc_client = CreditsRpcClient()
