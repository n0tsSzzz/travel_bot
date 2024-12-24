from aiogram import Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.handlers.router import router
from src.handlers.utils.watching import watch_user_items
from src.keyboards.trips_kb import kb_on_user_trip_watching
from src.lexicon.lexicon_ru import LEXICON_RU


@router.callback_query(F.data == "items_mine", F.message.as_("message"))
async def usr_items_watch_hand(callback: CallbackQuery, state: FSMContext, bot: Bot, message: Message) -> None:
    await callback.answer()

    user_id, data = callback.from_user.id, await state.get_data()
    items = data["usr_trips"]["trips"][data["current_trip"]]["items"]

    await state.update_data(usr_items=items, current_item=0)
    await watch_user_items(callback, user_id, message.message_id, state, bot)


@router.callback_query(F.data.startswith("usr_item_watch"), F.message.as_("message"), F.data.as_("callback_data"))
async def item_watch_hand(
    callback: CallbackQuery, state: FSMContext, bot: Bot, message: Message, callback_data: str
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
    await message.edit_text(
        text=LEXICON_RU["trip_info"].format(title=title, days_needed=days_needed),
        reply_markup=kb_on_user_trip_watching(len(data["usr_trips"]["trips"]), data["current_trip"]),
    )
