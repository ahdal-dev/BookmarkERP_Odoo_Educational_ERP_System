"""RabbitMQ consumer for the Academic Agent microservice.

Consumes queued write events and performs the actual Odoo writes, keeping the
high-concurrency registration/petition writes off the synchronous request path.

Run: ``python worker.py``  (or ``make worker`` from services/RAG-Chatbot/)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

import agent_tools
from mq import connect, QUEUE_REGISTRATION, QUEUE_PETITION
from odoo_client import OdooError

HANDLERS = {
    QUEUE_REGISTRATION: agent_tools.process_registration_event,
    QUEUE_PETITION: agent_tools.process_petition_event,
}


def _make_callback(queue_name):
    handler = HANDLERS[queue_name]

    def _callback(ch, method, properties, body):
        try:
            payload = json.loads(body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as e:
            print(f"[worker] {queue_name}: bad message dropped ({e})")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        try:
            result = handler(payload)
            status = "ok" if result.get("ok") else "rejected"
            print(f"[worker] {queue_name} {status}: {result.get('message')}")
        except OdooError as e:
            # Business/validation error — log and ack (re-queueing won't help).
            print(f"[worker] {queue_name} Odoo error: {e}")
        except Exception as e:  # noqa: BLE001
            print(f"[worker] {queue_name} unexpected error: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    return _callback


def main():
    conn = connect()
    channel = conn.channel()
    for q in (QUEUE_REGISTRATION, QUEUE_PETITION):
        channel.queue_declare(queue=q, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=q, on_message_callback=_make_callback(q))
    print(f"[worker] waiting on queues: {QUEUE_REGISTRATION}, {QUEUE_PETITION} (CTRL+C to stop)")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("[worker] stopping...")
        channel.stop_consuming()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
