import unittest

from fastapi.testclient import TestClient

from xlsx_parsing.xlsx_parsing.app import app  # CHANGE this line depending on workdir

client = TestClient(app)

examples = [
    "example-excels/clearSKY data example 1 basic.xlsx",
    "example-excels/clearSKY data example 2 detailed.xlsx",
    "example-excels/clearSKY-question3.xlsx",
]

invalid_file = "app.py"

invalid_examples = [
    "invalid-excels/clearSKY data invalid 1 basic.xlsx",
    "invalid-excels/clearSKY data invalid 2 basic.xlsx",
]


warning_examples = [
    "warning-excels/clearSKY data warning 2 detailed.xlsx",
    "warning-excels/clearSKY-warning-question3.xlsx",
]

base_path = "xlsx_parsing/"


class TestParse(unittest.TestCase):
    def test_parse(self) -> None:
        # Test the parsing endpoint with a sample Excel file
        for xlsx_file in examples:
            with open(base_path + xlsx_file, "rb") as f:
                response = client.post("/xlsx_parsing/parse_grades", files={"file": f})
                print(f"####### {response.json()} {response.status_code} ############")
                self.assertEqual(
                    response.status_code, 200, f"Failed for file: {xlsx_file}"
                )
                json_response = response.json()
                self.assertIn(
                    "result",
                    json_response,
                    f"Missing 'result' key in response for file: {xlsx_file}",
                )
                self.assertIsInstance(
                    json_response["result"],
                    dict,
                    f"Result is not a dict for file: {xlsx_file}",
                )
                self.assertGreater(
                    len(json_response["result"]),
                    0,
                    f"Empty result for file: {xlsx_file}",
                )

    def test_invalid_file(self) -> None:
        # Test with an invalid file type
        with open(base_path + invalid_file, "rb") as f:
            response = client.post("/xlsx_parsing/parse_grades", files={"file": f})
            self.assertEqual(
                response.status_code,
                415,
                f"Unexpected status code for invalid file: {invalid_file}",
            )
            json_response = response.json()
            self.assertIn(
                "detail",
                json_response,
                f"Missing 'detail' key in response for file: {invalid_file}",
            )
            self.assertIn(
                "error",
                json_response["detail"],
                f"Missing 'error' key in detail for file: {invalid_file}",
            )
            self.assertEqual(
                json_response["detail"]["error"],
                "Only Excel files (.xlsx) are allowed",
                f"Unexpected error message for file: {invalid_file}",
            )

    def test_invalid_examples(self) -> None:
        # Test the parsing endpoint with invalid Excel files
        for xlsx_file in invalid_examples:
            with open(base_path + xlsx_file, "rb") as f:
                response = client.post("/xlsx_parsing/parse_grades", files={"file": f})
                self.assertEqual(
                    response.status_code,
                    400,
                    f"Unexpected status code for invalid Excel: {xlsx_file}",
                )
                json_response = response.json()
                self.assertIn(
                    "error",
                    json_response,
                    f"Missing 'error' key in detail for file: {xlsx_file}",
                )
                self.assertGreater(
                    len(json_response["error"]),
                    0,
                    f"Empty error message for file: {xlsx_file}",
                )

    def test_warnings(self) -> None:
        # Test the parsing endpoint with warning Excel files
        for xlsx_file in warning_examples:
            with open(base_path + xlsx_file, "rb") as f:
                response = client.post("/xlsx_parsing/parse_grades", files={"file": f})
                self.assertEqual(
                    response.status_code,
                    200,
                    f"Unexpected status code for warning Excel: {xlsx_file}",
                )
                json_response = response.json()
                self.assertIn(
                    "warning",
                    json_response,
                    f"Missing 'warning' key in response for file: {xlsx_file}",
                )
                self.assertGreater(
                    len(json_response["warning"]),
                    0,
                    f"Empty warning message for file: {xlsx_file}",
                )
                self.assertIn(
                    "result",
                    json_response,
                    f"Missing 'result' key in response for file: {xlsx_file}",
                )
                self.assertIsInstance(
                    json_response["result"],
                    dict,
                    f"Result is not a dict for file: {xlsx_file}",
                )
                self.assertGreater(
                    len(json_response["result"]),
                    0,
                    f"Empty result for file: {xlsx_file}",
                )

    def test_parse_enrolled_students(self) -> None:
        # Test the parsing endpoint with a sample Excel file
        for xlsx_file in examples:
            with open(base_path + xlsx_file, "rb") as f:
                response = client.post(
                    "/xlsx_parsing/parse_enrolled_students", files={"file": f}
                )
                print(f"####### {response.json()} {response.status_code} ############")
                self.assertEqual(
                    response.status_code,
                    200,
                    f"Failed for file: {xlsx_file}",
                )
                json_response = response.json()
                self.assertIn(
                    "result",
                    json_response,
                    f"Missing 'result' key in response for file: {xlsx_file}",
                )
                self.assertIsInstance(
                    json_response["result"],
                    dict,
                    f"Result is not a dict for file: {xlsx_file}",
                )
                self.assertGreater(
                    len(json_response["result"]),
                    0,
                    f"Empty result for file: {xlsx_file}",
                )
