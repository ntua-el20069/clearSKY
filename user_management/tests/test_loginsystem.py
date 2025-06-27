import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import unittest

import mongomock
from fastapi.security import OAuth2PasswordBearer
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect
from werkzeug.security import generate_password_hash

from user_management.user_management.app import app
from user_management.user_management.models.models import Session, User

client = TestClient(app)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class TestLoginFastAPI(unittest.TestCase):
    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        Session.objects().delete()
        User.objects().delete()

        # Create test users
        User(
            username="Admin1",
            password=generate_password_hash("123456789"),
            email="admin@ntua.gr",
            role="Admin",
            institution="NTUA",
        ).save()
        User(
            username="InstitutionRepresentative1",
            password=generate_password_hash("123456789"),
            email="institutionrepresentative@ntua.gr",
            role="InstitutionRepresentative",
            institution="NTUA",
        ).save()
        User(
            username="Instructor1",
            password=generate_password_hash("123456789"),
            email="instructor@ntua.gr",
            role="Instructor",
            institution="NTUA",
        ).save()
        User(
            username="Student1",
            password=generate_password_hash("123456789"),
            email="student@ntua.gr",
            role="Student",
            institution="NTUA",
        ).save()

    def tearDown(self) -> None:
        Session.objects().delete()
        User.objects().delete()
        disconnect()

    def test_admin_login(self) -> None:
        login_json = {"username": "Admin1", "password": "123456789"}
        response = client.post("/login/login", json=login_json)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("token", data)

        token_in_db = Session.objects(username="Admin1").first()
        self.assertIsNotNone(token_in_db)
        self.assertEqual(token_in_db.token, data["token"])

    def test_InstitutionRepresentative_login(self) -> None:
        login_json = {
            "username": "InstitutionRepresentative1",
            "password": "123456789",
        }
        response = client.post("/login/login", json=login_json)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("token", data)

        token_in_db = Session.objects(username="InstitutionRepresentative1").first()
        self.assertIsNotNone(token_in_db)
        self.assertEqual(token_in_db.token, data["token"])

    def test_Instructor_login(self) -> None:
        login_json = {
            "username": "Instructor1",
            "password": "123456789",
        }
        response = client.post("/login/login", json=login_json)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("token", data)

        token_in_db = Session.objects(username="Instructor1").first()
        self.assertIsNotNone(token_in_db)
        self.assertEqual(token_in_db.token, data["token"])

    def test_Student_login(self) -> None:
        login_json = {
            "username": "Student1",
            "password": "123456789",
        }
        response = client.post("/login/login", json=login_json)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("token", data)

        token_in_db = Session.objects(username="Student1").first()
        self.assertIsNotNone(token_in_db)
        self.assertEqual(token_in_db.token, data["token"])

    def test_invalid_username(self) -> None:
        login_json = {"username": "wronguser", "password": "123456789"}
        response = client.post("/login/login", json=login_json)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid credentials")

    def test_invalid_password(self) -> None:
        login_json = {
            "username": "Admin1",
            "password": "wrongpassword",
        }
        response = client.post("/login/login", json=login_json)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid credentials")

    def test_missing_username(self) -> None:
        login_json = {"password": "123456789"}
        response = client.post("/login/login", json=login_json)
        print(response.status_code)
        print(response.json())
        self.assertEqual(response.status_code, 422)

    def test_missing_password(self) -> None:
        login_json = {"username": "Student1"}
        response = client.post("/login/login", json=login_json)
        print(response.status_code)
        print(response.json())
        self.assertEqual(response.status_code, 422)

    def test_extra_columns(self) -> None:
        login_json = {
            "username": "Admin1",
            "password": "123456789",
            "extra": 0,
        }
        response = client.post("/login/login", json=login_json)
        print(response.status_code)
        print(response.json())
        self.assertEqual(response.status_code, 422)

    def test_invalid_data_format(self) -> None:
        login_json = {"username": "Admin1", "password": "123456789", "wrong": "Admin"}
        response = client.post("/login/login", json=login_json)
        print(response.status_code)
        print(response.json())
        self.assertEqual(response.status_code, 422)

    def test_user_already_logged_in(self) -> None:
        login_json = {"username": "Admin1", "password": "123456789"}
        response = client.post("/login/login", json=login_json)
        print(response.status_code)
        print(response.json())
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("token", data)

        token_in_db = Session.objects(username="Admin1").first()
        self.assertIsNotNone(token_in_db)
        self.assertEqual(token_in_db.token, data["token"])

        login_json = {"username": "Admin1", "password": "123456789"}
        response = client.post("/login/login", json=login_json)
        print(response.status_code)
        print(response.json())
        self.assertEqual(response.status_code, 402)
        self.assertEqual(response.json()["detail"], "Already logged in")


class TestLogoutFastAPI(unittest.TestCase):
    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        Session.objects().delete()
        User.objects().delete()

        # Create test users
        User(
            username="Admin1",
            password=generate_password_hash("123456789"),
            email="admin@ntua.gr",
            role="Admin",
            institution="NTUA",
        ).save()
        User(
            username="InstitutionRepresentative1",
            password=generate_password_hash("123456789"),
            email="institutionrepresentative@ntua.gr",
            role="InstitutionRepresentative",
            institution="NTUA",
        ).save()
        User(
            username="Instructor1",
            password=generate_password_hash("123456789"),
            email="instructor@ntua.gr",
            role="Instructor",
            institution="NTUA",
        ).save()
        User(
            username="Student1",
            password=generate_password_hash("123456789"),
            email="student@ntua.gr",
            role="Student",
            institution="NTUA",
        ).save()

    def tearDown(self) -> None:
        Session.objects().delete()
        User.objects().delete()
        disconnect()

    def test_user_logout(self) -> None:
        login_json = {"username": "Admin1", "password": "123456789"}
        login_response = client.post("/login/login", json=login_json)
        token = login_response.json()["token"]

        headers = {"Authorization": f"Bearer {token}"}
        logout_response = client.post("/login/logout", headers=headers)
        self.assertEqual(logout_response.status_code, 204)

        session = Session.objects(token=token).first()
        self.assertIsNone(session)

    def test_missing_token(self) -> None:
        login_json = {"username": "Admin1", "password": "123456789"}
        _ = client.post("/login/login", json=login_json)
        token = ""

        headers = {"Authorization": f"Bearer {token}"}
        logout_response = client.post("/login/logout", headers=headers)
        self.assertEqual(logout_response.status_code, 400)
        self.assertEqual(logout_response.json()["detail"], "Token missing")

    def test_invalid_token(self) -> None:
        login_json = {"username": "Admin1", "password": "123456789"}
        _ = client.post("/login/login", json=login_json)

        headers = {"Authorization": "Bearer 1234567890"}
        logout_response = client.post("/login/logout", headers=headers)
        self.assertEqual(logout_response.status_code, 401)
        self.assertEqual(
            logout_response.json()["detail"], "Invalid token or already logged out"
        )

    def test_token_with_no_user(self) -> None:
        headers = {"Authorization": "Bearer 1234567890"}
        logout_response = client.post("/login/logout", headers=headers)
        self.assertEqual(logout_response.status_code, 401)
        self.assertEqual(
            logout_response.json()["detail"], "Invalid token or already logged out"
        )
