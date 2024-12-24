import msgpack
from aio_pika.exceptions import QueueEmpty
from aiogram import F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from starlette_context import context
from starlette_context.header_keys import HeaderKeys

from schema.trip import TripQueueInitMessage, TripDeleteMessage
from src.keyboards.trips_kb import trips_menu_kb, kb_on_user_trip_watching
from src.lexicon.lexicon_ru import LEXICON_RU, ERROR_LEXICON_RU
from src.keyboards.items_kb import item_create_break_kb, item_create_kb
from src.keyboards.menu_kb import start_kb
from src.handlers.router import router

from aiogram.exceptions import TelegramBadRequest

from src.handlers.utils.validator import check_valid_title

from src.states.item import CreateItemForm

import aio_pika
from aio_pika import ExchangeType
from db.storages.rabbit import channel_pool
from msgpack import packb
from schema.item import ItemMessage
from config.settings import settings

import logging

from aiogram.exceptions import TelegramBadRequest, TelegramAPIError
from src.handlers.utils.watching import watch_user_items

from src.logger import logger, correlation_id_ctx

from db.storages.rabbit import rmq


@router.callback_query(F.data == "items_mine", F.message.as_("message"))
async def usr_items_watch_hand(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    message: Message
) -> None:
    await callback.answer()

    user_id, data = callback.from_user.id, await state.get_data()
    items = data["usr_trips"]["trips"][data["current_trip"]]['items']

    await state.update_data(usr_items=items, current_item=0)
    await watch_user_items(callback, user_id, message.message_id, state, bot)


@router.callback_query(F.data.startswith("usr_item_watch"), F.message.as_("message"), F.message.as_("callback_data"))
async def item_watch_hand(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    message: Message,
    callback_data: str
) -> None:
    await callback.answer()

    user_id, data = callback.from_user.id, await state.get_data()
    data["current_item"] += [1, -1][callback_data.split(":")[1] == "prev"]

    await state.set_data(data)
    await watch_user_items(callback, user_id, message.message_id, state, bot, data["current_item"])


@router.callback_query(F.data == "trip_items_menu", F.message.as_("message"))
async def trip_create_break_hand(callback: CallbackQuery, state: FSMContext, message: Message) -> None:
    await callback.answer()

    data = await state.get_data()
    current_trip = data["usr_trips"]["trips"][data["current_trip"]]
    title = current_trip["title"]
    days_needed = current_trip["days_needed"]
    await message.edit_text(text=LEXICON_RU["trip_info"].format(title=title, days_needed=days_needed),
          reply_markup=kb_on_user_trip_watching(len(data["usr_trips"]["trips"]), data["current_trip"])
    )
