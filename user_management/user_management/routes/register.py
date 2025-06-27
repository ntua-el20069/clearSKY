from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from werkzeug.security import generate_password_hash

from user_management.user_management.models.models import (
    InstitutionRepresentative,
    InstitutionRepresentativeModel,
    Instructor,
    InstructorModel,
    Student,
    StudentModel,
    User,
)

router = APIRouter()


@router.post(
    "/register_representative",
    response_description="Institution Representative registered successfully",
)  # type: ignore
async def register_representative(
    representative: InstitutionRepresentativeModel,
) -> JSONResponse:
    """
    Register a new institution representative.
    :param representative: Institution representative info
    :type representative: BaseModel(see models.py)
    """

    try:
        representative_obj = InstitutionRepresentative.objects(
            representative_id=representative.representative_id
        ).first()
        user_obj = User.objects(username=representative.representative_id).first()
        if representative_obj or user_obj:
            raise HTTPException(
                status_code=405, detail="Institution representative already exists"
            )

        new_representative = InstitutionRepresentative(
            representative_id=representative.representative_id,
            name=representative.name,
            email=representative.email,
            institution=representative.institution,
        )
        new_representative.save()

        hashed_password = generate_password_hash(representative.password)
        new_user = User(
            username=representative.representative_id,
            password=hashed_password,
            email=representative.email,
            role="InstitutionRepresentative",
            institution=representative.institution,
        )
        new_user.save()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "description": "Institution representative registered successfully"
            },
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/register_instructor",
    response_description="Instructor registered successfully",
)  # type: ignore
async def register_instructor(instructor: InstructorModel) -> JSONResponse:
    """
    Register a new instructor.
    If the instructor already exists, an HTTPException will be raised.

    :param instructor: Instructor info
    :type instructor: BaseModel(see models.py)
    """
    try:
        instructor_obj = Instructor.objects(
            instructor_id=instructor.instructor_id
        ).first()
        user_obj = User.objects(username=instructor.instructor_id).first()
        if instructor_obj or user_obj:
            raise HTTPException(status_code=405, detail="Instructor already exists")

        new_instructor = Instructor(
            instructor_id=instructor.instructor_id,
            email=instructor.email,
            name=instructor.name,
            institution=instructor.institution,
            department=instructor.department,
            phone=instructor.phone,
            office=instructor.office,
        )
        new_instructor.save()

        hashed_password = generate_password_hash(instructor.password)
        new_user = User(
            username=instructor.instructor_id,
            password=hashed_password,
            email=instructor.email,
            role="Instructor",
            institution=instructor.institution,
        )
        new_user.save()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"description": "Instructor registered successfully"},
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fetch_instructors/{institution}")  # type: ignore
async def fetch_instructors(institution: str) -> JSONResponse:
    """
    Fetch instructors of an institution

    :param institution: The passed institution name
    :type institution: str
    """
    try:
        returned_instructors = []
        for instructor in Instructor.objects(institution=institution):
            returned_instructors.append(
                InstructorModel(
                    instructor_id=instructor.instructor_id,
                    email=instructor.email,
                    name=instructor.name,
                    institution=instructor.institution,
                    department=instructor.department,
                    phone=instructor.phone,
                    office=instructor.office,
                ).dict()
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "description": "Instructors fetched successfully",
                "instructors": returned_instructors,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/remove_instructor",
    response_description="Instructor removed successfully",
)  # type: ignore
async def remove_instructor(instructor: InstructorModel) -> JSONResponse:
    """
    Remove an instructor.
    If the instructor does not exist, an HTTPException will be raised.

    :param instructor: Instructor info
    :type instructor: BaseModel(see models.py)
    """
    try:
        instructor_obj = Instructor.objects(
            instructor_id=instructor.instructor_id
        ).first()
        user_obj = User.objects(username=instructor.instructor_id).first()
        if not instructor_obj or not user_obj:
            raise HTTPException(status_code=406, detail="Instructor does not exist")

        instructor_obj.delete()
        user_obj.delete()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"description": "Instructor removed successfully"},
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/update_instructor",
    response_description="Instructor updated successfully",
)  # type: ignore
async def update_instructor(instructor: InstructorModel) -> JSONResponse:
    """
    Update an instructor.
    If the instructor does not exist, an HTTPException will be raised.

    :param instructor: Instructor info
    :type instructor: BaseModel(see models.py)
    """
    try:
        instructor_obj = Instructor.objects(
            instructor_id=instructor.instructor_id
        ).first()
        user_obj = User.objects(username=instructor.instructor_id).first()
        if not instructor_obj or not user_obj:
            raise HTTPException(status_code=406, detail="Instructor does not exist")

        instructor_obj.update(
            instructor_id=instructor.instructor_id,
            email=instructor.email,
            name=instructor.name,
            institution=instructor.institution,
            department=instructor.department,
            phone=instructor.phone,
            office=instructor.office,
        )

        hashed_password = generate_password_hash(instructor.password)
        user_obj.update(
            username=instructor.instructor_id,
            password=hashed_password,
            email=instructor.email,
            role="Instructor",
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"description": "Instructor updated successfully"},
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/register_student",
    response_description="Student registered successfully",
)  # type: ignore
async def register_student(student: StudentModel) -> JSONResponse:
    """
    Register a new student.
    If the student already exists, an HTTPException will be raised.

    :param student: Student info
    :type student: BaseModel(see models.py)
    """
    try:
        student_obj = Student.objects(student_id=student.student_id).first()
        user_obj = User.objects(username=student.student_id).first()
        if student_obj or user_obj:
            raise HTTPException(status_code=405, detail="Student already exists")

        new_student = Student(
            student_id=student.student_id,
            email=student.email,
            name=student.name,
            institution=student.institution,
            enrollment_year=student.enrollment_year,
        )
        new_student.save()

        hashed_password = generate_password_hash(student.password)
        new_student_user = User(
            username=student.student_id,
            password=hashed_password,
            email=student.email,
            role="Student",
            institution=student.institution,
        )
        new_student_user.save()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"description": "Student registered successfully"},
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/remove_student",
    response_description="Student removed successfully",
)  # type: ignore
async def remove_student(student: StudentModel) -> JSONResponse:
    """
    Remove an student.
    If the student does not exist, an HTTPException will be raised.

    :param student: Student info
    :type student: BaseModel(see models.py)
    """
    try:
        student_obj = Student.objects(student_id=student.student_id).first()
        user_obj = User.objects(username=student.student_id).first()
        if not student_obj or not user_obj:
            raise HTTPException(status_code=406, detail="Student does not exist")

        student_obj.delete()
        user_obj.delete()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"description": "Student removed successfully"},
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/update_student",
    response_description="Student updated successfully",
)  # type: ignore
async def put_student(student: StudentModel) -> JSONResponse:
    """
    Update an student.
    If the student does not exist, an HTTPException will be raised.

    :param student: Student info
    :type student: BaseModel(see models.py)
    """
    try:
        student_obj = Student.objects(student_id=student.student_id).first()
        user_obj = User.objects(username=student.student_id).first()
        if not student_obj or not user_obj:
            raise HTTPException(status_code=406, detail="Student does not exist")

        student_obj.update(
            student_id=student.student_id,
            email=student.email,
            name=student.name,
            institution=student.institution,
            enrollment_year=student.enrollment_year,
        )

        hashed_password = generate_password_hash(student.password)
        user_obj.update(
            username=student.student_id,
            password=hashed_password,
            email=student.email,
            role="Student",
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"description": "Student updated successfully"},
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
