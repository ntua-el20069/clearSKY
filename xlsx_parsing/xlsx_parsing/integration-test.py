import sys

import requests

examples = [
    "example-excels/clearSKY data example 1 basic.xlsx",
    "example-excels/clearSKY data example 2 detailed.xlsx",
    "example-excels/clearSKY-question3.xlsx",
]

ind = int(sys.argv[1]) if len(sys.argv) > 1 else 0
response = requests.post(
    "http://localhost:8003/xlsx_parsing/parse_grades",
    files={"file": open(examples[ind], "rb")},
)
if response.status_code == 200:
    response = requests.post(
        "http://localhost:8004/grades/add_grades",
        json=response.json()["result"]["data"],
    )
    print(response.json())
else:
    print("Error:", response.status_code, response.text)
