import json

from fastapi.responses import JSONResponse

from .user_management_rpc_server import user_management_rpc_server

BASE_URL = "http://127.0.0.1:8001"


def RPC_RESPONSE(load: dict) -> JSONResponse:
    response_data, _ = user_management_rpc_server.call(load)
    print(" [x] Received response")

    response = json.loads(response_data)
    return JSONResponse(
        content=response["content"],
        status_code=response["status_code"],
    )


async def register_instructor(instructor: dict) -> JSONResponse:
    print(" [x] Registering an instructor")

    load = {
        "method": "POST",
        "endpoint": f"{BASE_URL}/register/register_instructor",
        "json": instructor,
    }

    return RPC_RESPONSE(load)


async def remove_instructor(instructor: dict) -> JSONResponse:
    print(" [x] Removing an instructor")

    load = {
        "method": "DELETE",
        "endpoint": f"{BASE_URL}/register/remove_instructor",
        "json": instructor,
    }

    return RPC_RESPONSE(load)


async def update_instructor(updated_instructor: dict) -> JSONResponse:
    print(" [x] Updating an instructor")

    load = {
        "method": "PUT",
        "endpoint": f"{BASE_URL}/register/update_instructor",
        "params": updated_instructor,
    }

    return RPC_RESPONSE(load)


async def register_student(student: dict) -> JSONResponse:
    print(" [x] Registering a student")

    load = {
        "method": "POST",
        "endpoint": f"{BASE_URL}/register/register_student",
        "json": student,
    }

    return RPC_RESPONSE(load)


async def remove_student(removed_student: dict) -> JSONResponse:
    print(" [x] Removing a student")

    load = {
        "method": "DELETE",
        "endpoint": f"{BASE_URL}/register/remove_student",
        "json": removed_student,
    }

    return RPC_RESPONSE(load)


async def update_student(updated_student: dict) -> JSONResponse:
    print(" [x] Updating a student")

    load = {
        "method": "PUT",
        "endpoint": f"{BASE_URL}/register/update_student",
        "params": updated_student,
    }

    return RPC_RESPONSE(load)


async def login(credentials: dict) -> JSONResponse:
    print(" [x] Logging in")

    load = {
        "method": "POST",
        "endpoint": f"{BASE_URL}/login/login",
        "json": credentials,
    }

    return RPC_RESPONSE(load)


async def logout(token: str) -> JSONResponse:
    print(" [x] Logging out")

    load = {
        "method": "POST",
        "endpoint": f"{BASE_URL}/login/logout",
        "headers": {"Authorization": f"Bearer {token}"},
    }

    return RPC_RESPONSE(load)


async def check_access(token: str) -> JSONResponse:
    print(" [x] Checking logged in user privileges")

    load = {
        "method": "POST",
        "endpoint": f"{BASE_URL}/login/check_access?token={token}",
    }

    return RPC_RESPONSE(load)


async def fetch_instructors(institution: str) -> JSONResponse:
    print(" [x] Fetching instructors")

    load = {
        "method": "GET",
        "endpoint": f"{BASE_URL}/register/fetch_instructors/{institution}",
    }

    return RPC_RESPONSE(load)
