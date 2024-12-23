import aio_pika
from aio_pika import Queue, ExchangeType
from aio_pika.exceptions import QueueEmpty
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from msgpack import packb

from db.storages.rabbit import channel_pool
from config.settings import settings
import msgpack

from schema.item import ItemForTrip
from schema.trip import TripMessage
from src.keyboards.menu_kb import start_kb
from src.lexicon.lexicon_ru import LEXICON_RU, ERROR_LEXICON_RU
from aiogram import Bot

from src.keyboards.trips_kb import trip_items_create_kb, trip_items_create_last_kb, trips_menu_kb
import asyncio

from src.logger import logger


async def select_items(text_type: Message | CallbackQuery, state: FSMContext):
    # text_type = text_type.message if isinstance(text_type, CallbackQuery) else text_type


    # await callback.message.delete_reply_markup()
    async with channel_pool.acquire() as channel:  # type: aio_pika.Channel
        exchange = await channel.declare_exchange(settings.USER_EXCHANGE, ExchangeType.TOPIC, durable=True)

        queue: Queue = await channel.declare_queue(
            settings.USER_ITEMS_QUEUE_TEMPLATE.format(user_id=text_type.from_user.id),
                durable=True,
            )


        retries = 1
        for _ in range(retries):
            try:
                item = await queue.get()
                parsed_item: ItemForTrip | None = msgpack.unpackb(item.body)
                logger.info('get item %s', parsed_item)
                await item.ack()

                data = await state.get_data()
                await state.update_data(choose_item=parsed_item)


                if isinstance(text_type, Message):

                    print('-----------------------------')
                    await text_type.answer(
                        text=LEXICON_RU["trip_items_create"].format(title=parsed_item["title"]),
                        reply_markup=trip_items_create_last_kb() if queue.declaration_result.message_count == 1 else trip_items_create_kb(),
                    )
                else:
                    print('++++++++++++++++++++++++++++++++++++++++')
                    await text_type.message.edit_text(
                        text=LEXICON_RU["trip_items_create"].format(title=parsed_item["title"]),
                        reply_markup=trip_items_create_last_kb() if queue.declaration_result.message_count == 1 else trip_items_create_kb(),
                    )
                return
            except QueueEmpty:
                data = await state.get_data()
                items = data["items"]

                queue_name = settings.USER_MESSAGES_QUEUE
                await channel.declare_queue(queue_name, durable=True)

                await exchange.publish(
                    aio_pika.Message(msgpack.packb(
                        TripMessage(
                            user_id=text_type.from_user.id,
                            title=data["title"],
                            days_needed=data["days_needed"],
                            items=items,
                            event='trip',
                            action='trip_init',
                        )
                    )),
                    queue_name)

                await state.clear()
                await text_type.message.edit_text(text=LEXICON_RU["trip_finish"], reply_markup=trips_menu_kb())
