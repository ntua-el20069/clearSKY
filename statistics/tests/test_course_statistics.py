import unittest
from statistics.statistics.app import app

import mongomock
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

client = TestClient(app)


class GetCourseStats(unittest.TestCase):

    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def test_get_course_stats_no_error(self) -> None:
        test_courses = {
            "course_id": "NTU_CS101",
            "institution": "National Technical University of Athens",
            "instructors": ["I213213", "I412341"],
            "name": "Introduction to Computer Science",
            "semester": 3,
            "ects": 6,
            "current_registered_students": [
                "0000002",
                "0000001",
                "0000003",
                "0000004",
                "0000005",
                "0000006",
            ],
            "grades": [],
            "finalized": {},
        }

        response = client.post("/courses/add_course", json=test_courses)
        self.assertEqual(response.status_code, 200)

        grades = [
            {
                "student_id": "0000002",
                "name": "aaa",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 6.0,
                "question_grades": [9.0, 3.0, 5.0, 7.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            },
            {
                "student_id": "0000001",
                "name": "bbb",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 9.5,
                "question_grades": [10.0, 9.0, 9.5, 9.5],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            },
            {
                "student_id": "0000003",
                "name": "ccc",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 9.0,
                "question_grades": [9.0, 9.0, 9.0, 9.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            },
            {
                "student_id": "0000005",
                "name": "fff",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 9.0,
                "question_grades": [9.0, 9.0, 9.0, 9.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            },
        ]

        # initial [post grades]
        response = client.post("/grades/add_grades", json=grades)
        self.assertEqual(response.status_code, 200)

        response = client.get(
            "/course_stats/get_course_stats?course_id=NTU_CS101&exam_year=2024&exam_type=Winter"
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        grades_dist = response["grades_dist"]
        question_grades_dist = response["question_grades_dist"]

        self.assertEqual(grades_dist.get("9.0", 0), 2)
        self.assertEqual(grades_dist.get("6.0", 0), 1)
        self.assertEqual(grades_dist.get("9.5", 0), 1)
        self.assertEqual(grades_dist.get("8.2", 0), 0)

        self.assertEqual(question_grades_dist[0]["9.0"], 3)
        self.assertEqual(question_grades_dist[0]["10.0"], 1)

        updated_grades = [
            {
                "student_id": "0000002",
                "name": "aaa",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 5.0,
                "question_grades": [9.0, 3.0, 3.0, 4.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            },
            {
                "student_id": "0000001",
                "name": "bbb",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 8.5,
                "question_grades": [10.0, 9.0, 9.5, 4.2],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            },
            {
                "student_id": "0000003",
                "name": "ccc",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 9.0,
                "question_grades": [9.0, 9.0, 9.0, 9.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            },
            {
                "student_id": "0000005",
                "name": "fff",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 7.0,
                "question_grades": [9.0, 9.0, 9.0, 9.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            },
        ]
        response = client.put("/grades/update_grades", json=updated_grades)
        print(response.json())
        self.assertEqual(response.status_code, 200)
        response = client.get(
            "/course_stats/get_course_stats?course_id=NTU_CS101&exam_year=2024&exam_type=Winter"
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        grades_dist = response["grades_dist"]
        question_grades_dist = response["question_grades_dist"]

        self.assertEqual(grades_dist.get("5.0", 0), 1)
        self.assertEqual(grades_dist.get("9.0", 0), 1)
        self.assertEqual(grades_dist.get("7.0", 0), 1)

        self.assertEqual(question_grades_dist[1]["3.0"], 1)
        self.assertEqual(question_grades_dist[0]["9.0"], 3)
        self.assertEqual(question_grades_dist[3]["4.2"], 1)
        self.assertEqual(question_grades_dist[3]["4.0"], 1)
        self.assertEqual(question_grades_dist[3]["9.0"], 2)
