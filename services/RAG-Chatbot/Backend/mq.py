"""Minimal RabbitMQ helper for the Academic Agent microservice.

Used to offload high-concurrency write actions (course registration attempts and
petition submissions) from the synchronous request path. The publisher is used by
``agent_tools``; the consumer lives in ``worker.py``.

Kept deliberately small: durable queues, persistent messages, no DLQ/retry.
"""
import json
import os

try:
    import pika
except ImportError:  # pika is optional when MQ is disabled (ENABLE_MQ=false)
    pika = None

AMQP_URL = os.getenv("AMQP_URL", "amqp://guest:guest@localhost:5672/")

# Queue (== routing key on the default exchange) per event type.
QUEUE_REGISTRATION = "registration.attempt"
QUEUE_PETITION = "petition.submitted"
QUEUES = (QUEUE_REGISTRATION, QUEUE_PETITION)

_SOCKET_TIMEOUT = float(os.getenv("AMQP_TIMEOUT", "5"))


class MQUnavailable(Exception):
    """Raised when the broker can't be reached, so callers can fall back to a
    synchronous write instead of failing the user's request."""


def mq_enabled() -> bool:
    return os.getenv("ENABLE_MQ", "true").strip().lower() in ("1", "true", "yes", "on")


def connect():
    if pika is None:
        raise MQUnavailable("pika is not installed")
    params = pika.URLParameters(AMQP_URL)
    params.socket_timeout = _SOCKET_TIMEOUT
    params.blocked_connection_timeout = _SOCKET_TIMEOUT
    try:
        return pika.BlockingConnection(params)
    except Exception as e:  # noqa: BLE001 - normalize all connection failures
        raise MQUnavailable(str(e))


def _declare(channel) -> None:
    for q in QUEUES:
        channel.queue_declare(queue=q, durable=True)


def publish_event(routing_key: str, payload: dict) -> None:
    """Publish a durable JSON message. Raises MQUnavailable if the broker is down."""
    conn = connect()
    try:
        channel = conn.channel()
        _declare(channel)
        channel.basic_publish(
            exchange="",
            routing_key=routing_key,
            body=json.dumps(payload, default=str).encode("utf-8"),
            properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
        )
    finally:
        try:
            conn.close()
        except Exception:  # noqa: BLE001
            pass
