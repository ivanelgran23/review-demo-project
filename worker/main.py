import json
import logging
import time
from uuid import UUID

import pika

from common.config import settings
from common.db import init_db, session_scope
from common.crud import get_review, set_review_status
from worker.moderation import moderate_text
from common.models import ReviewStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_message(ch, method, _properties, body):
    try:
        payload = json.loads(body.decode())
        review_id = UUID(payload["review_id"])
    except Exception as exc:  # noqa: BLE001
        logger.error("Invalid message %s: %s", body, exc)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    try:
        with session_scope() as db:
            review = get_review(db, review_id)
            if not review:
                logger.warning("Review %s not found", review_id)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            status, reason = moderate_text(review.text)
            set_review_status(db, review_id, status, reason=reason)
            logger.info(
                "Review %s moderation -> %s (%s)",
                review_id,
                status.value,
                reason or "approved",
            )
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to process review %s: %s", review_id, exc)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main():
    init_db()
    credentials = pika.PlainCredentials(settings.rabbit_user, settings.rabbit_password)
    params = pika.ConnectionParameters(
        host=settings.rabbit_host,
        port=settings.rabbit_port,
        credentials=credentials,
        heartbeat=30,
    )
    while True:
        try:
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue=settings.rabbit_queue, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue=settings.rabbit_queue, on_message_callback=handle_message
            )
            logger.info("Worker listening on queue %s", settings.rabbit_queue)
            channel.start_consuming()
        except Exception:  # noqa: BLE001
            logger.warning("Cannot connect to RabbitMQ, retrying in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    main()
