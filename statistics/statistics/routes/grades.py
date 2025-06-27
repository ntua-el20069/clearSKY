from statistics.statistics.models.models import (
    Course,
    CourseStatistics,
    Grades,
    GradesModel,
    GradesModelOps,
)
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK

router = APIRouter()


@router.post("/add_grades", response_description="Grades added successfully")  # type: ignore
async def add_grades(passed_grades: list[GradesModel]) -> JSONResponse:
    """
    Add grades to the database - INITIAL POST GRADES
    Used for initial post grades for (student, course, exam type, year) combinations.
    computes course statistics and saves them.
    at the end of a successful call to this endpoint,
    the course.finalized field will be set to False for the given exam type and year,
    so that the status_of_grades will be set to INITIAL for the course

    :param passed_grades: A list of grades
    :type passed_grades: List[BaseModel](see models.py)
    """

    try:
        grades_dist: dict = {}
        question_grades_dist: list[dict] = [
            {} for i in range(len(passed_grades[0].question_grades))
        ]

        # check the course exists and is not finalized for the given exam type and year
        check_course = Course.objects(course_id=passed_grades[0].course_id).first()
        if check_course is None:
            raise HTTPException(
                status_code=400,
                detail=f"Course: {passed_grades[0].course_id} doesn't exist. Make sure your representative add the course first.",
            )
        if (
            f"{passed_grades[0].exam_type}-{passed_grades[0].year}"
            in check_course.finalized
        ):
            if check_course.finalized[
                f"{passed_grades[0].exam_type}-{passed_grades[0].year}"
            ]:  # check_course.finalized[{examp_type}-{year}] == True
                # this means that the course has been finalized for the given exam type and year
                # final grades have been posted
                # and we should neither add / post them again, nor update them
                raise HTTPException(
                    status_code=400,
                    detail=f"Final grades already posted for course: {passed_grades[0].course_id}, exam type: {passed_grades[0].exam_type} and year: {passed_grades[0].year}. You cannot add grades anymore.",
                )
            else:  # check_course.finalized[{examp_type}-{year}] == False
                # this means that the initial grades have been posted
                # and we should not post them again, but update them instead
                raise HTTPException(
                    status_code=400,
                    detail=f"Initial grades already posted for: {passed_grades[0].course_id}, exam type: {passed_grades[0].exam_type} and year: {passed_grades[0].year}. You should use the update_grades endpoint.",
                )

        for grade in passed_grades:

            if grade.student_id not in check_course.current_registered_students:
                raise HTTPException(
                    status_code=400,
                    detail=f"Student {grade.student_id} doesn't exist in this course",
                )

            if (
                len(
                    Grades.objects(
                        student_id=grade.student_id,
                        course_id=grade.course_id,
                        exam_type=grade.exam_type,
                        year=grade.year,
                    )
                )
                > 0
            ):
                raise HTTPException(
                    status_code=400,
                    detail=f"Tried to post already existing grades: [{grade.student_id}, {grade.course_id}, {grade.exam_type}, {grade.year}]",
                )

            new_grade = Grades(
                student_id=grade.student_id,
                name=grade.name,
                course_id=grade.course_id,
                exam_type=grade.exam_type,
                year=grade.year,
                grade=grade.grade,
                question_grades=grade.question_grades,
                grade_weights=grade.grade_weights,
            )
            new_grade.save()

            check_course.grades.append(new_grade)
            check_course.save()

            # compute course statistics
            if str(grade.grade) not in grades_dist:
                grades_dist[str(grade.grade)] = 1
            else:
                grades_dist[str(grade.grade)] += 1

            for q, question_grade in enumerate(grade.question_grades):
                if str(question_grade) not in question_grades_dist[q]:
                    question_grades_dist[q][str(question_grade)] = 1
                else:
                    question_grades_dist[q][str(question_grade)] += 1

        # save the course statistics
        course_stats = CourseStatistics(
            course_id=passed_grades[0].course_id,
            exam_type=passed_grades[0].exam_type,
            year=passed_grades[0].year,
            grades_dist=grades_dist,
            question_grades_dist=question_grades_dist,
        )
        course_stats.save()

        # mark the course as not finalized for the given exam type and year (INITIAL POST GRADES)
        check_course.finalized[
            f"{passed_grades[0].exam_type}-{passed_grades[0].year}"
        ] = False
        check_course.save()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"description": "Grades added successfully"},
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get_student_grades", response_description="Grades extracted successfully")  # type: ignore
async def get_student_grades(
    student_ids: list[str] = Query(...),
    years: Optional[list[int]] = Query(None),
    exam_types: Optional[list[str]] = Query(None),
) -> JSONResponse:
    """
    Returns a list of grade statistics for the passed Students information

     :param student_ids: A list of student id's
     :type student_ids: list[str]
     :param years: A list of years
     :type years: Optional[list[int]]
     :param exam_types: A list of exam types(like "Winter", "Summer", "Re-take", depends on your use case)
     :type exam_types: Optional[list[str]]
    """
    if len(student_ids) != len(set(student_ids)):
        raise HTTPException(status_code=422, detail="Found duplicate student id's")
    if years and len(years) != len(set(years)):
        raise HTTPException(status_code=422, detail="Found duplicate years")
    if exam_types and len(exam_types) != len(set(exam_types)):
        raise HTTPException(status_code=422, detail="Found duplicate exam types")

    try:
        returned_grades = []
        for student in student_ids:
            grade_query = {"student_id": student}
            if exam_types:
                grade_query["exam_type__in"] = exam_types  # type: ignore
            if years:
                grade_query["year__in"] = years  # type: ignore

            for grade in Grades.objects(**grade_query).order_by("student_id"):
                returned_grades.append(
                    GradesModel(
                        student_id=grade.student_id,
                        name=grade.name,
                        course_id=grade.course_id,
                        exam_type=grade.exam_type,
                        year=grade.year,
                        grade=grade.grade,
                        question_grades=grade.question_grades,
                        grade_weights=grade.grade_weights,
                    ).dict()
                )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "description": "Grades extracted successfully",
                "grades": returned_grades,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get_course_grades", response_description="Grades extracted successfully")  # type: ignore
async def get_course_grades(
    course_ids: list[str] = Query(...),
    instructors: Optional[list[str]] = Query(None),
    semester: Optional[list[int]] = Query(None),
) -> JSONResponse:
    """
    Returns a list of grade statistics for the passed courses information

    :param course_ids: A list of course id's
    :type course_ids: list[str]
    :param instructors: A list of instructor id's
    :type instructors: Optional[list[str]]
    :param semester: A list of semesters
    :type semester: Optional[list[int]]
    """
    try:
        returned_grades = []
        for course in course_ids:
            grade_query = {"course_id": course}
            if instructors:
                grade_query["instructors__in"] = instructors  # type: ignore

            if semester:
                grade_query["semester__in"] = semester  # type: ignore
            for course in Course.objects(**grade_query).order_by("course_id"):
                for grade in course.grades:  # type: ignore
                    returned_grades.append(
                        GradesModel(
                            student_id=grade.student_id,
                            name=grade.name,
                            course_id=grade.course_id,
                            exam_type=grade.exam_type,
                            year=grade.year,
                            grade=grade.grade,
                            question_grades=grade.question_grades,
                            grade_weights=grade.grade_weights,
                        ).dict()
                    )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "description": "Grades extracted successfully",
                "grades": returned_grades,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/update_grades", response_description="Grades updated successfully")  # type: ignore
