import importlib
import json
import os
import tempfile
from typing import Any, Dict

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

# Differentiate between running in Docker and locally
base_path = "/app/" if os.getcwd() == "/app" else ""

# try to import independently of the dir from which the script is run
# the app.py can be run from directories:
# saas25-20, saas25-20/xlsx_parsing, saas25-20/xlsx_parsing/xlsx_parsing

try:
    parse_module = importlib.import_module(".parse", package=__package__)
except ImportError:
    try:
        parse_module = importlib.import_module("xlsx_parsing.parse")
    except ImportError:
        parse_module = importlib.import_module("xlsx_parsing.xlsx_parsing.parse")

parse_grades_excel = parse_module.parse_grades_excel
parse_enrolled_students_excel = parse_module.parse_enrolled_students_excel

for example_base_path in (
    base_path + x for x in ["", "xlsx_parsing/", "xlsx_parsing/xlsx_parsing/"]
):
    try:
        with open(example_base_path + "example-response.json", "r") as f:
            example_response = json.load(f)
    except:
        pass

app = FastAPI()


@app.post(
    "/xlsx_parsing/parse_grades",
    response_description="Grades parsed successfully",
    responses={
        200: {
            "description": "Grades parsed successfully",
            "model": Dict[str, Any],
            "content": {
                "application/json": {"example": example_response},
            },
        },
        400: {
            "description": "Invalid data in Excel file",
            "model": Dict[str, Any],
            "content": {
                "application/json": {
                    "example": {"error": "Mandatory header in column 4 is missing"}
                }
            },
        },
        415: {
            "description": "Unsupported media type",
            "model": Dict[str, Any],
            "content": {
                "application/json": {
                    "example": {"error": "Only Excel files (.xlsx) are allowed"}
                }
            },
        },
        500: {
            "description": "Internal server error",
            "model": Dict[str, Any],
            "content": {
                "application/json": {
                    "example": {
                        "error": "Internal Server Error - Unexpected Error processing file: <error message>"
                    }
                }
            },
        },
    },
)  # type: ignore
async def parse_grades(file: UploadFile = File(...)) -> JSONResponse:
    # Check file extension
    if not file.filename.lower().endswith((".xlsx")):
        raise HTTPException(
            status_code=415, detail={"error": "Only Excel files (.xlsx) are allowed"}
        )

    # Create a temporary file
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)

    try:
        # Save the uploaded file temporarily
        with open(temp_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)

        # Process the file
        res: Dict[str, Any] = parse_grades_excel(temp_path)

        if res["error"]:
            # Return 400 for validation errors
            return JSONResponse(status_code=400, content=res)
        return JSONResponse(content=res)

    except HTTPException:
        # Re-raise HTTPExceptions (like the 415 above)
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": f"Unexpected Error processing file: {str(e)}"},
        )

    finally:
        # Clean up - delete the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post(
    "/xlsx_parsing/parse_enrolled_students",
    response_description="Enrolled students parsed successfully",
    responses={
        200: {
            "description": "Enrolled students parsed successfully",
            "model": Dict[str, Any],
            "content": {
                "application/json": {
                    "example": {
                        "error": "",
                        "warning": "",
                        "result": {
                            "format": "enrolled",
                            "course_id": "3205",
                            "exam_type": "Winter",
                            "year": 2024,
                            "student_ids": [
                                "03184623",
                                "03184610",
                            ],
                        },
                    }
                },
            },
        },
    },
)  # type: ignore
async def parse_enrolled_students(file: UploadFile = File(...)) -> JSONResponse:
    # Check file extension
    if not file.filename.lower().endswith((".xlsx")):
        raise HTTPException(
            status_code=415, detail={"error": "Only Excel files (.xlsx) are allowed"}
        )

    # Create a temporary file
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)

    try:
        # Save the uploaded file temporarily
        with open(temp_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)

        # Process the file
        res: Dict[str, Any] = parse_enrolled_students_excel(temp_path)

        if res["error"]:
            # Return 400 for validation errors
            return JSONResponse(status_code=400, content=res)
        return JSONResponse(content=res)

    except HTTPException:
        # Re-raise HTTPExceptions (like the 415 above)
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": f"Unexpected Error processing file: {str(e)}"},
        )

    finally:
        # Clean up - delete the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
