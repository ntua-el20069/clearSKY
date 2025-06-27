from typing import Optional

from mongoengine import Document, IntField, StringField
from pydantic import BaseModel, Extra


class User(Document):
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    email = StringField(required=False, unique=True)
    institution = StringField(required=True)
    role = StringField(
        required=True,
        choices=["Admin", "InstitutionRepresentative", "Instructor", "Student"],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "username": "el00000",
                "password": "123456789",
                "email": "I21312@uoa.gr",
                "institution": "National Technical University of Athens",
                "role": "Student",
            }
        }


class UserModel(BaseModel):
    username: str
    password: str

    class Config:
        extra = Extra.forbid


class Session(Document):
    token = StringField(required=True, unique=True)
    username = StringField(required=True, unique=True)
    role = StringField(
        required=True,
        choices=["Admin", "InstitutionRepresentative", "Instructor", "Student"],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "token": "123456789",
                "username": "el00000",
                "role": "Student",
            }
        }


class Instructor(Document):
    instructor_id = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    name = StringField(required=True)
    institution = StringField(required=True)
    department = StringField(required=False)
    phone = StringField(required=False)
    office = StringField(required=False)

    class Config:
        json_schema_extra = {
            "example": {
                "instructor_id": "I21312",
                "email": "I21312@uoa.gr",
                "name": "Alexandros Mandilaras",
                "institution": "National Technical University of Athens",
                "department": "Computer Science",
                "phone": "+210 XXXXXXXXX",
                "office": "1.1.13 old Electrical Engineering buildings",
            }
        }


class InstructorModel(BaseModel):
    instructor_id: str
    password: Optional[str] = None
    email: str
    name: str
    institution: str
    department: Optional[str] = None
    phone: Optional[str] = None
    office: Optional[str] = None


class Student(Document):
    student_id = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    name = StringField(required=True)
    institution = StringField(required=True)
    enrollment_year = IntField(required=True)

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "S13213",
                "email": "S13213@ntua.gr",
                "name": "Adamantios Adamantiou",
                "institution": "National Technical University of Athens",
                "enrollment_year": 2021,
            }
        }


class StudentModel(BaseModel):
    student_id: str
    password: str
    email: str
    name: str
    institution: str
    enrollment_year: str


class InstitutionRepresentative(Document):
    representative_id = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    name = StringField(required=True)
    institution = StringField(required=True)

    class Config:
        json_schema_extra = {
            "example": {
                "representative_id": "R1234",
                "email": "R1234@ntua.gr",
                "name": "Adamantios Adamantiou",
                "institution": "National Technical University of Athens",
            }
        }


class InstitutionRepresentativeModel(BaseModel):
    representative_id: str
    password: str
    email: str
    name: str
    institution: str
