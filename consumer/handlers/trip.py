from aiogram.loggers import event
from mypy.dmypy.client import action

from db.storages.postgres import db
from schema.item import ItemMessage, ItemForTrip
from schema.trip import TripMessage, TripUserMessage

import logging.config
from consumer.logger import LOGGING_CONFIG, logger, correlation_id_ctx

import aio_pika
from aio_pika import ExchangeType
import msgpack

from db.storages import rabbit

from config.settings import settings

logging.config.dictConfig(LOGGING_CONFIG)


async def handle_event_trip(message: TripMessage):
    if message['action'] == 'trip_init':
        try:
            trip_id = await db.create_trip(title=message["title"], user_id=message["user_id"], days_needed=message["days_needed"])
            trip_id = trip_id.scalar()
            logger.info('Added Trip %s into db', message)
            for item in message["items"]:
                print(item)
                await db.attach_item_to_trip(item["id"], trip_id)
                logger.info('Attach Item %s to Trip %s', item, trip_id)
        except Exception as e:
            logger.exception(e)
    elif message['action'] == 'get_trips':
        try:
            not_fetched = await db.get_trips(message["user_id"])
            tuple_rows = not_fetched.all()
            trips = [row for row, in tuple_rows]
            async with rabbit.channel_pool.acquire() as channel:  # type: aio_pika.Channel
                exchange = await channel.declare_exchange(settings.USER_EXCHANGE, ExchangeType.TOPIC, durable=True)

                queue_name = settings.USER_TRIPS_QUEUE_TEMPLATE.format(user_id=message["user_id"])
                queue = await channel.declare_queue(queue_name, durable=True)
                await queue.purge()

                trips = TripUserMessage(
                    trips=trips
                )
                await exchange.publish(
                    aio_pika.Message(
                        msgpack.packb(
                            trips
                        ),
                        correlation_id=correlation_id_ctx.get(),
                    ),
                    routing_key=queue_name,
                )
        except Exception as e:
            logger.error("Error processing message: %s", e)
