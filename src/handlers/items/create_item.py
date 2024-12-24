from aiogram import F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from starlette_context import context
from starlette_context.header_keys import HeaderKeys

from src.lexicon.lexicon_ru import LEXICON_RU, ERROR_LEXICON_RU
from src.keyboards.items_kb import item_create_break_kb, item_create_kb
from src.keyboards.menu_kb import start_kb
from src.handlers.router import router

from src.handlers.utils.validator import check_valid_title

from src.states.item import CreateItemForm

from src.logger import correlation_id_ctx

import aio_pika
from aio_pika import ExchangeType
from db.storages.rabbit import channel_pool
from msgpack import packb
from schema.item import ItemMessage
from config.settings import settings

import logging

from aiogram.exceptions import TelegramBadRequest

from db.storages.rabbit import rmq


@router.callback_query(F.data == "item_create", F.message.as_("message"))
async def item_create_hand(callback: CallbackQuery, state: FSMContext, message: Message) -> None:
    await callback.answer()

    await state.set_state(CreateItemForm.title)

    await message.edit_text(LEXICON_RU["item_create"], reply_markup=item_create_break_kb())


@router.message(CreateItemForm.title, F.text.as_("text"), F.from_user.id.as_("user_id"))
async def item_title_hand(message: Message, state: FSMContext, bot: Bot, text: str, user_id: int) -> None:
    data = await state.get_data()

    await message.delete()
    origin_msg = data["origin_msg"]

    title, exc_msg = check_valid_title(text)
    try:
        if exc_msg:
            await bot.edit_message_text(
                text=exc_msg,
                reply_markup=item_create_break_kb(),
                chat_id=user_id,
                message_id=origin_msg
            )
            return
    except TelegramBadRequest:
        return

    data.update(title=title)

    item = ItemMessage(
        title=data['title'],
        user_id=user_id,
        event='items',
        action='item_create',
    )

    queue_name = settings.USER_MESSAGES_QUEUE
    correlation_id = context.get(HeaderKeys.correlation_id) or ""
    await rmq.publish_message(item, queue_name, correlation_id)

    await state.clear()
    await state.update_data(origin_msg=origin_msg)
    await bot.edit_message_text(
        chat_id=user_id,
        message_id=data["origin_msg"],
        text=LEXICON_RU["item_result"],
        reply_markup=start_kb()
    )


@router.callback_query(F.data == "item_create_break", F.message.as_("message"))
async def item_create_break_hand(callback: CallbackQuery, state: FSMContext, message: Message) -> None:
    await callback.answer()

    data = await state.get_data()
    origin_msg = data["origin_msg"]

    await state.clear()
    await state.update_data(origin_msg=origin_msg)
    await message.edit_text(LEXICON_RU["item_cancel"], reply_markup=start_kb())
