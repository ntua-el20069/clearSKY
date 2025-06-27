import json

from fastapi.responses import JSONResponse

from .statistics_rpc_server import statistics_rpc_client

BASE_URL = "http://127.0.0.1:8004"


def RPC_RESPONSE(load: dict) -> JSONResponse:
    response_data, _ = statistics_rpc_client.call(load)
    print(" [x] Received response")

    response = json.loads(response_data)
    return JSONResponse(
        content=response["content"],
        status_code=response["status_code"],
    )


async def add_grades(grades: list[dict]) -> JSONResponse:
    print(" [x] Sending grades for submission")

    load = {
        "method": "POST",
        "endpoint": f"{BASE_URL}/grades/add_grades",
        "json": grades,
    }

    return RPC_RESPONSE(load)


async def get_student_grades(students: dict) -> JSONResponse:
    print(" [x] Fetching student grades")

    load = {
        "method": "GET",
        "endpoint": f"{BASE_URL}/grades/get_student_grades",
        "params": students,
    }

    return RPC_RESPONSE(load)


async def update_grades(updated_grades: list[dict]) -> JSONResponse:
    print(" [x] updating student grades")

    load = {
        "method": "PUT",
        "endpoint": f"{BASE_URL}/grades/update_grades",
        "json": updated_grades,
    }

    return RPC_RESPONSE(load)


async def delete_grades(deleted_grades: list[dict]) -> JSONResponse:
    print(" [x] deleting student grades")

    load = {
        "method": "DELETE",
        "endpoint": f"{BASE_URL}/grades/delete_grades",
        "json": deleted_grades,
    }

    return RPC_RESPONSE(load)


async def add_course(course: dict) -> JSONResponse:
    print(" [x] adding course")

    load = {
        "method": "POST",
        "endpoint": f"{BASE_URL}/courses/add_course",
        "json": course,
    }

    return RPC_RESPONSE(load)


async def delete_course(course_id: str) -> JSONResponse:
    print(" [x] deleting course")

    load = {
        "method": "DELTE",
        "endpoint": f"{BASE_URL}/courses/delete_course/{course_id}",
    }

    return RPC_RESPONSE(load)


async def get_course_stats(
    course_id: str, exam_year: int, exam_type: str
) -> JSONResponse:
    print(" [x] fetching course statistics")

    load = {
        "method": "GET",
        "endpoint": f"{BASE_URL}/course_stats/get_course_stats?course_id={course_id}&exam_year={exam_year}&exam_type={exam_type}",
    }

    return RPC_RESPONSE(load)


async def enroll_students(
    course_id: str,
    enrolled_students: list,
) -> JSONResponse:

    load = {
        "method": "PUT",
        "endpoint": f"{BASE_URL}/courses/enroll_students",
        "json": {
            "course_id": course_id,
            "current_registered_students": enrolled_students,
        },
    }

    return RPC_RESPONSE(load)


async def finalize_course(
    course_id: str,
    exam_type: str,
    exam_year: int,
) -> JSONResponse:
    print("[x] finalizing course")

    load = {
        "method": "GET",
        "endpoint": f"{BASE_URL}/courses/finalize_course/course_id={course_id}&exam_type={exam_type}&exam_year={exam_year}",
    }

    return RPC_RESPONSE(load)


async def initialize_course_grades(
    course_id: str, exam_type: str, exam_year: int
) -> JSONResponse:
    print("[x] initializing course grades")

    load = {
        "method": "GET",
        "endpoint": f"{BASE_URL}/courses/initialize_course_grades/course_id={course_id}&exam_type={exam_type}&exam_year={exam_year}",
    }

    return RPC_RESPONSE(load)


# similat to the above, but just get the status_of_grades
async def get_status_of_grades(
    course_id: str, exam_type: str, exam_year: int
) -> JSONResponse:
    print("[x] fetching status of grades")

    load = {
        "method": "GET",
        "endpoint": f"{BASE_URL}/courses/status_of_grades/course_id={course_id}&exam_type={exam_type}&exam_year={exam_year}",
    }

    return RPC_RESPONSE(load)
