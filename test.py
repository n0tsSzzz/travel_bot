import aio_pika
from aio_pika import ExchangeType
from db.storages.rabbit import channel_pool
from msgpack import packb, unpackb
from schema.item import ItemMessage, ItemQueueInitMessage
from config.settings import settings

import logging

from aiogram.exceptions import TelegramBadRequest

from aio_pika import Queue

import msgpack

from schema.user import UserMessage


async def test():
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange(settings.USER_EXCHANGE, ExchangeType.TOPIC, durable=True)
        queue_name = settings.USER_MESSAGES_QUEUE
        queue = await channel.declare_queue(queue_name, durable=True)
        await queue.bind(exchange, queue_name)

        user = UserMessage(
            user_id=1,
            username='Marko',
            event='users',
            action='register',
        )
        await exchange.publish(
            aio_pika.Message(msgpack.packb(user)),settings.USER_MESSAGES_QUEUE)

import asyncio

asyncio.run(test())