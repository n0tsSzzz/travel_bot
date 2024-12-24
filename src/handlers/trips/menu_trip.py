from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.handlers.router import router
from src.keyboards.menu_kb import start_kb
from src.keyboards.trips_kb import trips_menu_kb
from src.lexicon.lexicon_ru import LEXICON_RU


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
