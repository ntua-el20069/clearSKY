import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from base_rpc import RpcClient


class XlsxParsingRpcClient(RpcClient):
    queue_name = "xlsx_parsing_queue"


xlsx_parsing_rpc_client = XlsxParsingRpcClient()
