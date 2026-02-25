import json
import logging

import pika

from common.config import settings

logger = logging.getLogger(__name__)


def _connection() -> pika.BlockingConnection:
    credentials = pika.PlainCredentials(settings.rabbit_user, settings.rabbit_password)
    params = pika.ConnectionParameters(
        host=settings.rabbit_host,
        port=settings.rabbit_port,
        credentials=credentials,
        heartbeat=30,
    )
    return pika.BlockingConnection(params)


def publish_review_task(review_id: str) -> None:
    """Send review id to moderation queue."""
    connection = _connection()
    channel = connection.channel()
    channel.queue_declare(queue=settings.rabbit_queue, durable=True)
    body = json.dumps({"review_id": review_id})
    channel.basic_publish(
        exchange="",
        routing_key=settings.rabbit_queue,
        body=body,
        properties=pika.BasicProperties(delivery_mode=2),  # make message persistent
    )
    logger.info("Published review %s for moderation", review_id)
    connection.close()
