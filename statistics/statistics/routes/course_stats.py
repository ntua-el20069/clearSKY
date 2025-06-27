from statistics.statistics.models.models import CourseStatistics

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK

router = APIRouter()


@router.get(
    "/get_course_stats",
    response_description="Course statistics extracted successfully",
)  # type: ignore
async def get_course_stats(
    course_id: str, exam_year: int, exam_type: str
) -> JSONResponse:
    """
    Extract distribution plots for a specific exam period of a course
    returns both the course grades distributions as well as individual question grades distributions

    :param course_id: The course id
    :type course_id: str
    :param exam_year: The exam year
    :type exam_year: int
    :param exam_type: Winter, Spring or Retake(more can be used, depending on modeling)
    :type exam_type: str
    """
    try:
        grades_stats = CourseStatistics.objects(
            course_id=course_id,
            year=exam_year,
            exam_type=exam_type,
        ).first()

        if grades_stats is None:
            raise HTTPException(
                status_code=400,
                detail=f"Could not find any stats for course: {course_id}, year: {exam_year} and exam type: {exam_type}",
            )

        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "description": "Course statistics extracted successfully",
                "grades_dist": grades_stats.grades_dist,
                "question_grades_dist": grades_stats.question_grades_dist,
            },
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
