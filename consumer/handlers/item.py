from aiogram.loggers import event
from mypy.dmypy.client import action

from db.storages.postgres import db
from schema.item import ItemMessage, ItemForTrip

import logging.config
from consumer.logger import LOGGING_CONFIG, logger, correlation_id_ctx

import aio_pika
from aio_pika import ExchangeType
import msgpack

from db.storages import rabbit

from config.settings import settings

logging.config.dictConfig(LOGGING_CONFIG)

async def handle_event_item(message: ItemMessage):
    if message['action'] == 'item_create':
        try:
            await db.create_item(title=message["title"], user_id=message["user_id"])
            logger.info('Added Item %s into db', message)
        except Exception as e:
            logger.exception(e)
    elif message['action'] == 'get_items':
        try:
            not_fetched = await db.get_items(message["user_id"])
            tuple_rows = not_fetched.all()
            items = [row for row, in tuple_rows]

            async with rabbit.channel_pool.acquire() as channel:  # type: aio_pika.Channel
                exchange = await channel.declare_exchange(settings.USER_EXCHANGE, ExchangeType.TOPIC, durable=True)

                queue_name = settings.USER_ITEMS_QUEUE_TEMPLATE.format(user_id=message["user_id"])
                queue = await channel.declare_queue(queue_name, durable=True)
                await queue.purge()
                # await queue.bind(exchange, queue_name)

                for item in items:
                    item = ItemForTrip(
                        id=item.id,
                        title=item.title,
                        user_id=item.user_id,
                        action='trip_connecting',
                        event='items',
                    )
                    await exchange.publish(
                        aio_pika.Message(
                            msgpack.packb(
                                item
                            ),
                            correlation_id=correlation_id_ctx.get(),
                        ),
                        routing_key=queue_name,
                    )
                    logger.info('added Item %s to queue', item)
        except Exception as e:
            logger.error("Error processing message: %s", e)
    elif message['action'] == 'trip_connecting':
        ...
        # try:
