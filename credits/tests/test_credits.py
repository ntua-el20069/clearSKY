import unittest

import mongomock
from credits.app import app
from credits.models.models import Credits
from fastapi.testclient import TestClient
from mongoengine import connect, disconnect

client = TestClient(app)


class AddCredits(unittest.TestCase):
    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def test_add_credits_no_error(self) -> None:
        added_credits = {
            "institution": "National Technical University of Athens",
            "credits": 100,
        }
        response = client.post("/credits/add_credits", json=added_credits)
        self.assertEqual(response.status_code, 200)
        check_credit = Credits.objects(
            institution="National Technical University of Athens"
        ).first()
        self.assertEqual(check_credit.credits, 100)

        added_credits = {"institution": "uni_1", "credits": 150}
        response = client.post("/credits/add_credits", json=added_credits)
        self.assertEqual(response.status_code, 200)
        check_credit = Credits.objects(institution="uni_1").first()
        self.assertEqual(check_credit.credits, 150)

        added_credits = {"institution": "uni_1", "credits": 150}
        response = client.post("/credits/add_credits", json=added_credits)
        self.assertEqual(response.status_code, 200)
        check_credit = Credits.objects(institution="uni_1").first()
        self.assertEqual(check_credit.credits, 300)


class RemoveCredits(unittest.TestCase):

    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def test_remove_credits_no_error(self) -> None:
        added_credits = {"institution": "uni_1", "credits": 300}
        response = client.post("/credits/add_credits", json=added_credits)
        self.assertEqual(response.status_code, 200)

        remove_credits = {"institution": "uni_1", "credits": 100}

        response = client.request("PUT", "/credits/remove_credits", json=remove_credits)
        self.assertEqual(response.status_code, 200)
        check_credit = Credits.objects(institution="uni_1").first()
        self.assertEqual(check_credit.credits, 200)

    def test_remove_credits_error(self) -> None:
        added_credits = {"institution": "uni_1", "credits": 300}
        response = client.post("/credits/add_credits", json=added_credits)
        self.assertEqual(response.status_code, 200)

        remove_credits = {"institution": "uni_1", "credits": 400}
        response = client.request("PUT", "/credits/remove_credits", json=remove_credits)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["detail"],
            "Can't remove 400 amount of credits from uni_1 institution",
        )

        remove_credits = {"institution": "uni_2", "credits": 1.0}
        response = client.request("PUT", "/credits/remove_credits", json=remove_credits)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Institution: uni_2 not found")


class GetCredits(unittest.TestCase):

    def setUp(self) -> None:
        disconnect()
        connect(
            "mongoenginetest",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    def tearDown(self) -> None:
        disconnect()

    def test_get_credits_no_error(self) -> None:
        added_credits = {"institution": "uni_1", "credits": 300}
        response = client.post("/credits/add_credits", json=added_credits)
        self.assertEqual(response.status_code, 200)

        response = client.get("/credits/get_credits?institution=uni_1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["credits"], 300)

        remove_credits = {"institution": "uni_1", "credits": 150}
        response = client.request("PUT", "/credits/remove_credits", json=remove_credits)
        self.assertEqual(response.status_code, 200)

        response = client.get("/credits/get_credits?institution=uni_1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["credits"], 150)
