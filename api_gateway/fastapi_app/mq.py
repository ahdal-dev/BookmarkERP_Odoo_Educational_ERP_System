"""
RabbitMQ producer scaffold for the API gateway (next-phase readiness).

This mirrors ``services/RAG-Chatbot/Backend/mq.py``. It is intentionally NOT
wired into any hot path yet — it exists so the upcoming async-messaging phase
can move blocking work (emails, mailbox provisioning, notification fan-out,
waitlist promotion, grade posting) off the request path with a one-line
``publish_event(...)`` call plus a worker consumer.

Design: durable queues, persistent messages, graceful fallback. If the broker
is unreachable or ``ENABLE_MQ`` is off, ``try_publish`` returns False and the
caller continues synchronously — messaging never breaks a request.
"""
import json
import logging
import os

try:
    import pika
except ImportError:  # pika is optional when MQ is disabled
    pika = None

logger = logging.getLogger(__name__)

AMQP_URL = os.getenv("AMQP_URL", "amqp://guest:guest@rabbitmq:5672/")
_SOCKET_TIMEOUT = float(os.getenv("AMQP_TIMEOUT", "5"))

# Planned queues (== routing keys on the default exchange) for the next phase.
QUEUE_NOTIFICATION = "notification.created"
QUEUE_ADMISSION_EMAIL = "admission.email"
QUEUE_ADMISSION_MAILBOX = "admission.mailbox"
QUEUE_WAITLIST_PROMOTION = "waitlist.promotion"
QUEUE_GRADE_POSTED = "grade.posted"
QUEUES = (
    QUEUE_NOTIFICATION, QUEUE_ADMISSION_EMAIL, QUEUE_ADMISSION_MAILBOX,
    QUEUE_WAITLIST_PROMOTION, QUEUE_GRADE_POSTED,
)


class MQUnavailable(Exception):
    """Broker unreachable — callers fall back to synchronous handling."""


def mq_enabled() -> bool:
    return os.getenv("ENABLE_MQ", "false").strip().lower() in ("1", "true", "yes", "on")


def _connect():
    if pika is None:
        raise MQUnavailable("pika is not installed")
    params = pika.URLParameters(AMQP_URL)
    params.socket_timeout = _SOCKET_TIMEOUT
    params.blocked_connection_timeout = _SOCKET_TIMEOUT
    try:
        return pika.BlockingConnection(params)
    except Exception as e:  # noqa: BLE001
        raise MQUnavailable(str(e))


def publish_event(routing_key: str, payload: dict) -> None:
    """Publish a durable JSON message. Raises MQUnavailable if the broker is down."""
    conn = _connect()
    try:
        channel = conn.channel()
        for q in QUEUES:
            channel.queue_declare(queue=q, durable=True)
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


def try_publish(routing_key: str, payload: dict) -> bool:
    """Best-effort publish. Returns True if queued, False if MQ is off/unavailable
    so the caller can proceed synchronously. Never raises."""
    if not mq_enabled():
        return False
    try:
        publish_event(routing_key, payload)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.debug("MQ publish skipped (%s): %s", routing_key, exc)
        return False
