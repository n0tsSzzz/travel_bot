import msgpack
from aio_pika.exceptions import QueueEmpty
from aiogram import F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from schema.trip import TripUserMessage, TripQueueInitMessage
from src.keyboards.trips_kb import trips_menu_kb
from src.lexicon.lexicon_ru import LEXICON_RU, ERROR_LEXICON_RU
from src.keyboards.items_kb import item_create_break_kb, item_create_kb
from src.keyboards.menu_kb import start_kb
from src.handlers.router import router

from src.handlers.utils.utils import check_valid_title

from src.states.item import CreateItemForm

import aio_pika
from aio_pika import ExchangeType
from db.storages.rabbit import channel_pool
from msgpack import packb
from schema.item import ItemMessage
from config.settings import settings

import logging

from aiogram.exceptions import TelegramBadRequest
from src.handlers.utils.watching import watch_user_ad

from src.logger import logger


@router.callback_query(F.data == "trips_mine")
async def usr_ad_watch(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
):
    await callback.answer()


    user_id, data = callback.from_user.id, await state.get_data()
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange(settings.USER_EXCHANGE, ExchangeType.TOPIC, durable=True)
        queue_name = settings.USER_MESSAGES_QUEUE

        await exchange.publish(
            aio_pika.Message(msgpack.packb(
                TripQueueInitMessage(
                    user_id=callback.from_user.id,
                    event='trip',
                    action='get_trips',
                )
            )),
            queue_name)

        user_trips_queue = await channel.declare_queue(settings.USER_TRIPS_QUEUE_TEMPLATE.format(user_id=user_id), durable=True)
        try:
            trips = await user_trips_queue.get()
            parsed_item: TripUserMessage = msgpack.unpackb(trips.body)
            logger.info('get item %s', parsed_item)
            data["current_trip"] += [1, -1][callback.data.split(":")[1] == "prev"]

            await state.set_data(data)
            await watch_user_ad(user_id, call.message.message_id, state, bot, data["current_ad"])
        except QueueEmpty:
            await state.clear()
            await callback.message.edit_text(ERROR_LEXICON_RU['no_trips'], reply_markup=trips_menu_kb())