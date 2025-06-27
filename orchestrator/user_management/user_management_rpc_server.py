import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from base_rpc import RpcClient


class UserManagementRpcClient(RpcClient):
    queue_name = "user_management_queue"


user_management_rpc_server = UserManagementRpcClient()
