from aiogram.loggers import event

from db.storages.postgres import db
from schema.item import ItemMessage, ItemForTrip, Item

import logging.config
from consumer.logger import LOGGING_CONFIG, logger, correlation_id_ctx

import aio_pika
from aio_pika import ExchangeType
import msgpack

from db.storages import rabbit

from db.storages.rabbit import rmq

from config.settings import settings

logging.config.dictConfig(LOGGING_CONFIG)

async def handle_event_item(message: ItemMessage) -> None:
    if message['action'] == 'item_create':
        try:
            await db.create_item(title=message["title"], user_id=message["user_id"])
            logger.info('Added Item %s into db', message)
        except Exception as e:
            logger.exception(e)
    elif message['action'] == 'get_items':
        try:
            not_fetched = await db.get_items(message["user_id"])
            if not_fetched is None:
                raise Exception
            tuple_rows = not_fetched.all()
            items = [row for row, in tuple_rows]

            queue_name = settings.USER_ITEMS_QUEUE_TEMPLATE.format(user_id=message["user_id"])
            await rmq.purge_queue(queue_name)

            for item in items:
                item = Item(
                    id=item.id,
                    title=item.title,
                    user_id=item.user_id,
                    trip_id=None
                )

                await rmq.publish_message(item, queue_name, correlation_id_ctx.get())
                logger.info('added Item %s to queue', item)

        except Exception as e:
            logger.error("Error processing message: %s", e)
