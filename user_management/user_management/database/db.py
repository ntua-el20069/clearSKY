import os

import mongoengine
from werkzeug.security import generate_password_hash

from user_management.user_management.models.models import User


def initialize_db() -> None:
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongoengine.connect(db="user_management", host=mongo_uri, alias="default")

    # Create a default admin if not exists
    default_username = "Admin1"
    if not User.objects(username=default_username).first():
        default_user = User(
            username=default_username,
            password=generate_password_hash("123456789"),
            role="Admin",
            institution="NTUA",
            email="saas2520ntua@gmail.com",
        )
        default_user.save()
        print("Default admin user created.")
    else:
        print("Default admin user already exists.")
