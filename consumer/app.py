import logging.config
from typing import Any

import aio_pika
import msgpack

from config.settings import settings
from consumer.handlers.item import handle_event_item
from consumer.handlers.trip import handle_event_trip
from consumer.handlers.user import handle_event_user
from consumer.logger import LOGGING_CONFIG, correlation_id_ctx, logger
from db.storages import rabbit

# from consumer.metrics import TOTAL_RECEIVED_MESSAGES


async def start_consumer() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)
    logger.info("Starting consumer...")

    channel: aio_pika.Channel
    async with rabbit.channel_pool.acquire() as channel:
        await channel.set_qos(prefetch_count=10)

        queue = await channel.declare_queue(settings.USER_MESSAGES_QUEUE, durable=True)

        logger.info("Consumer started!")
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:  # type: aio_pika.abc.AbstractIncomingMessage
                # TOTAL_RECEIVED_MESSAGES.inc()
                if message.correlation_id is not None:
                    correlation_id_ctx.set(message.correlation_id)

                body: Any = msgpack.unpackb(message.body)
                logger.info("Message: %s", body)

                try:
                    if body.get("event") == "users":
                        await handle_event_user(body)
                    elif body.get("event") == "items":
                        await handle_event_item(body)
                    elif body.get("event") == "trip":
                        await handle_event_trip(body)

                    await message.ack()
                except Exception as e:
                    logger.error("Error processing message: %s", e)
                    await message.reject(requeue=False)
