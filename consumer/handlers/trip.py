import logging.config
from typing import Any

import aio_pika
import msgpack
from aio_pika import ExchangeType
from aiogram.loggers import event
from mypy.dmypy.client import action

from config.settings import settings
from consumer.logger import LOGGING_CONFIG, correlation_id_ctx, logger
from db.storages import rabbit
from db.storages.postgres import db
from db.storages.rabbit import rmq
from schema.item import Item, ItemForTrip, ItemMessage
from schema.trip import Trip, TripMessage, TripUser

logging.config.dictConfig(LOGGING_CONFIG)


async def handle_event_trip(message: Any) -> None:
    if message['action'] == 'trip_init':
        try:
            trip_id = await db.create_trip(title=message["title"], user_id=message["user_id"], days_needed=message["days_needed"])
            if trip_id is None:
                raise Exception
            trip_id = trip_id.scalar()
            if not isinstance(trip_id, int):
                raise Exception
            logger.info('Added Trip %s into db', message)
            for item in message["items"]:
                print(item)
                await db.attach_item_to_trip(item["id"], trip_id)
                logger.info('Attach Item %s to Trip %s', item, trip_id)
        except Exception as e:
            logger.exception(e)
    elif message['action'] == 'get_trips':
        try:
            not_fetched_trips = await db.get_trips(message["user_id"])
            if not_fetched_trips is None:
                raise Exception
            tuple_rows = not_fetched_trips.all()
            packed_trips = [row for row, in tuple_rows]
            if not packed_trips:
                return

            trips: list[Trip] = []
            for trip in packed_trips:
                trips_items = await db.get_trip_items(trip.id)
                if trips_items is None:
                    raise Exception
                tuple_rows = trips_items.all()
                packed_items = [row for row, in tuple_rows]

                items = []
                for item in packed_items:
                    item = Item(
                        id=item.id,
                        title=item.title,
                        user_id=item.user_id,
                        trip_id=item.trip_id
                    )
                    items.append(item)

                trip = Trip(
                    id=trip.id,
                    title=trip.title,
                    days_needed=trip.days_needed,
                    user_id=trip.user_id,
                    items=items
                )
                trips.append(trip)

            queue_name = settings.USER_TRIPS_QUEUE_TEMPLATE.format(user_id=message["user_id"])
            await rmq.purge_queue(queue_name)

            all_trips = TripUser(
                trips=trips,
            )

            await rmq.publish_message(all_trips, queue_name, correlation_id_ctx.get())
            logger.info('added Trips %s to queue', all_trips)

        except Exception as e:
            logger.error("Error processing message: %s", e)
    elif message['action'] == "delete_trip":
        try:
            await db.delete_trip(message['trip_id'])
            logger.info('Delete Trip %s', message)
        except Exception as e:
            logger.exception(e)
