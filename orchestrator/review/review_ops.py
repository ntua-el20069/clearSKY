import json

from fastapi.responses import JSONResponse

from .review_rpc_server import review_rpc_client

BASE_URL = "http://127.0.0.1:8005"


def RPC_RESPONSE(load: dict) -> JSONResponse:
    response_data, _ = review_rpc_client.call(load)
    print(" [x] Received response")

    response = json.loads(response_data)
    return JSONResponse(
        content=response["content"],
        status_code=response["status_code"],
    )


async def submit_review(review: dict) -> JSONResponse:
    print(" [x] Submitting review")

    load = {
        "method": "POST",
        "endpoint": f"{BASE_URL}/review/submit_review",
        "json": review,
    }

    return RPC_RESPONSE(load)


async def get_reviews(query: dict) -> JSONResponse:

    print(" [x] Fetching reviews")

    load = {
        "method": "GET",
        "endpoint": f"{BASE_URL}/review/get_reviews",
        "params": query,
    }

    return RPC_RESPONSE(load)


async def reply_to_review(reply: dict) -> JSONResponse:
    print(" [x] Replying to review")

    load = {
        "method": "PUT",
        "endpoint": f"{BASE_URL}/review/reply",
        "json": reply,
    }

    return RPC_RESPONSE(load)
