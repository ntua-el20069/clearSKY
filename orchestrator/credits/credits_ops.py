import json

from fastapi.responses import JSONResponse

from .credits_rpc_server import credits_rpc_client

BASE_URL = "http://127.0.0.1:8002"


def RPC_RESPONSE(load: dict) -> JSONResponse:
    response_data, _ = credits_rpc_client.call(load)
    print(" [x] Received response")

    response = json.loads(response_data)
    return JSONResponse(
        content=response["content"],
        status_code=response["status_code"],
    )


async def add_credits(credits: dict) -> JSONResponse:
    print(" [x] Adding credits")

    load = {
        "method": "POST",
        "endpoint": f"{BASE_URL}/credits/add_credits",
        "json": credits,
    }

    return RPC_RESPONSE(load)


async def remove_credits(credits: dict) -> JSONResponse:
    print(" [x] Removing credits")

    load = {
        "method": "PUT",
        "endpoint": f"{BASE_URL}/credits/remove_credits",
        "json": credits,
    }

    return RPC_RESPONSE(load)


async def get_credits(institution: str) -> JSONResponse:

    print(" [x] Fetching credits")

    load = {
        "method": "GET",
        "endpoint": f"{BASE_URL}/credits/get_credits?institution={institution}",
    }

    return RPC_RESPONSE(load)
