import unittest

import mongomock
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

from review.review.app import app
from review.review.models.review import ReviewCreate, ReviewReply

client = TestClient(app)


class AddReview(unittest.TestCase):
    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def test_add_review(self) -> None:
        response = client.post(
            "/review/submit_review",
            json=ReviewCreate(
                student_id="student1",
                course_id="course1",
                exam_type="exam1",
                year=2023,
                review_text="Great course!",
            ).dict(),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "description": "Review of student student1 for (course, exam_type, year) = (course1, exam1, 2023) successfully submitted",
            },
        )

    def test_add_review_duplicate(self) -> None:
        # Add a review first
        response = client.post(
            "/review/submit_review",
            json=ReviewCreate(
                student_id="student1",
                course_id="course1",
                exam_type="exam1",
                year=2023,
                review_text="Great course!",
            ).dict(),
        )
        self.assertEqual(
            response.status_code, 200, msg="Failed to add the first review"
        )

        # Attempt to add the same review again
        response = client.post(
            "/review/submit_review",
            json=ReviewCreate(
                student_id="student1",
                course_id="course1",
                exam_type="exam1",
                year=2023,
                review_text="Great course!",
            ).dict(),
        )
        self.assertEqual(
            response.status_code, 400, msg="Failed to detect duplicate review"
        )
        self.assertEqual(
            response.json(),
            {"detail": "Review already exists for this student and exam"},
        )


class GetReviews(unittest.TestCase):
    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def test_get_reviews(self) -> None:
        # Add a review first
        response = client.post(
            "/review/submit_review",
            json=ReviewCreate(
                student_id="student1",
                course_id="course1",
                exam_type="winter",
                year=2023,
                review_text="Great course!",
            ).dict(),
        )
        self.assertEqual(
            response.status_code, 200, msg="Failed to add the first review"
        )

        # add another review
        response = client.post(
            "/review/submit_review",
            json=ReviewCreate(
                student_id="student2",
                course_id="course2",
                exam_type="winter",
                year=2023,
                review_text="Average course!",
            ).dict(),
        )
        self.assertEqual(
            response.status_code, 200, msg="Failed to add the second review"
        )

        # add review for 2025
        client.post(
            "/review/submit_review",
            json=ReviewCreate(
                student_id="student2",
                course_id="course2",
                exam_type="winter",
                year=2025,
                review_text="Poor course!",
            ).dict(),
        )

        # Get reviews
        response = client.get(
            "/review/get_reviews", params={"student_ids": ["student1"]}
        )
        self.assertEqual(response.status_code, 200)
        print(response.json())
        self.assertEqual(
            len(response.json()["reviews"]),
            1,
            msg="Found more or less than one review for student1",
        )
        self.assertEqual(
            response.json()["reviews"][0]["student_id"],
            "student1",
            msg="#1 Student ID 1 does not match",
        )

        # Test with multiple filters
        response = client.get(
            "/review/get_reviews",
            params={
                "years": [2023],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["reviews"]), 2)
        self.assertEqual(
            response.json()["reviews"][0]["student_id"],
            "student1",
            msg="#2 Student ID 1 does not match",
        )
        self.assertEqual(
            response.json()["reviews"][1]["student_id"],
            "student2",
            msg="#2 Student ID 2 does not match",
        )

        # another test
        response = client.get(
            "/review/get_reviews",
            params={
                "course_ids": ["course2"],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(response.json()["reviews"][0]["year"], 2023)
        self.assertEqual(response.json()["reviews"][0]["student_id"], "student2")
        self.assertEqual(response.json()["reviews"][1]["year"], 2025)
        self.assertEqual(response.json()["reviews"][1]["student_id"], "student2")


class ReplyReview(unittest.TestCase):
    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def test_reply_review(self) -> None:
        # Add a review first
        client.post(
            "/review/submit_review",
            json=ReviewCreate(
                student_id="student1",
                course_id="course1",
                exam_type="exam1",
                year=2023,
                review_text="Great course!",
            ).dict(),
        )

        # Reply to the review
        response = client.put(
            "/review/reply",
            json=ReviewReply(
                student_id="student1",
                course_id="course1",
                exam_type="exam1",
                year=2023,
                reply_text="Thank you for your feedback!",
            ).dict(),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "description": "Replied to the Review of student student1 for (course, exam_type, year) = (course1, exam1, 2023) successfully",
            },
        )

    def test_reply_review_not_found(self) -> None:
        # Attempt to reply to a non-existent review
        response = client.put(
            "/review/reply",
            json=ReviewReply(
                student_id="student2",  # This student has not submitted a review
                course_id="course2",
                exam_type="exam2",
                year=2024,
                reply_text="Thank you for your feedback!",
            ).dict(),
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Review not found"})
