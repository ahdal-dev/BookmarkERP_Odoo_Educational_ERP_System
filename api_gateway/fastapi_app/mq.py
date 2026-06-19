"""
RabbitMQ async producer/consumer for the API gateway.

Uses aio_pika (async-native) to match the FastAPI async architecture.
The module-level _mq_connection is set by the lifespan hook in main.py.

Design: durable queues, persistent messages, graceful fallback. If the broker
is unreachable or ENABLE_MQ is off, try_publish returns False and the caller
continues synchronously — messaging never breaks a request.
"""
import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

AMQP_URL = os.getenv("AMQP_URL", "amqp://guest:guest@rabbitmq:5672/")

# Planned queues (== routing keys on the default exchange).
QUEUE_NOTIFICATION = "notification.created"
QUEUE_ADMISSION_EMAIL = "admission.email"
QUEUE_ADMISSION_MAILBOX = "admission.mailbox"
QUEUE_WAITLIST_PROMOTION = "waitlist.promotion"
QUEUE_GRADE_POSTED = "grade.posted"
QUEUES = (
    QUEUE_NOTIFICATION, QUEUE_ADMISSION_EMAIL, QUEUE_ADMISSION_MAILBOX,
    QUEUE_WAITLIST_PROMOTION, QUEUE_GRADE_POSTED,
)

# Set by the lifespan hook; None means MQ is off or unavailable.
_mq_connection = None


def mq_enabled() -> bool:
    return os.getenv("ENABLE_MQ", "false").strip().lower() in ("1", "true", "yes", "on")


async def connect_mq():
    """Create a RobustConnection (auto-reconnects on transient broker failures)."""
    import aio_pika
    return await aio_pika.connect_robust(AMQP_URL)


async def try_publish(routing_key: str, payload: dict) -> bool:
    """Best-effort async publish. Returns True if queued, False if MQ is off/unavailable.
    Never raises — the caller always continues synchronously on False."""
    if not mq_enabled() or _mq_connection is None:
        return False
    try:
        import aio_pika
        async with _mq_connection.channel() as channel:
            await channel.declare_queue(routing_key, durable=True)
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(payload, default=str).encode("utf-8"),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    content_type="application/json",
                ),
                routing_key=routing_key,
            )
        return True
    except Exception as exc:
        logger.debug("MQ publish skipped (%s): %s", routing_key, exc)
        return False
