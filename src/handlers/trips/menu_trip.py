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



@router.callback_query(F.data == "trips_menu", F.message.as_("message"))
async def trips_menu_hand(callback: CallbackQuery, message: Message) -> None:
    await callback.answer()

    await message.edit_text(LEXICON_RU["trips_menu"], reply_markup=trips_menu_kb())


@router.callback_query(F.data == "menu_back", F.message.as_("message"))
async def trips_menu_back_hand(callback: CallbackQuery, state: FSMContext, message: Message) -> None:
    await callback.answer()
    data = await state.get_data()
    origin_msg = data["origin_msg"]

    await state.clear()
    await state.update_data(origin_msg=origin_msg)

    await message.edit_text(LEXICON_RU["back"], reply_markup=start_kb())
