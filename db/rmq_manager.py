import asyncio
import logging
from typing import Any

import aio_pika
from aio_pika import Channel, ExchangeType
from aio_pika.abc import AbstractIncomingMessage
from aio_pika.pool import Pool
from msgpack import packb

from config.settings import settings

logger = logging.getLogger(__name__)


class RMQManager:
    def __init__(self, pool: Pool[Channel]):
        self._channel_pool = pool
        logging.info("Successfully connected to rabbitmq!")

    async def init_queue(self, queue_name: str) -> None:
        async with self._channel_pool.acquire() as channel:  # type: aio_pika.Channel
            exchange = await channel.declare_exchange(settings.USER_EXCHANGE, ExchangeType.TOPIC, durable=True)
            queue = await channel.declare_queue(queue_name, durable=True)
            await queue.bind(exchange, queue_name)

    async def publish_message(self, message: Any, queue_name: str, correlation_id: str) -> None:
        async with self._channel_pool.acquire() as channel:  # type: aio_pika.Channel
            exchange = await channel.declare_exchange(settings.USER_EXCHANGE, ExchangeType.TOPIC, durable=True)

            await exchange.publish(
                aio_pika.Message(packb(message), correlation_id=correlation_id),
                queue_name,
            )

    async def purge_queue(self, queue_name: str) -> None:
        async with self._channel_pool.acquire() as channel:  # type: aio_pika.Channel
            queue = await channel.declare_queue(queue_name, durable=True)
            await queue.purge()

    async def await_objects(self, queue_name: str) -> bool:
        async with self._channel_pool.acquire() as channel:  # type: aio_pika.Channel
            for _ in range(3):
                queue = await channel.declare_queue(queue_name, durable=True)
                messages_count: int = queue.declaration_result.message_count or 0
                if messages_count > 0:
                    return True
                await asyncio.sleep(0.1)
            return False

    async def get_obj(self, queue_name: str) -> AbstractIncomingMessage:
        async with self._channel_pool.acquire() as channel:  # type: aio_pika.Channel
            queue = await channel.declare_queue(queue_name, durable=True)
            obj = await queue.get()
            await obj.ack()
            return obj

    async def quantity_messages(self, queue_name: str) -> int | None:
        async with self._channel_pool.acquire() as channel:
            queue = await channel.declare_queue(queue_name, durable=True)
            return queue.declaration_result.message_count
