import base64
import json
import os
import time
from typing import Any, Callable

import pika
import requests
from fastapi import UploadFile


def send_request(body: Any) -> dict:
    try:
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
        if body_dict["method"] == "POST":
            if "headers" in body_dict:
                response = requests.post(
                    body_dict["endpoint"], headers=body_dict["headers"]
                )
            if "json" in body_dict:
                response = requests.post(body_dict["endpoint"], json=body_dict["json"])
            else:
                response = requests.post(body_dict["endpoint"])
        elif body_dict["method"] == "GET":
            if "params" in body_dict:
                response = requests.get(
                    body_dict["endpoint"], params=body_dict["params"]
                )
            else:
                response = requests.get(body_dict["endpoint"])
        elif body_dict["method"] == "PUT":
            response = requests.put(body_dict["endpoint"], json=body_dict["json"])
        else:  # DELETE
            if "json" not in body_dict:
                response = requests.delete(body_dict["endpoint"])
            else:
                response = requests.delete(
                    body_dict["endpoint"], json=body_dict["json"]
                )

        print(f" [.] Response status code: {response.status_code}")

        try:
            content = response.json()
        except Exception:
            content = response.text

        response_data = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": content,
        }

    except Exception as e:
        response_data = {
            "status_code": 500,
            "headers": {},
            "content": {"error": f"Worker exception: {str(e)}"},
        }

    return response_data


def publish(ch: Any, props: Any, method: Any, response_data: dict) -> None:
    ch.basic_publish(
        exchange="",
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=json.dumps(response_data),
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def connect_to_rabbitmq(rabbitmq_host: str, queue_name: str) -> Any:
    while True:
        try:
            rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
            rabbitmq_pass = os.getenv("RABBITMQ_PASS", "guest")
            credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
            if rabbitmq_host == "localhost":
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=rabbitmq_host)
                )
            else:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=rabbitmq_host, heartbeat=0, credentials=credentials
                    )
                )
            return connection
        except pika.exceptions.AMQPConnectionError:
            print(
                f"Worker for queue {queue_name}: Failed to connect to RabbitMQ. Retrying in 5 seconds..."
            )
            time.sleep(5)


def queue_and_consume(queue_name: str, on_request: Callable) -> None:
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")

    connection = connect_to_rabbitmq(rabbitmq_host, queue_name)

    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=on_request)
    print(" [x] Awaiting requests")
    channel.start_consuming()


def encode_file(file: UploadFile):  # type: ignore
    content = file.file.read()
    return {
        "filename": file.filename,
        "content": base64.b64encode(content).decode(),  # base64-encode binary content
        "content_type": file.content_type,
    }


def decode_file(body):  # type: ignore
    file_info = json.loads(body)

    filename = file_info["json"]["filename"]
    content_type = file_info["json"]["content_type"]
    content_bytes = base64.b64decode(file_info["json"]["content"])

    # Construct proper multipart-form file
    files = {"file": (filename, content_bytes, content_type)}
    return files
