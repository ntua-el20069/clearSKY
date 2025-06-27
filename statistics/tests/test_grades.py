import unittest
from statistics.statistics.app import app
from statistics.statistics.models.models import Course, Grades

import mongomock
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

client = TestClient(app)


class AddGrades(unittest.TestCase):

    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def test_add_grades_noerror(self) -> None:
        course = {
            "course_id": "NTU_CS101",
            "institution": "Institution name",
            "instructors": ["Instructor id 1", "Instructor id 2"],
            "name": "Introduction to Computer Science",
            "semester": 1,
            "ects": 6,
            "current_registered_students": ["0000001", "0000002", "0000003"],
            "grades": [],
            "finalized": {},
        }
        response = client.post("/courses/add_course", json=course)
        self.assertEqual(response.status_code, 200)
        grades = [
            {
                "student_id": "0000002",
                "name": "abc",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 6.0,
                "question_grades": [9.0, 3.0, 5.0, 7.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            },
            {
                "student_id": "0000001",
                "name": "bca",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 9.5,
                "question_grades": [10.0, 9.0, 9.5, 9.5],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            },
            {
                "student_id": "0000003",
                "name": "bbb",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 9.0,
                "question_grades": [9.0, 9.0, 9.0, 9.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            },
        ]

        response = client.post("/grades/add_grades", json=grades)
        self.assertEqual(response.status_code, 200)

        saved_grades = Grades.objects().first()
        self.assertEqual(saved_grades.student_id, "0000002")
        self.assertEqual(saved_grades.course_id, "NTU_CS101")

    def test_add_grades_duplicate_error(self) -> None:
        course = {
            "course_id": "NTU_CS101",
            "institution": "Institution name",
            "instructors": ["Instructor id 1", "Instructor id 2"],
            "name": "Introduction to Computer Science",
            "semester": 1,
            "ects": 6,
            "current_registered_students": ["0000001", "0000002", "0000003"],
            "grades": [],
            "finalized": {},
        }
        response = client.post("/courses/add_course", json=course)
        self.assertEqual(response.status_code, 200)

        grades = [
            {
                "student_id": "0000001",
                "name": "abc",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 6.0,
                "question_grades": [9.0, 3.0, 5.0, 7.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            },
            {
                "student_id": "0000001",
                "name": "abc",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 9.5,
                "question_grades": [10.0, 9.0, 9.5, 9.5],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            },
            {
                "student_id": "0000003",
                "name": "aaa",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 9.0,
                "question_grades": [9.0, 9.0, 9.0, 9.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            },
        ]

        response = client.post("/grades/add_grades", json=grades)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["detail"],
            "400: Tried to post already existing grades: [0000001, NTU_CS101, Winter, 2024]",
        )

    def test_add_grades_non_existing_student_error(self) -> None:
        course = {
            "course_id": "NTU_CS101",
            "institution": "Institution name",
            "instructors": ["Instructor id 1", "Instructor id 2"],
            "name": "Introduction to Computer Science",
            "semester": 1,
            "ects": 6,
            "current_registered_students": ["0000001", "0000002", "0000003"],
            "grades": [],
            "finalized": {},
        }
        response = client.post("/courses/add_course", json=course)
        self.assertEqual(response.status_code, 200)

        grades = [
            {
                "student_id": "0000006",
                "name": "bbb",
                "course_id": "NTU_CS101",
                "exam_type": "winter",
                "year": 2024,
                "grade": 6.0,
                "question_grades": [9.0, 3.0, 5.0, 7.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            }
        ]

        response = client.post("/grades/add_grades", json=grades)
        self.assertEqual(response.status_code, 400)

    def test_add_grades_duplicate_error_2(self) -> None:
        course = {
            "course_id": "NTU_CS101",
            "institution": "Institution name",
            "instructors": ["Instructor id 1", "Instructor id 2"],
            "name": "Introduction to Computer Science",
            "semester": 1,
            "ects": 6,
            "current_registered_students": ["0000001", "0000002", "0000003"],
            "grades": [],
            "finalized": {},
        }
        response = client.post("/courses/add_course", json=course)
        self.assertEqual(response.status_code, 200)

        grades = [
            {
                "student_id": "0000001",
                "name": "bbb",
                "course_id": "NTU_CS101",
                "exam_type": "winter",
                "year": 2024,
                "grade": 6.0,
                "question_grades": [9.0, 3.0, 5.0, 7.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            }
        ]

        response = client.post("/grades/add_grades", json=grades)
        self.assertEqual(response.status_code, 200)

        grades = [
            {
                "student_id": "0000001",
                "name": "ccc",
                "course_id": "NTU_CS101",
                "exam_type": "winter",
                "year": 2024,
                "grade": 7.35,
                "question_grades": [9.0, 3.0, 7.0, 7.0],
                "grade_weights": [1.0, 1.0, 1.25, 1.25],
            }
        ]

        response = client.post("/grades/add_grades", json=grades)
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Initial grades already posted for",
            response.json()["detail"],
        )


class GetStudentGrades(unittest.TestCase):
    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def test_get_student_grades_no_error(self) -> None:
        course = {
            "course_id": "NTU_CS101",
            "institution": "Institution name",
            "instructors": ["Instructor id 1", "Instructor id 2"],
            "name": "Introduction to Computer Science",
            "semester": 1,
            "ects": 6,
            "current_registered_students": ["0000002", "0000001", "0000003"],
            "grades": [],
            "finalized": {},
        }
        response = client.post("/courses/add_course", json=course)
        self.assertEqual(response.status_code, 200)
        grades = [
            {
                "student_id": "0000002",
                "name": "bca",
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
                "name": "aaa",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 9.0,
                "question_grades": [9.0, 9.0, 9.0, 9.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            },
        ]

        response = client.post("/grades/add_grades", json=grades)
        self.assertEqual(response.status_code, 200)

        params = {
            "student_ids": ["0000001", "0000002"],
            "years": [2024],
            "exam_types": "Winter",
        }
        response = client.get("/grades/get_student_grades", params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["grades"], [grades[1], grades[0]])

        params = {
            "student_ids": ["0000001", "0000003"],
            "years": [2025],
            "exam_types": "Winter",
        }
        response = client.get("/grades/get_student_grades", params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["grades"]), 0)

    def test_get_student_grades_error(self) -> None:
        params = {
            "student_ids": ["0000001", "0000001"],
            "years": [2024],
            "exam_types": "Winter",
        }
        response = client.get("/grades/get_student_grades", params=params)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"], "Found duplicate student id's")

        params = {
            "student_ids": ["0000001", "0000003"],
            "years": [2024, 2024],
            "exam_types": "Winter",
        }
        response = client.get("/grades/get_student_grades", params=params)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"], "Found duplicate years")

        params = {
            "student_ids": ["0000001", "0000003"],
            "years": [2024],
            "exam_types": ["Winter", "Winter"],
        }
        response = client.get("/grades/get_student_grades", params=params)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"], "Found duplicate exam types")


class GetCourseGrades(unittest.TestCase):
    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def test_get_course_grades_no_error(self) -> None:
        course = Course(
            course_id="NTU_CS101",
            name="Computer Science 101",
            institution="National Technical University",
            ects=6,
            instructors=["I123456", "I789012"],
            semester=3,
        )
        course.save()

        grade1 = Grades(
            student_id="0000001",
            name="aaa",
            course_id="NTU_CS101",
            exam_type="Winter",
            year=2024,
            grade=9.5,
            question_grades=[10.0, 9.0, 9.5, 9.5],
            grade_weights=[1.0, 1.0, 1.0, 1.0],
        ).save()

        grade2 = Grades(
            student_id="0000002",
            name="bbb",
            course_id="NTU_CS101",
            exam_type="Winter",
            year=2024,
            grade=6.0,
            question_grades=[9.0, 3.0, 5.0, 7.0],
            grade_weights=[1.0, 1.0, 1.0, 1.0],
        ).save()

        Course.objects(course_id="NTU_CS101").update_one(
            push_all__grades=[grade1, grade2]
        )

        params = {"course_ids": ["NTU_CS101"]}
        response = client.get("/grades/get_course_grades", params=params)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(len(response_data["grades"]), 2)
        self.assertEqual(response_data["grades"][0]["course_id"], "NTU_CS101")

    def test_get_course_grades_error_cases(self) -> None:
        params: dict = {"course_ids": []}
        response = client.get("/grades/get_course_grades", params=params)
        self.assertEqual(response.status_code, 422)

        params = {"course_ids": ["NON_EXISTENT"]}
        response = client.get("/grades/get_course_grades", params=params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["grades"]), 0)


class UpdateGrades(unittest.TestCase):
    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def test_update_no_error(self) -> None:
        course = {
            "course_id": "NTU_CS101",
            "institution": "Institution name",
            "instructors": ["Instructor id 1", "Instructor id 2"],
            "name": "Introduction to Computer Science",
            "semester": 1,
            "ects": 6,
            "current_registered_students": ["0000001", "0000002", "0000003"],
            "grades": [],
            "finalized": {},
        }
        response = client.post("/courses/add_course", json=course)
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
        ]

        # Add initial grades
        response = client.post("/grades/add_grades", json=grades)
        self.assertEqual(response.status_code, 200)

        updated_grades = [
            {
                "student_id": "0000001",
                "name": "bbb",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 10.0,
                "question_grades": [10.0, 10.0, 10.0, 10.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            }
        ]

        response = client.put("/grades/update_grades", json=updated_grades)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["description"], "Updated 1 grades. Failed to update 0"
        )
        self.assertEqual(Grades.objects(student_id="0000001").first().grade, 10.0)

        updated_grades = [
            {
                "student_id": "0000001",
                "name": "aaa",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 8.0,
                "question_grades": [10.0, 10.0, 6.0, 7.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            },
            {
                "student_id": "0000002",
                "name": "bbb",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
                "grade": 8.0,
                "question_grades": [10.0, 10.0, 6.0, 7.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            },
        ]
        response = client.put("/grades/update_grades", json=updated_grades)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Grades.objects(student_id="0000001").first().grade, 8.0)
        self.assertEqual(Grades.objects(student_id="0000002").first().grade, 8.0)
        self.assertEqual(
            Grades.objects(student_id="0000001").first().question_grades,
            [10.0, 10.0, 6.0, 7.0],
        )

        updated_grades = [
            {
                "student_id": "not_existing",
                "course_id": "...",
                "exam_type": "Hell",
                "year": 2025,
                "grade": 0.0,
                "question_grades": [0.0, 0.0, 0.0, 0.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            }
        ]
        response = client.put("/grades/update_grades", json=updated_grades)
        self.assertEqual(response.status_code, 400)

    def test_update_error(self) -> None:
        updated_grades = [
            {
                "student_id": "0000001",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2026,
                "grade": 8.0,
                "question_grades": [10.0, 10.0, 6.0, 7.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            }
        ]
        response = client.put("/grades/update_grades", json=updated_grades)
        self.assertEqual(response.status_code, 422)

        updated_grades = [
            {
                "student_id": "0000001",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2025,
                "grade": 10.1,
                "question_grades": [10.0, 10.0, 10.0, 10.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            }
        ]
        response = client.put("/grades/update_grades", json=updated_grades)
        self.assertEqual(response.status_code, 422)

        updated_grades = [
            {
                "student_id": "0000001",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2025,
                "grade": 10.0,
                "question_grades": [10.0, 10.0, 10.0, 15.0],
                "grade_weights": [1.0, 1.0, 1.0, 1.0],
            }
        ]
        response = client.put("/grades/update_grades", json=updated_grades)
        self.assertEqual(response.status_code, 422)


class DeleteGrades(unittest.TestCase):
    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def test_delete_grades_no_error(self) -> None:
        course = {
            "course_id": "NTU_CS101",
            "institution": "Institution name",
            "instructors": ["Instructor id 1", "Instructor id 2"],
            "name": "Introduction to Computer Science",
            "semester": 1,
            "ects": 6,
            "current_registered_students": ["0000001", "0000002", "0000003"],
            "grades": [],
            "finalized": {},
        }
        response = client.post("/courses/add_course", json=course)
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
        ]

        response = client.post("/grades/add_grades", json=grades)
        self.assertEqual(response.status_code, 200)

        grades_to_delete = [
            {
                "student_id": "0000002",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2024,
            }
        ]

        response = client.request(
            "DELETE", "/grades/delete_grades", json=grades_to_delete
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Grades.objects(student_id="0000002")), 0)
        self.assertEqual(
            response.json()["description"], "Deleted 1 grades. Failed to delete 0"
        )

    def test_delete_grades_error(self) -> None:
        grades_to_delete = [
            {
                "student_id": "0000002",
                "course_id": "NTU_CS101",
                "exam_type": "Winter",
                "year": 2420,
            }
        ]

        response = client.request(
            "DELETE", "/grades/delete_grades", json=grades_to_delete
        )
        self.assertEqual(response.status_code, 422)
