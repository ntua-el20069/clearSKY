import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import unittest

import mongomock
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from user_management.user_management.app import app
from user_management.user_management.models.models import Instructor

client = TestClient(app)


class RegisterInstructor(unittest.TestCase):
    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        Instructor.objects().delete()

    def tearDown(self) -> None:
        disconnect()

    def test_register_instructor_no_error(self) -> None:
        instructor_data = {
            "instructor_id": "inst001",
            "password": "123456789",
            "email": "john@example.com",
            "name": "John Doe",
            "institution": "Example University",
            "department": "CS",
            "phone": "1234567890",
            "office": "Room 101",
        }

        response = client.post("/register/register_instructor", json=instructor_data)
        print(app.routes)
        self.assertEqual(response.status_code, 200)

    def test_register_instructor_conflict(self) -> None:
        instructor_data = {
            "instructor_id": "inst001",
            "password": "123456789",
            "email": "john@example.com",
            "name": "John Doe",
            "institution": "Example University",
            "department": "CS",
            "phone": "1234567890",
            "office": "Room 101",
        }

        client.post("/register/register_instructor", json=instructor_data)
        response = client.post("/register/register_instructor", json=instructor_data)
        self.assertEqual(response.status_code, 405)

    def test_register_instructor_missing_fields(self) -> None:
        instructor_data = {
            "instructor_id": "inst001",
            "password": "123456789",
            "name": "John Doe",
            "institution": "Example University",
            "department": "CS",
            "phone": "1234567890",
            "office": "Room 101",
        }
        response = client.post("/register/register_instructor", json=instructor_data)
        self.assertEqual(response.status_code, 422)


class RemoveInstructor(unittest.TestCase):
    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        Instructor.objects().delete()

    def tearDown(self) -> None:
        disconnect()

    def test_remove_instructor_no_error(self) -> None:
        instructor_data = {
            "instructor_id": "inst001",
            "password": "123456789",
            "email": "john@example.com",
            "name": "John Doe",
            "institution": "Example University",
            "department": "CS",
            "phone": "1234567890",
            "office": "Room 101",
        }

        client.post("/register/register_instructor", json=instructor_data)
        response = client.request(
            "DELETE", "/register/remove_instructor", json=instructor_data
        )
        self.assertEqual(response.status_code, 200)

    def test_remove_instructor_not_found(self) -> None:
        instructor_data = {
            "instructor_id": "nonexistent",
            "password": "123456789",
            "email": "ghost@example.com",
            "name": "Ghost",
            "institution": "Nowhere",
            "department": "Unknown",
            "phone": "0000000000",
            "office": "None",
        }

        response = client.request(
            "DELETE", "/register/remove_instructor", json=instructor_data
        )
        self.assertEqual(response.status_code, 406)


class UpdateInstructor(unittest.TestCase):
    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )
        Instructor.objects().delete()

    def tearDown(self) -> None:
        disconnect()

    def test_update_instructor_no_error(self) -> None:
        instructor_data = {
            "instructor_id": "inst001",
            "password": "123456789",
            "email": "john@example.com",
            "name": "John Doe",
            "institution": "Example University",
            "department": "CS",
            "phone": "1234567890",
            "office": "Room 101",
        }

        updated_data = {
            **instructor_data,
            "email": "new_email@example.com",
            "phone": "9999999999",
        }

        client.post("/register/register_instructor", json=instructor_data)
        response = client.put("/register/update_instructor", json=updated_data)
        self.assertEqual(response.status_code, 200)

    def test_update_instructor_not_found(self) -> None:
        instructor_data = {
            "instructor_id": "nonexistent",
            "password": "123456789",
            "email": "ghost@example.com",
            "name": "Ghost",
            "institution": "Nowhere",
            "department": "Unknown",
            "phone": "0000000000",
            "office": "None",
        }

        response = client.put("/register/update_instructor", json=instructor_data)
        self.assertEqual(response.status_code, 406)
