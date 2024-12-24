import aio_pika
import msgpack
from aio_pika import ExchangeType
from aiogram.types import CallbackQuery

from config.settings import settings
from db.storages.rabbit import channel_pool
from schema.item import ItemQueueInitMessage


async def init_queue(queue_name: str) -> None:
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange(settings.USER_EXCHANGE, ExchangeType.TOPIC, durable=True)
        queue = await channel.declare_queue(queue_name, durable=True)
        await queue.bind(exchange, queue_name)


async def load_queue(callback: CallbackQuery) -> None:
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange(settings.USER_EXCHANGE, ExchangeType.TOPIC, durable=True)
        queue_name = settings.USER_MESSAGES_QUEUE
        await channel.declare_queue(queue_name, durable=True)

        await exchange.publish(
            aio_pika.Message(
                msgpack.packb(
                    ItemQueueInitMessage(
                        user_id=callback.from_user.id,
                        event="items",
                        action="get_items",
                    )
                )
            ),
            queue_name,
        )
