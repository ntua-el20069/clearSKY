import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import publish, queue_and_consume, send_request


def on_request(ch, method, props, body) -> None:  # type: ignore
    print("[.] Received request")

    response_data = send_request(body)
    publish(ch, props, method, response_data)


if __name__ == "__main__":
    queue_and_consume(queue_name="review_queue", on_request=on_request)
