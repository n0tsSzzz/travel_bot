import asyncio
from pyexpat.errors import messages

import msgpack
from aiogram import F, Bot
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.sql.selectable import SelectState

from src.bg_tasks import background_tasks
from src.keyboards.items_kb import item_create_break_kb
from src.lexicon.lexicon_ru import LEXICON_RU, ERROR_LEXICON_RU
from src.keyboards.trips_kb import trips_menu_kb, trip_create_break_kb, trip_items_create_kb, TripItemCallback
from src.keyboards.menu_kb import start_kb
from src.handlers.router import router

from src.handlers.utils.utils import check_valid_title, load_queue
from src.logger import logger

from src.states.trip import CreateTripForm


import aio_pika
from aio_pika import ExchangeType
from db.storages.rabbit import channel_pool
from msgpack import packb, unpackb
from schema.item import ItemMessage, ItemQueueInitMessage, ItemForTrip
from schema.trip import TripMessage, TripQueueInitMessage
from config.settings import settings

import logging

from aiogram.exceptions import TelegramBadRequest

from aio_pika import Queue

from src.handlers.utils.select_items_for_trip import select_items


@router.callback_query(F.data == "trips_menu")
async def trips_menu_hand(callback: CallbackQuery):
    await callback.answer()

    await callback.message.edit_text(LEXICON_RU["trips_menu"], reply_markup=trips_menu_kb())

    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange(settings.USER_EXCHANGE, ExchangeType.TOPIC, durable=True)
        queue_name = settings.USER_MESSAGES_QUEUE
        queue = await channel.declare_queue(queue_name, durable=True)
        await queue.bind(exchange, queue_name)


@router.callback_query(F.data == "menu_back")
async def trips_menu_back_hand(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.clear()
    await callback.message.edit_text(LEXICON_RU["back"], reply_markup=start_kb())


# async def _check_queue_state(queue_name, channel):
#     async with channel:
#         for _ in range(10):
#             logger.info(queue_name.declaration_result.message_count)
#             try:
#                 item = await queue_name.get()
#                 parsed_item = msgpack.unpackb(item.body)
#                 logger.info('item is %s', parsed_item)
#             except Exception as e:
#                 logger.error(e)
#             if queue_name.declaration_result.message_count > 0:
#                 return True
#             await asyncio.sleep(1)
#         return False

@router.callback_query(F.data == "trip_create")
async def trip_create_hand(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(msg_on_delete=callback.message.message_id)

    asyncio.create_task(load_queue(callback))


    async with channel_pool.acquire() as channel:

        # items_available = await _check_queue_state(user_items_queue, channel)
        for _ in range(3):
            user_items_queue = await channel.declare_queue(
                settings.USER_ITEMS_QUEUE_TEMPLATE.format(user_id=callback.from_user.id), durable=True)

            if user_items_queue.declaration_result.message_count > 0:
                await state.set_state(CreateTripForm.title)
                return await callback.message.edit_text(LEXICON_RU["trip_create"], reply_markup=trip_create_break_kb())
            await asyncio.sleep(0.1)

        await state.clear()
        return await callback.message.edit_text(ERROR_LEXICON_RU['no_items'], reply_markup=start_kb())



@router.message(CreateTripForm.title, F.text)
async def trip_title_hand(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    title, exc_msg = check_valid_title(message.text)
    if exc_msg:
        await state.update_data(msg_on_delete=message.message_id + 1)
        return await message.answer(
            exc_msg,
            reply_markup=(trip_create_break_kb())
        )

    try:
        await bot.delete_message(message.from_user.id, data["msg_on_delete"])
    except TelegramBadRequest:
        pass

    await state.update_data(title=title, msg_on_delete=message.message_id + 1)

    await state.set_state(CreateTripForm.days)
    return await message.answer(LEXICON_RU["trip_days_create"],
                            reply_markup=trip_create_break_kb())


@router.message(CreateTripForm.days, F.text.isdigit() & ~F.text.startswith('0') & (F.text.cast(int) > 0))
async def trip_days_hand(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(days_needed=int(message.text))
    form_data = await state.get_data()
    try:
        await bot.delete_message(message.from_user.id, form_data["msg_on_delete"])
    except TelegramBadRequest:
        pass
    await state.set_state(CreateTripForm.items)
    await select_items(message, state)
    # await message.answer(LEXICON_RU["trip_items_create"], reply_markup=trip_items_create_kb())


@router.message(CreateTripForm.days)
async def trip_days_invalid_hand(message: Message, state: FSMContext):
    await state.update_data(msg_on_delete=message.message_id + 1)

    await message.answer(
        ERROR_LEXICON_RU["incorrect_format"] + ERROR_LEXICON_RU["days_val"],
        reply_markup=trip_create_break_kb()
    )



@router.callback_query(CreateTripForm.items, TripItemCallback.filter())
async def trip_items_hand(callback: CallbackQuery, callback_data: TripItemCallback, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    choose_item = data["choose_item"]
    try:
        items: list[ItemForTrip] = data["items"]
    except KeyError:
        items = []

    if callback_data.action == 'add' or callback_data.action == 'last':
        if items:
            items.append(choose_item)
        else:
            items = [choose_item]
        await state.update_data(items=items)
    await select_items(callback, state)


@router.callback_query(F.data == 'trip_finish')
async def trip_finish_hand(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    try:
        items = data["items"]
    except KeyError:
        await state.clear()
        return await callback.message.edit_text(ERROR_LEXICON_RU['no_items'], reply_markup=trips_menu_kb())

    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange(settings.USER_EXCHANGE, ExchangeType.TOPIC, durable=True)
        queue_name = settings.USER_MESSAGES_QUEUE
        await channel.declare_queue(queue_name, durable=True)

        await exchange.publish(
            aio_pika.Message(msgpack.packb(
                TripMessage(
                    user_id=callback.from_user.id,
                    title=data["title"],
                    days_needed=data["days_needed"],
                    items=items,
                    event='trip',
                    action='trip_init',
                )
            )),
            queue_name)

    await state.clear()
    await callback.message.edit_text(text=LEXICON_RU["trip_finish"], reply_markup=trips_menu_kb())

@router.callback_query(F.data == "trip_create_break")
async def trip_create_break_hand(callback: CallbackQuery, state: FSMContext):

    await state.clear()
    await callback.message.edit_text(LEXICON_RU["trip_cancel"], reply_markup=trips_menu_kb())
