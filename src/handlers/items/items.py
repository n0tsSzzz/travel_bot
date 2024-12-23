from aiogram import F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

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


@router.callback_query(F.data == "item_create")
async def item_create_hand(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(CreateItemForm.title)
    await state.update_data(msg_on_delete=callback.message.message_id)

    await callback.message.edit_text(LEXICON_RU["item_create"], reply_markup=item_create_break_kb())


@router.message(CreateItemForm.title, F.text)
async def item_title_hand(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    title, exc_msg = check_valid_title(message.text)
    if exc_msg:
        await state.update_data(msg_on_delete=message.message_id + 1)
        return await message.answer(
            exc_msg,
            reply_markup=item_create_break_kb()
        )

    try:
        await bot.delete_message(message.from_user.id, data["msg_on_delete"])
    except TelegramBadRequest:
        pass

    await state.update_data(title=title, msg_on_delete=message.message_id + 1)

    form_data = await state.get_data()

    try:
        del form_data["msg_on_delete"]

        async with channel_pool.acquire() as channel:  # type: aio_pika.Channel
            exchange = await channel.declare_exchange(settings.USER_EXCHANGE, ExchangeType.TOPIC, durable=True)

            await exchange.publish(
                aio_pika.Message(
                    packb(
                        ItemMessage(
                            **form_data,
                            user_id=message.from_user.id,
                            event='items',
                            action='item_create',
                        )
                    ),
                ),
                settings.USER_MESSAGES_QUEUE,
            )
    except Exception as e:
        await state.clear()
        await message.answer('Ошибка!!!')
        logging.exception(e)

    await state.clear()
    await message.answer(LEXICON_RU["item_result"], reply_markup=start_kb())


@router.callback_query(F.data == "item_create_break")
async def item_create_break_hand(callback: CallbackQuery, state: FSMContext):

    await state.clear()
    await callback.message.edit_text(LEXICON_RU["item_cancel"], reply_markup=start_kb())
