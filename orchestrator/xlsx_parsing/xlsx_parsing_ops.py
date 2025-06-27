import base64
import json
import os
import sys
from typing import Any, Dict

from fastapi.responses import JSONResponse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from .xlsx_rpc_server import xlsx_parsing_rpc_client

BASE_URL = "http://127.0.0.1:8003"


def encode_file(file: Any) -> dict:
    content = file.read()
    return {
        "filename": file.name,
        "content": base64.b64encode(content).decode(),
        "content_type": file.type,
    }


def decode_file(body: Any) -> dict:
    file_info = json.loads(body)
    filename = file_info["json"]["filename"]
    content_type = file_info["json"]["content_type"]
    content_bytes = base64.b64decode(file_info["json"]["content"])

    files = {"file": (filename, content_bytes, content_type)}
    return files


async def parse_grades(file: Any) -> JSONResponse:
    encoded_file: Dict[str, str] = encode_file(file)
    print(f" [x] Sending file: {encoded_file['filename']}")
    load = {
        "method": "POST",
        "endpoint": f"{BASE_URL}/xlsx_parsing/parse_grades",
        "json": encoded_file,
    }

    response_data, _ = xlsx_parsing_rpc_client.call(load)
    print(" [x] Received response")

    # Decode the JSON string received from worker
    response = json.loads(response_data)

    return JSONResponse(
        content=response["content"],
        status_code=response["status_code"],
    )


async def parse_enrolled_students(file: Any) -> JSONResponse:
    encoded_file: Dict[str, str] = encode_file(file)
    print(f" [x] Sending file: {encoded_file['filename']}")

    load = {
        "method": "POST",
        "endpoint": f"{BASE_URL}/xlsx_parsing/parse_enrolled_students",
        "json": encoded_file,
    }

    response_data, _ = xlsx_parsing_rpc_client.call(load)
    print("[x] Received response")

    response = json.loads(response_data)

    return JSONResponse(
        content=response["content"],
        status_code=response["status_code"],
    )
