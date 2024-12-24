import aio_pika
from aio_pika import Queue, ExchangeType
from aio_pika.exceptions import QueueEmpty
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from msgpack import packb
from starlette_context import context
from starlette_context.header_keys import HeaderKeys

from db.storages.rabbit import channel_pool
from config.settings import settings
import msgpack

from schema.item import ItemForTrip, Item
from schema.trip import TripMessage
from src.keyboards.menu_kb import start_kb
from src.lexicon.lexicon_ru import LEXICON_RU, ERROR_LEXICON_RU
from aiogram import Bot

from src.keyboards.trips_kb import trip_items_create_kb, trip_items_create_last_kb, trips_menu_kb
import asyncio

from src.logger import logger, correlation_id_ctx
from db.storages.rabbit import rmq


async def select_items(update: Message | CallbackQuery, state: FSMContext, bot: Bot) -> None:
    if update is not None and isinstance(update, (Message, CallbackQuery)):
        if update.from_user is not None:
            user_id = update.from_user.id

        items_queue = settings.USER_ITEMS_QUEUE_TEMPLATE.format(user_id=user_id)

        retries = 1
        for _ in range(retries):
            try:
                item = await rmq.get_obj(items_queue)
                if item.correlation_id is not None:
                    correlation_id_ctx.set(item.correlation_id)
                parsed_item: Item | None = msgpack.unpackb(item.body)
                if parsed_item is not None:
                    logger.info('get item %s', parsed_item)

                    data = await state.get_data()
                    await state.update_data(choose_item=parsed_item)
                    quantity_messages = await rmq.quantity_messages(items_queue)

                    if isinstance(update, Message):
                        await bot.edit_message_text(
                            text=LEXICON_RU["trip_items_create"].format(title=parsed_item["title"]),
                            reply_markup=trip_items_create_last_kb() if quantity_messages == 0 else trip_items_create_kb(),
                            chat_id=user_id,
                            message_id=data["origin_msg"]
                        )
                    else:
                        if isinstance(update.message, Message):
                            await update.message.edit_text(
                                text=LEXICON_RU["trip_items_create"].format(title=parsed_item["title"]),
                                reply_markup=trip_items_create_last_kb() if quantity_messages == 0 else trip_items_create_kb(),
                            )
                        return
            except QueueEmpty:
                data = await state.get_data()
                origin_msg = data["origin_msg"]
                items = data["items"]

                trip = TripMessage(
                    user_id=user_id,
                    title=data["title"],
                    days_needed=data["days_needed"],
                    items=items,
                    event='trip',
                    action='trip_init',
                )
                queue_name = settings.USER_MESSAGES_QUEUE
                await rmq.publish_message(trip, queue_name, context.get(HeaderKeys.correlation_id) or "")

                await state.clear()
                await state.update_data(origin_msg=origin_msg)
                if isinstance(update, CallbackQuery) and (isinstance(update.message, Message)):
                    await update.message.edit_text(text=LEXICON_RU["trip_finish"], reply_markup=trips_menu_kb())
