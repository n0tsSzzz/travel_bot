from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from src.lexicon.lexicon_ru import KB_LEXICON_RU


def trips_menu_kb() -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb_builder.max_width = 2

    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["trip_create"],
            callback_data="trip_create",
        ),
        InlineKeyboardButton(
            text=KB_LEXICON_RU["trips_mine"],
            callback_data="trips_mine",
        ),
        InlineKeyboardButton(
            text=KB_LEXICON_RU["back"],
            callback_data="menu_back",
        )
    )

    return kb_builder.as_markup()


class TripItemCallback(CallbackData, prefix="trip_item"):
    action: str

def trip_items_create_kb() -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["trip_item_add"],
            callback_data=TripItemCallback(action = 'add').pack(),
        ),
        InlineKeyboardButton(
            text=KB_LEXICON_RU["trip_item_next"],
            callback_data=TripItemCallback(action = 'next').pack(),
        )
    )
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["trip_finish"],
            callback_data="trip_finish",
        )
    )
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["cancel"],
            callback_data="trip_create_break",
        )
    )

    return kb_builder.as_markup()


def trip_items_create_last_kb() -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["trip_item_add"],
            callback_data=TripItemCallback(action = 'last').pack(),
        )
    )
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["trip_finish"],
            callback_data="trip_finish",
        )
    )
    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["cancel"],
            callback_data="trip_create_break",
        )
    )

    return kb_builder.as_markup()


def trip_create_break_kb() -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    kb_builder.row(
        InlineKeyboardButton(
            text=KB_LEXICON_RU["cancel"],
            callback_data="trip_create_break",
        ),
    )

    return kb_builder.as_markup()



def kb_on_user_ad_watching(all_ads_len, current_num):
    builder = InlineKeyboardBuilder()
    two_btns_required = (0 < current_num < all_ads_len - 1)

    if current_num == 0 and all_ads_len != 1:
        builder.button(text='➡️', callback_data='usr_ad_watch:next')
    elif (current_num == all_ads_len - 1) and all_ads_len != 1:
        builder.button(text='⬅️', callback_data='usr_ad_watch:prev')
    elif two_btns_required:
        builder.button(text='⬅️', callback_data='usr_ad_watch:prev')
        builder.button(text='➡️', callback_data='usr_ad_watch:next')

    builder.button(text='🖋Изменить', callback_data='edit_ad')
    builder.button(text='🗑Удалить', callback_data='delete_ad')

    builder.button(text='В главное меню', callback_data='back-to_advertisement_menu')
    if all_ads_len == 1:
        builder.adjust(2, 1)
    else:
        builder.adjust(1 + two_btns_required, 2, 1)
    return builder.as_markup()