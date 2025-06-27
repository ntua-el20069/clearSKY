import json
import os
import time
import uuid

import pika
from fastapi.responses import JSONResponse


def connect_to_rabbitmq(rabbitmq_host: str, queue_name: str):  # type: ignore
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


class RpcClient:
    queue_name: str
    max_retries: int = 5
    timeout: float = 5.0

    def __init__(self) -> None:
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
        self.connection = connect_to_rabbitmq(rabbitmq_host, "orchestrator-reply-queue")

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True,
        )

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body) -> None:  # type: ignore
        if self.corr_id == props.correlation_id:
            self.response = [body, props.headers]  # type: ignore

    def call(self, load: dict) -> JSONResponse:
        attempts = 0
        self.response = None

        while attempts < self.max_retries:
            self.response = None
            self.corr_id = str(uuid.uuid4())  # type: ignore
            self.channel.basic_publish(
                exchange="",
                routing_key=self.queue_name,
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                    correlation_id=self.corr_id,
                    delivery_mode=pika.DeliveryMode.Persistent,
                ),
                body=json.dumps(load),
            )

            start_time = time.time()
            while time.time() - start_time < self.timeout:
                self.connection.process_data_events(time_limit=1.0)
                if self.response is not None:
                    return self.response  # type: ignore

            attempts += 1

        return JSONResponse(
            content={
                "error": f"RPC request timed out after {attempts}/{self.max_retries} retries"
            },
            status_code=504,
        )
