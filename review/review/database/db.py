import os

import mongoengine


def initialize_db() -> None:
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongoengine.connect(db="review", host=mongo_uri, alias="default")
