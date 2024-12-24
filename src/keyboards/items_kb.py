from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from src.lexicon.lexicon_ru import KB_LEXICON_RU


def item_create_kb() -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["item_create"],
            callback_data="item_create",
        ),
    )

    return kb_builder.as_markup()


def item_create_break_kb() -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["cancel"],
            callback_data="item_create_break",
        ),
    )
    return kb_builder.as_markup()


def kb_on_user_item_watching(all_items_len: int, current_num: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    two_btns_required = (0 < current_num < all_items_len - 1)

    if current_num == 0 and all_items_len != 1:
        builder.button(text=KB_LEXICON_RU["next"], callback_data='usr_item_watch:next')
    elif (current_num == all_items_len - 1) and all_items_len != 1:
        builder.button(text=KB_LEXICON_RU["prev"], callback_data='usr_item_watch:prev')
    elif two_btns_required:
        builder.button(text=KB_LEXICON_RU["prev"], callback_data='usr_item_watch:prev')
        builder.button(text=KB_LEXICON_RU["next"], callback_data='usr_item_watch:next')


    builder.button(text=KB_LEXICON_RU["main_menu"], callback_data='trip_items_menu')
    if all_items_len == 1:
        builder.adjust(2, 1)
    else:
        builder.adjust(1 + two_btns_required, 2, 1)
    return builder.as_markup()