from datetime import datetime
from typing import Optional

from mongoengine import (
    BooleanField,
    Document,
    FloatField,
    IntField,
    ListField,
    MapField,
    ReferenceField,
    StringField,
)
from pydantic import BaseModel, Field, confloat, conlist


class Grades(Document):
    student_id = StringField(required=True)
    name = StringField(required=True)
    course_id = StringField(required=True)
    exam_type = StringField(required=True)
    year = IntField(required=True)
    grade = FloatField(required=True)
    question_grades = ListField(FloatField(), required=True)
    grade_weights = ListField(FloatField(), required=True)

    meta = {
        "indexes": [
            {
                "fields": ["student_id", "course_id", "exam_type", "year"],
                "unique": True,
            },
        ]
    }

    class Config:
        json_schema_extra = {
            "example": {
                "student": "03121000",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 10.0,
                "question_grades": [10.0, 10.0, 10.0],
                "grade_weights": [1.25, 2.5, 2.5],
            }
        }


class GradesModel(BaseModel):
    student_id: str = Field(str)
    name: str = Field(str)
    course_id: str = Field(str)
    exam_type: str = Field(str)
    year: int = Field(int, ge=2000, le=datetime.now().year)
    grade: float = Field(float, ge=0.0, le=10.0)
    question_grades: conlist(item_type=confloat(ge=0.0, le=10.0))  # type: ignore
    grade_weights: conlist(item_type=confloat())  # type: ignore


class GradesModelOps(BaseModel):
    student_id: str = Field(str)
    course_id: str = Field(str)
    exam_type: str = Field(str)
    year: int = Field(int, ge=2000, le=datetime.now().year)


class CourseStatistics(Document):
    course_id = StringField(required=True)
    exam_type = StringField(required=True)
    year = IntField(required=True)
    grades_dist = MapField(field=IntField(), required=True)
    question_grades_dist = ListField(
        MapField(field=IntField()), required=True
    )  # list[i] -> distribution for i-th question

    meta = {
        "indexes": [
            {
                "fields": ["course_id", "exam_type", "year"],
                "unique": True,
            },
        ]
    }

    class Config:
        json_schema_extra = {
            "example": {
                "course_id": "NTU-SaaS",
                "exam_type": "Winter",
                "year": 2024,
                "grades_dist": {
                    "4.0": 12,
                    "8.0": 6,
                    "9.0": 4,
                    "10.0": 1,
                },
                "question_grades_dist": [
                    {
                        "8.0": 5,
                        "9.0": 20,
                    },
                ],
            }
        }


class Course(Document):
    course_id = StringField(required=True, unique=True)
    institution = StringField(required=True)
    instructors = ListField(StringField(required=True), required=True)
    name = StringField(required=True)
    semester = IntField(required=True)
    ects = IntField(required=True)
    current_registered_students = ListField(StringField(unique=True), required=False)
    grades = ListField(ReferenceField(Grades), required=False)
    finalized = MapField(field=BooleanField(required=False))

    class Config:
        json_schema_extra = {
            "example": {
                "course_id": "CS101",
                "institution": "Institution name",
                "instructors": ["Instructor id 1", "Instructor id 2"],
                "name": "Introduction to Computer Science",
                "semester": 1,
                "ects": 6,
                "current_registered_students": ["id1", "id2"],
                "grades": ["Object[Grade]", "Object[Grade]"],
                "finalized": {
                    "2023-Winter": True,
                    "2023-September": True,
                    "2024-Winter": True,
                    "2024-September": True,
                    "2025-Winter": False,
                },
            }
        }


class CourseModel(BaseModel):
    course_id: str
    institution: str
    instructors: list[str]
    name: str
    semester: int = Field(int, ge=1)
    ects: int = Field(int, ge=1, le=10)
    current_registered_students: list[str]
    grades: list[GradesModel]
    finalized: dict


class CourseGradesData(BaseModel):
    course_ids: list[str]
    instructors: Optional[list[str]] = None
    semester: Optional[list[int]] = None


class EnrollmentModel(BaseModel):
    course_id: str
    current_registered_students: list[str]
