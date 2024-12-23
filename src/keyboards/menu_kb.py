from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from src.lexicon.lexicon_ru import KB_LEXICON_RU

def start_kb() -> InlineKeyboardMarkup:
    """
    Build a starting keyboard.
    """

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["item_create"],
            callback_data="item_create",
        ),
        InlineKeyboardButton(
            text=KB_LEXICON_RU["trips_menu"],
            callback_data="trips_menu",
        ),
    )
    return kb_builder.as_markup()