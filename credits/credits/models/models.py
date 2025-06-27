from mongoengine import Document, IntField, StringField
from pydantic import BaseModel, Field


class Credits(Document):
    institution = StringField(required=True, unique=True)
    credits = IntField(required=True)

    class Config:
        json_schema_extra = {
            "example": {
                "institution": "National Technical University of Athens",
                "credits": 20,
            }
        }


class CreditsModel(BaseModel):
    institution: str
    credits: int = Field(int, ge=0.0)
