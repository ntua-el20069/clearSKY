import unittest
from statistics.statistics.app import app
from statistics.statistics.models.models import Course

import mongomock
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

client = TestClient(app)


class AddCourses(unittest.TestCase):

    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def test_add_courses_noerror(self) -> None:
        test_courses = {
            "course_id": "NTU_CS101",
            "institution": "National Technical University of Athens",
            "instructors": ["I213213", "I412341"],
            "name": "Introduction to Computer Science",
            "semester": 3,
            "ects": 6,
            "current_registered_students": [
                "03121321",
                "03121322",
                "03175846",
                "03172856",
                "03121968",
            ],
            "grades": [],
            "finalized": {},
        }

        response = client.post("/courses/add_course", json=test_courses)
        self.assertEqual(response.status_code, 200)

        course = Course.objects().first()
        self.assertEqual(course.course_id, "NTU_CS101")
        self.assertEqual(len(course.current_registered_students), 5)
        self.assertEqual(course.current_registered_students[0], "03121321")

    def test_add_courses_duplicate_error(self) -> None:
        test_courses = {
            "course_id": "NTU_CS101",
            "institution": "National Technical University of Athens",
            "instructors": ["I213213", "I412341"],
            "name": "Introduction to Computer Science",
            "semester": 3,
            "ects": 6,
            "current_registered_students": [
                "03121111",
                "03121112",
                "03121112",
                "03121111",
                "03121312",
            ],
            "grades": [],
            "finalized": {},
        }

        response = client.post("/courses/add_course", json=test_courses)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"], "Found duplicate student id's")

        test_courses = {
            "course_id": "NTU_CS102",
            "institution": "National Technical University of Athens",
            "instructors": ["I213213", "I213213"],
            "name": "Introduction to Computer Science",
            "semester": 4,
            "ects": 6,
            "current_registered_students": [
                "03121119",
                "03121115",
                "03121112",
                "03121111",
                "03121312",
            ],
            "grades": [],
            "finalized": {},
        }
        response = client.post("/courses/add_course", json=test_courses)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"], "Found duplicate instructor id's")


class DeleteCourses(unittest.TestCase):
    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def testing_deletion(self) -> None:
        test_courses = {
            "course_id": "NTU_CS101",
            "institution": "National Technical University of Athens",
            "instructors": ["I213213", "I412341"],
            "name": "Introduction to Computer Science",
            "semester": 3,
            "ects": 6,
            "current_registered_students": [
                "03121321",
                "03121322",
                "03175846",
                "03172856",
                "03121968",
            ],
            "grades": [],
            "finalized": {},
        }

        response = client.post("/courses/add_course", json=test_courses)
        self.assertEqual(response.status_code, 200)
        response = client.delete("/courses/delete_course/NTU_CS101")
        self.assertEqual(response.status_code, 200)

        courses = Course.objects()
        self.assertEqual(len(courses), 0)

        response = client.delete("/courses/delete_course/NTU_23131")
        self.assertEqual(response.status_code, 404)


class FinalizeCourse(unittest.TestCase):
    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def testing_finalization(self) -> None:
        test_courses = {
            "course_id": "NTU_CS101",
            "institution": "National Technical University of Athens",
            "instructors": ["I213213", "I412341"],
            "name": "Introduction to Computer Science",
            "semester": 3,
            "ects": 6,
            "current_registered_students": [
                "03121321",
                "03121322",
                "03175846",
                "03172856",
                "03121968",
            ],
            "grades": [],
            "finalized": {},
        }

        response = client.post("/courses/add_course", json=test_courses)
        self.assertEqual(response.status_code, 200)

        response = client.get(
            "/courses/finalize_course/course_id=NTU_CS101&exam_type=Winter&exam_year=2024"
        )
        self.assertEqual(response.status_code, 200)
        course = Course.objects(course_id="NTU_CS101").first()
        print(course.finalized)
        self.assertEqual(course.finalized["Winter-2024"], True)


class InitializeCourseGrades(unittest.TestCase):
    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def test_initialize_course(self) -> None:
        test_courses = {
            "course_id": "NTU_CS101",
            "institution": "National Technical University of Athens",
            "instructors": ["I213213", "I412341"],
            "name": "Introduction to Computer Science",
            "semester": 3,
            "ects": 6,
            "current_registered_students": [
                "03121321",
                "03121322",
                "03175846",
                "03172856",
                "03121968",
            ],
            "grades": [],
            "finalized": {},
        }

        response = client.post("/courses/add_course", json=test_courses)
        self.assertEqual(response.status_code, 200)

        response = client.get(
            "/courses/initialize_course_grades/course_id=NTU_CS101&exam_type=Winter&exam_year=2024"
        )
        self.assertEqual(response.status_code, 200)
        course = Course.objects(course_id="NTU_CS101").first()
        self.assertIn("Winter-2024", course.finalized)
        self.assertFalse(course.finalized["Winter-2024"])


class GetGradesStatus(unittest.TestCase):
    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def test_get_grades_status(self) -> None:

        test_courses = {
            "course_id": "NTU_CS101",
            "institution": "National Technical University of Athens",
            "instructors": ["I213213", "I412341"],
            "name": "Introduction to Computer Science",
            "semester": 3,
            "ects": 6,
            "current_registered_students": [
                "03121321",
                "03121322",
                "03175846",
                "03172856",
                "03121968",
            ],
            "grades": [],
            "finalized": {},
        }

        response = client.get(
            "/courses/status_of_grades/course_id=NTU_CS101&exam_type=Winter&exam_year=2024"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())
        self.assertIn("Can't find course", response.json()["detail"])

        response = client.post("/courses/add_course", json=test_courses)
        self.assertEqual(response.status_code, 200)

        response = client.get(
            "/courses/status_of_grades/course_id=NTU_CS101&exam_type=Winter&exam_year=2024"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("grades_status", response.json())
        self.assertEqual(response.json()["grades_status"], "UNKNOWN")

        # INTITIAL POST GRADES - just initialize the course grades
        response = client.get(
            "/courses/initialize_course_grades/course_id=NTU_CS101&exam_type=Winter&exam_year=2024"
        )
        self.assertEqual(
            response.status_code, 200, "Failed to initialize course grades"
        )
        response = client.get(
            "/courses/status_of_grades/course_id=NTU_CS101&exam_type=Winter&exam_year=2024"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("grades_status", response.json())
        self.assertEqual(response.json()["grades_status"], "INITIAL")

        # FINAL POST GRADES - just finalize the course
        response = client.get(
            "/courses/finalize_course/course_id=NTU_CS101&exam_type=Winter&exam_year=2024"
        )
        self.assertEqual(response.status_code, 200)
        response = client.get(
            "/courses/status_of_grades/course_id=NTU_CS101&exam_type=Winter&exam_year=2024"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("grades_status", response.json())
        self.assertEqual(response.json()["grades_status"], "FINAL")
