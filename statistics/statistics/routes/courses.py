from statistics.statistics.models.models import (
    Course,
    CourseModel,
    EnrollmentModel,
    Grades,
)

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/add_course", response_description="Course added successfully")  # type: ignore
async def add_course(course_data: CourseModel) -> JSONResponse:
    """
    Add a course to the database

    :param course_data: Passed information about the course
    :type course_data: BaseModel(see models.py)
    """
    if len(course_data.current_registered_students) != len(
        set(course_data.current_registered_students)
    ):
        raise HTTPException(status_code=422, detail="Found duplicate student id's")
    if len(course_data.instructors) != len(set(course_data.instructors)):
        raise HTTPException(status_code=422, detail="Found duplicate instructor id's")

    try:
        new_course = Course(
            course_id=course_data.course_id,
            institution=course_data.institution,
            instructors=course_data.instructors,
            name=course_data.name,
            semester=course_data.semester,
            ects=course_data.ects,
            current_registered_students=sorted(course_data.current_registered_students),
            grades=[],
            finalized=course_data.finalized,
        )

        grades = []
        for student_id in course_data.current_registered_students:
            grade_docs = list(
                Grades.objects(student_id=student_id, course_id=course_data.course_id)
            )
            grades.extend(grade_docs)

        new_course.grades = grades
        new_course.save()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"description": "Course added successfully"},
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/enroll_students", response_description="Course updated successfully")  # type: ignore
async def enroll_students(enroll: EnrollmentModel) -> JSONResponse:

    try:
        if len(enroll.current_registered_students) == 0:
            raise HTTPException(
                status_code=400, detail="Enrolled students list is empty"
            )

        course = Course.objects(course_id=enroll.course_id).first()
        course.current_registered_students = enroll.current_registered_students

        course.save()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"description": "Course updated successfully"},
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/delete_course/{course_id}", response_description="Course deleted successfully"
)  # type: ignore
async def delete_course(course_id: str) -> JSONResponse:
    """
    Deletes a course from the database

    :param course_id: The id of the course to be deleted
    :type course_id: str
    """
    try:
        course = Course.objects(course_id=course_id).delete()

        if course:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"description": "Course deleted successfully"},
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"description": "Passed course not found"},
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/finalize_course/course_id={course_id}&exam_type={exam_type}&exam_year={exam_year}",
    response_description="Course finalized successfully",
)  # type: ignore
async def finalize_course(
    course_id: str, exam_type: str, exam_year: int
) -> JSONResponse:
    """
    Finalizes a course
    """
    try:
        course = Course.objects(course_id=course_id).first()

        if course is None:
            raise HTTPException(
                status_code=400, detail=f"Can't find course: {course_id}"
            )

        course.finalized[f"{exam_type}-{exam_year}"] = True
        course.save()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"description": "Course finalized successfully"},
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/initialize_course_grades/course_id={course_id}&exam_type={exam_type}&exam_year={exam_year}",
)  # type: ignore
async def initialize_course_grades(
    course_id: str, exam_type: str, exam_year: int
) -> JSONResponse:
    """
    Initializes the course grades for the given (course_id, exam_type, exam_year) tuple.
    This means that the course is not finalized yet, but initial grades exist.
    """
    try:
        course = Course.objects(course_id=course_id).first()

        if course is None:
            raise HTTPException(
                status_code=400, detail=f"Can't find course: {course_id}"
            )

        course.finalized[f"{exam_type}-{exam_year}"] = False
        course.save()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"description": "Course grades initialized successfully"},
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/status_of_grades/course_id={course_id}&exam_type={exam_type}&exam_year={exam_year}",
    response_description="Course finalized successfully",
)  # type: ignore
async def get_status_of_grades(
    course_id: str, exam_type: str, exam_year: int
) -> JSONResponse:
    """
    Returns "UNKNOWN" if there are no existing grades in the DB for the (course_id, exam_type, exam_year) tuple,
            "INITIAL" if grades exist but the (course_id, exam_type, exam_year) is not finalized (initial grades exist),
    and     "FINAL" if (course_id, exam_type, exam_year) finalized (final grades exist).
    """
    try:
        course = Course.objects(course_id=course_id).first()

        if course is None:
            raise HTTPException(
                status_code=400, detail=f"Can't find course: {course_id}"
            )

        if f"{exam_type}-{exam_year}" not in course.finalized:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"grades_status": "UNKNOWN"},
            )

        if course.finalized[f"{exam_type}-{exam_year}"]:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"grades_status": "FINAL"},
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"grades_status": "INITIAL"},
            )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
