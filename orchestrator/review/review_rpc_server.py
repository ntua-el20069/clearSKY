import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from base_rpc import RpcClient


class ReviewRpcClient(RpcClient):
    queue_name = "review_queue"


review_rpc_client = ReviewRpcClient()
