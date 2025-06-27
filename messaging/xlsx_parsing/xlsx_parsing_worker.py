import json
import os
import sys

import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import decode_file, publish, queue_and_consume


def on_request(ch, method, props, body) -> None:  # type: ignore
    print(" [.] Received request")

    body_dict = json.loads(body)
    hostname = os.getenv("RESPONSIBLE_HOST", "localhost")
    if hostname != "localhost":
        body_dict["endpoint"] = (
            body_dict["endpoint"]
            .replace("localhost", hostname)
            .replace("127.0.0.1", hostname)
        )
    print(
        f" [.] Sending request to {body_dict['endpoint']} with method {body_dict['method']}"
    )

    files = decode_file(body)

    try:
        response = requests.post(body_dict["endpoint"], files=files)
        print(f" [.] Response status code: {response.status_code}")
        response_data = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.json(),
        }
    except Exception as e:
        response_data = {
            "status_code": 500,
            "headers": {},
            "content": {"error": f"Worker exception: {str(e)}"},
        }

    publish(ch, props, method, response_data)


if __name__ == "__main__":
    queue_and_consume(queue_name="xlsx_parsing_queue", on_request=on_request)
