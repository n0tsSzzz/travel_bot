import asyncio

from aiogram import Bot, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from starlette_context import context
from starlette_context.header_keys import HeaderKeys

from config.settings import settings
from db.storages.rabbit import rmq
from schema.item import Item, ItemQueueInitMessage
from schema.trip import TripMessage
from src.handlers.router import router
from src.handlers.utils.select_items_for_trip import select_items
from src.handlers.utils.validator import check_valid_title
from src.keyboards.menu_kb import start_kb
from src.keyboards.trips_kb import TripItemCallback, trip_create_break_kb, trips_menu_kb
from src.lexicon.lexicon_ru import ERROR_LEXICON_RU, LEXICON_RU
from src.states.trip import CreateTripForm


@router.callback_query(F.data == "trip_create", F.message.as_("message"))
async def trip_create_hand(callback: CallbackQuery, state: FSMContext, message: Message) -> None:
    await callback.answer()

    data = await state.get_data()
    origin_msg = data["origin_msg"]

    item = ItemQueueInitMessage(
        user_id=callback.from_user.id,
        event="items",
        action="get_items",
    )

    queue_name = settings.USER_MESSAGES_QUEUE
    correlation_id = context.get(HeaderKeys.correlation_id) or ""
    asyncio.create_task(rmq.publish_message(item, queue_name, correlation_id))
    user_items_queue = settings.USER_ITEMS_QUEUE_TEMPLATE.format(user_id=callback.from_user.id)
    result = await rmq.await_objects(user_items_queue)

    if result:
        await state.set_state(CreateTripForm.title)
        await message.edit_text(LEXICON_RU["trip_create"], reply_markup=trip_create_break_kb())
        return

    await state.clear()
    await state.update_data(origin_msg=origin_msg)

    await message.edit_text(ERROR_LEXICON_RU["no_items"], reply_markup=start_kb())
    return


@router.message(CreateTripForm.title, F.text.as_("text"), F.from_user.id.as_("user_id"))
async def trip_title_hand(message: Message, state: FSMContext, bot: Bot, text: str, user_id: int) -> None:
    data = await state.get_data()

    await message.delete()
    title, exc_msg = check_valid_title(text)
    try:
        if exc_msg:
            await bot.edit_message_text(
                text=exc_msg, reply_markup=trip_create_break_kb(), chat_id=user_id, message_id=data["origin_msg"]
            )
            return
    except TelegramBadRequest:
        return

    await state.update_data(title=title)

    await state.set_state(CreateTripForm.days)
    await bot.edit_message_text(
        text=LEXICON_RU["trip_days_create"],
        reply_markup=trip_create_break_kb(),
        chat_id=user_id,
        message_id=data["origin_msg"],
    )
    return


@router.message(
    CreateTripForm.days, F.text.isdigit() & ~F.text.startswith("0") & (F.text.cast(int) > 0), F.text.as_("msg_text")
)
async def trip_days_hand(message: Message, state: FSMContext, bot: Bot, msg_text: str) -> None:
    await message.delete()

    await state.update_data(days_needed=int(msg_text))
    await state.set_state(CreateTripForm.items)
    await select_items(message, state, bot)


@router.message(CreateTripForm.days, F.from_user.id.as_("user_id"))
async def trip_days_invalid_hand(message: Message, state: FSMContext, bot: Bot, user_id: int) -> None:
    await message.delete()

    data = await state.get_data()
    origin_msg = data["origin_msg"]

    try:
        await bot.edit_message_text(
            text=ERROR_LEXICON_RU["incorrect_format"] + ERROR_LEXICON_RU["days_val"],
            reply_markup=trip_create_break_kb(),
            chat_id=user_id,
            message_id=origin_msg,
        )
        return
    except TelegramBadRequest:
        return


@router.callback_query(CreateTripForm.items, TripItemCallback.filter())
async def trip_items_hand(
    callback: CallbackQuery, callback_data: TripItemCallback, state: FSMContext, bot: Bot
) -> None:
    await callback.answer()

    data = await state.get_data()
    choose_item = data["choose_item"]
    try:
        items: list[Item] = data["items"]
    except KeyError:
        items = []

    if callback_data.action == "add" or callback_data.action == "last":
        if items:
            items.append(choose_item)
        else:
            items = [choose_item]
        await state.update_data(items=items)
    await select_items(callback, state, bot)


@router.callback_query(F.data == "trip_finish", F.message.as_("message"))
async def trip_finish_hand(callback: CallbackQuery, state: FSMContext, message: Message) -> None:
    await callback.answer()

    data = await state.get_data()
    origin_msg = data["origin_msg"]
    try:
        items = data["items"]
    except KeyError:
        await state.clear()
        await state.update_data(origin_msg=origin_msg)
        await message.edit_text(ERROR_LEXICON_RU["no_items"], reply_markup=trips_menu_kb())
        return

    trip = TripMessage(
        user_id=callback.from_user.id,
        title=data["title"],
        days_needed=data["days_needed"],
        items=items,
        event="trip",
        action="trip_init",
    )

    queue_name = settings.USER_MESSAGES_QUEUE
    correlation_id = context.get(HeaderKeys.correlation_id) or ""
    await rmq.publish_message(trip, queue_name, correlation_id)

    await state.clear()
    await state.update_data(origin_msg=origin_msg)
    await message.edit_text(text=LEXICON_RU["trip_finish"], reply_markup=trips_menu_kb())


@router.callback_query(F.data == "trip_create_break", F.message.as_("message"))
async def trip_create_break_hand(callback: CallbackQuery, state: FSMContext, message: Message) -> None:
    await callback.answer()

    data = await state.get_data()
    origin_msg = data["origin_msg"]

    await state.clear()
    await state.update_data(origin_msg=origin_msg)
    await message.edit_text(LEXICON_RU["trip_cancel"], reply_markup=trips_menu_kb())
