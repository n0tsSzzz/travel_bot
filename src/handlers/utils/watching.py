from typing import Any

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram.fsm.context import FSMContext

from src.keyboards.items_kb import kb_on_user_item_watching
from src.keyboards.trips_kb import kb_on_user_trip_watching
from src.lexicon.lexicon_ru import LEXICON_RU


async def watch_user_trips(
    callback: CallbackQuery,
    user_id: int,
    msg_id: int,
    state: FSMContext,
    bot: Bot,
    current_trip_ind: int = 0
) -> None:
    usr_trips: dict[str, Any] = (await state.get_data())["usr_trips"]
    current_trip = usr_trips["trips"][current_trip_ind]
    title = current_trip["title"]
    days_needed = current_trip["days_needed"]

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            text=LEXICON_RU["trip_info"].format(title=title, days_needed=days_needed),
            reply_markup=kb_on_user_trip_watching(len(usr_trips["trips"]), current_trip_ind)
        )

async def watch_user_items(
    callback: CallbackQuery,
    user_id: int,
    msg_id: int,
    state: FSMContext,
    bot: Bot,
    current_item_ind: int = 0
) -> None:
    usr_items: dict[Any, str] = (await state.get_data())["usr_items"]
    current_item = usr_items[current_item_ind]
    if isinstance(current_item, dict):
        title = current_item["title"]
    else:
        title = None

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            text=LEXICON_RU["item_info"].format(title=title),
            reply_markup=kb_on_user_item_watching(len(usr_items), current_item_ind)
        )