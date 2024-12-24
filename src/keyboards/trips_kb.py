from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

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
            callback_data=TripItemCallback(action = "add").pack(),
        ),
        InlineKeyboardButton(
            text=KB_LEXICON_RU["trip_item_next"],
            callback_data=TripItemCallback(action = "next").pack(),
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
            callback_data=TripItemCallback(action = "last").pack(),
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



def kb_on_user_trip_watching(all_trips_len: int, current_num: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    two_btns_required = (0 < current_num < all_trips_len - 1)

    if current_num == 0 and all_trips_len != 1:
        builder.button(text=KB_LEXICON_RU["next"], callback_data="usr_trip_watch:next")
    elif (current_num == all_trips_len - 1) and all_trips_len != 1:
        builder.button(text=KB_LEXICON_RU["prev"], callback_data="usr_trip_watch:prev")
    elif two_btns_required:
        builder.button(text=KB_LEXICON_RU["prev"], callback_data="usr_trip_watch:prev")
        builder.button(text=KB_LEXICON_RU["next"], callback_data="usr_trip_watch:next")

    builder.button(text=KB_LEXICON_RU["trip_items_show"], callback_data="items_mine")
    builder.button(text=KB_LEXICON_RU["trip_remove"], callback_data="delete_trip")

    builder.button(text=KB_LEXICON_RU["main_menu"], callback_data="main_menu")
    if all_trips_len == 1:
        builder.adjust(2, 1)
    else:
        builder.adjust(1 + two_btns_required, 2, 1)
    return builder.as_markup()