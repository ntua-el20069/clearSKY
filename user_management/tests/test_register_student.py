import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import unittest

import mongomock
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from user_management.user_management.app import app
from user_management.user_management.models.models import Student

client = TestClient(app)


class RegisterStudent(unittest.TestCase):
    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        Student.objects().delete()

    def tearDown(self) -> None:
        disconnect()

    def test_register_student_should_succeed(self) -> None:
        student_data = {
            "student_id": "S12345",
            "password": "123456789",
            "email": "john@example.com",
            "name": "John Doe",
            "institution": "Example University",
            "enrollment_year": "2023",
        }
        response = client.post("/register/register_student", json=student_data)
        self.assertEqual(response.status_code, 200)

    def test_register_student_conflict(self) -> None:
        student_data = {
            "student_id": "S12345",
            "password": "123456789",
            "email": "john@example.com",
            "name": "John Doe",
            "institution": "Example University",
            "enrollment_year": "2023",
        }
        client.post("/register/register_student", json=student_data)
        response = client.post("/register/register_student", json=student_data)
        self.assertEqual(response.status_code, 405)

    def test_register_student_missing_fields(self) -> None:
        student_data = {
            "student_id": "S12345",
            "password": "123456789",
            "name": "John Doe",
            "institution": "Example University",
            "enrollment_year": "2023",
        }
        response = client.post("/register/register_student", json=student_data)
        self.assertEqual(response.status_code, 422)

    def test_delete_student(self) -> None:
        student_data = {
            "student_id": "S12345",
            "password": "123456789",
            "email": "john@example.com",
            "name": "John Doe",
            "institution": "Example University",
            "enrollment_year": "2023",
        }
        response = client.post("/register/register_student", json=student_data)
        self.assertEqual(response.status_code, 200)
        response = client.request(
            "DELETE", "/register/remove_student", json=student_data
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_student_not_found(self) -> None:
        student_data = {
            "student_id": "nonexistent",
            "password": "123456789",
            "email": "john@example.com",
            "name": "John Doe",
            "institution": "Example University",
            "enrollment_year": "2023",
        }
        response = client.request(
            "DELETE", "/register/remove_student", json=student_data
        )
        self.assertEqual(response.status_code, 406)

    def test_update_student(self) -> None:
        student_data = {
            "student_id": "S12345",
            "password": "123456789",
            "email": "john@example.com",
            "name": "John Doe",
            "institution": "Example University",
            "enrollment_year": "2023",
        }
        client.post("/register/register_student", json=student_data)
        updated_data = {
            **student_data,
            "email": "new@address.com",
            "institution": "New University",
        }
        response = client.put("/register/update_student", json=updated_data)
        self.assertEqual(response.status_code, 200)

    def test_update_student_not_found(self) -> None:
        student_data = {
            "student_id": "nonexistent",
            "password": "123456789",
            "email": "john@example.com",
            "name": "John Doe",
            "institution": "Example University",
            "enrollment_year": "2023",
        }
        response = client.put("/register/update_student", json=student_data)
        self.assertEqual(response.status_code, 406)
