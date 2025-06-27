from datetime import datetime
from typing import Optional

from mongoengine import BooleanField, DateTimeField, Document, IntField, StringField
from pydantic import BaseModel, Field


class Review(Document):
    student_id = StringField(required=True)
    course_id = StringField(required=True)
    exam_type = StringField(required=True)
    year = IntField(required=True)

    review_text = StringField(
        required=True, min_length=10
    )  # MongoEngine uses StringField
    reply_text = StringField()  # Optional by default in MongoEngine
    is_replied = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "indexes": [
            {
                "fields": ["student_id", "course_id", "exam_type", "year"],
                "unique": True,
            },
        ]
    }


class ReviewBase(BaseModel):
    student_id: str = Field(str)
    course_id: str = Field(str)
    exam_type: str = Field(str)
    year: int = Field(int, ge=2000, le=datetime.now().year)


class ReviewCreate(ReviewBase):
    review_text: str


class ReviewResponse(ReviewBase):
    review_text: str = Field(str)
    reply_text: Optional[str] = Field(None)
    is_replied: bool = Field(False)
    created_at: str = Field(str)  # use string because datetime is not JSON serializable

    class Config:

        json_schema_extra = {
            "example": {
                "student_id": "STU123",
                "course_id": "CS101",
                "exam_type": "winter",
                "year": 2024,
                "review_text": "Please review my grade...",
                "reply_text": None,
                "is_replied": False,
                "created_at": "2024-06-05T09:30:00Z",
            }
        }


class ReviewReply(ReviewBase):
    reply_text: str