async def update_grades(updated_grades: list[GradesModel]) -> JSONResponse:
    """
    Updates the passed students grades - used for FINAL POST GRADES.

    :param updated_grades: A list of the grades to be updated. This endpoint searches for the same student's grades
    for the same course and exam_type and year combination, and if it finds a match, it updates it with the passed grade
    :type updated_grades: BaseModel(see models.py)
    """
    # CAUTION:
    # this will not update properly the grades if the student ids in the grades saved before
    # are not the same as the ones in the passed updated_grades.
    # e.g. When saved grades refet to student_id's : # ["123", "456"]
    # and the passed updated_grades refer to student_id's: ["123", "789"]
    # then the grade for student_id "123" will be updated,
    # then the grade for student_id "456" will not be updated and will remain the same.
    # (I suppose we want to delete the grade for student_id "456")
    # and the new value for student_id "789" will not be added
    # (possible TODO): if we want to be absolutely compatible with FINAL POST GRADES,
    # we should  delete the saved grades and insert the new ones
    # or just delete the ones that are not in the passed updated_grades and update the others / insert.

    try:
        course_stats = CourseStatistics.objects(
            course_id=updated_grades[0].course_id,
            year=updated_grades[0].year,
            exam_type=updated_grades[0].exam_type,
        ).first()

        if course_stats is None:
            raise HTTPException(
                status_code=400,
                detail=f"There are not any grades for course: {updated_grades[0].course_id}, year: {updated_grades[0].year} and exam_type: {updated_grades[0].exam_type}",
            )
        grades_dist = course_stats.grades_dist
        question_grades_dist = course_stats.question_grades_dist

        # check the course exists and is not finalized for the given exam type and year
        check_course = Course.objects(course_id=updated_grades[0].course_id).first()
        if check_course is None:
            raise HTTPException(
                status_code=400,
                detail=f"Course: {updated_grades[0].course_id} doesn't exist. Make sure your representative add the course first.",
            )

        # you can make a call to this endpoint after INITIAL POST GRADES
        # and you can update the grades as many times as you want
        # frontend should not allow this endpoint to be called after FINAL POST GRADES

        total_updated_grades = 0
        for grade in updated_grades:
            curr_grade_obj = Grades.objects(
                student_id=grade.student_id,
                course_id=grade.course_id,
                exam_type=grade.exam_type,
                year=grade.year,
            ).first()

            if curr_grade_obj:
                # change grades
                grades_dist[str(curr_grade_obj.grade)] -= 1
                if grades_dist[str(curr_grade_obj.grade)] == 0:
                    del grades_dist[str(curr_grade_obj.grade)]

                curr_grade_obj.grade = grade.grade

                if str(grade.grade) not in grades_dist:
                    grades_dist[str(grade.grade)] = 1
                else:
                    grades_dist[str(grade.grade)] += 1

                # change question grades
                for q, question_grade in enumerate(curr_grade_obj.question_grades):
                    question_grades_dist[q][str(question_grade)] -= 1
                    if question_grades_dist[q][str(question_grade)] == 0:
                        del question_grades_dist[q][str(question_grade)]

                curr_grade_obj.question_grades = grade.question_grades

                for q, question_grade in enumerate(grade.question_grades):
                    if str(question_grade) not in question_grades_dist[q]:
                        question_grades_dist[q][str(question_grade)] = 1
                    else:
                        question_grades_dist[q][str(question_grade)] += 1

                curr_grade_obj.save()
                total_updated_grades += 1

        course_stats.update(
            grades_dist=grades_dist, question_grades_dist=question_grades_dist
        )

        check_course.finalized[
            f"{updated_grades[0].exam_type}-{updated_grades[0].year}"
        ] = True  # mark the course as finalized for the given exam type and year
        check_course.save()

        return JSONResponse(
            status_code=HTTP_200_OK,
            content={
                "description": f"Updated {total_updated_grades} grades. Failed to update {len(updated_grades) - total_updated_grades}"
            },
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete_grades", response_description="Grades deleted successfully")  # type: ignore
async def delete_grades(to_delete_grades: list[GradesModelOps]) -> JSONResponse:
    try:
        total_deleted_grades = 0
        for grade in to_delete_grades:
            curr_grade_obj = Grades.objects(
                student_id=grade.student_id,
                course_id=grade.course_id,
                exam_type=grade.exam_type,
                year=grade.year,
            ).first()

            if curr_grade_obj:
                curr_grade_obj.delete()
                total_deleted_grades += 1

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "description": f"Deleted {total_deleted_grades} grades. Failed to delete {len(to_delete_grades) - total_deleted_grades}"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
