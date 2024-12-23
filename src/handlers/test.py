from aiogram import F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.lexicon.lexicon_ru import LEXICON_RU, ERROR_LEXICON_RU
from src.keyboards.items_kb import item_create_break_kb, item_create_kb
from src.keyboards.menu_kb import start_kb
from .router import router

from .utils import check_valid_title

from src.states.item import CreateItemForm

import aio_pika
from aio_pika import ExchangeType
from db.storages.rabbit import channel_pool
from msgpack import packb
from schema.item import ItemMessage
from config.settings import settings

import logging

from aiogram.exceptions import TelegramBadRequest

async def watch_user_ad(
    user_id: int,
    msg_id: int,
    state: FSMContext,
    bot: Bot,
    db: Repository,
    current_ad_ind: int = 0
):
    usr_ads: list[Advertisement] = (await state.get_data())["usr_ads"]

    current_ad = usr_ads[current_ad_ind]
    title, photo, description, price = await db.get_ad_by_id(current_ad.advertisement_id)

    await state.update_data(
        msgs_on_delete=tuple(i for i in range(msg_id + 1, msg_id + len(photo) + 2 - (len(photo) == 1))),
    )
    caption = f"<b>Название</b>: {title}\n\n<b>Описание</b>: {description}\n\n<b>Цена</b>: {price}$"
    if len(photo) > 1:
        await bot.send_media_group(
            chat_id=user_id,
            media=[InputMediaPhoto(media=p) for p in photo],
        )
        return await bot.send_message(
            user_id, caption,
            reply_markup=mp.kb_on_user_ad_watching(len(usr_ads), current_ad_ind)
        )
    await bot.send_photo(
        user_id,
        photo[0],
        caption=caption,
        reply_markup=mp.kb_on_user_ad_watching(len(usr_ads), current_ad_ind)
    )

@router.callback_query(MainAdMenuOption.filter(F.action == "watch_own_ads"))
async def watch_own_ads(
        call: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        db: Repository
):
    await bot.delete_message(call.from_user.id, call.message.message_id)

    usr_ads = await db.get_user_ads(call.from_user.id)
    logging.info(f"User ads: {usr_ads}")
    if not usr_ads:
        return await call.message.answer("You don't have any ads", reply_markup=mp.main_menu)
    await state.set_state(WatchUserAds.on_watch)
    await state.update_data(usr_ads=usr_ads, current_ad=0)

    await watch_user_ad(user_id=call.from_user.id, msg_id=call.message.message_id, state=state, bot=bot, db=db)