import msgpack
from aiogram import Bot, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from starlette_context import context
from starlette_context.header_keys import HeaderKeys

from config.settings import settings
from db.storages.rabbit import rmq
from schema.trip import TripDeleteMessage, TripQueueInitMessage
from src.handlers.router import router
from src.handlers.utils.watching import watch_user_trips
from src.keyboards.trips_kb import trips_menu_kb
from src.lexicon.lexicon_ru import ERROR_LEXICON_RU, LEXICON_RU
from src.logger import correlation_id_ctx, get_or_create_correlation_id, logger


@router.callback_query(F.data == "trips_mine", F.message.as_("message"))
async def usr_trips_watch_hand(callback: CallbackQuery, state: FSMContext, message: Message) -> None:
    await callback.answer()

    user_id, data = callback.from_user.id, await state.get_data()
    origin_msg = data["origin_msg"]
    queue_name = settings.USER_MESSAGES_QUEUE

    trip = TripQueueInitMessage(
        user_id=callback.from_user.id,
        event="trip",
        action="get_trips",
    )

    correlation_id = get_or_create_correlation_id()
    await rmq.publish_message(trip, queue_name, correlation_id)
    user_trips_queue = settings.USER_TRIPS_QUEUE_TEMPLATE.format(user_id=user_id)

    result = await rmq.await_objects(user_trips_queue)
    if result:
        trips = await rmq.get_obj(user_trips_queue)
        if trips.correlation_id is not None:
            correlation_id_ctx.set(trips.correlation_id)
        parsed_trips = msgpack.unpackb(trips.body)
        logger.info("get trips %s", parsed_trips)

        await state.update_data(usr_trips=parsed_trips, current_trip=0)

        await watch_user_trips(state, message)
        return
    await state.clear()
    await state.update_data(origin_msg=origin_msg)
    try:
        await message.edit_text(ERROR_LEXICON_RU["no_trips"], reply_markup=trips_menu_kb())
        return
    except TelegramBadRequest:
        pass


@router.callback_query(F.data.startswith("usr_trip_watch"), F.message.as_("message"), F.data.as_("callback_data"))
async def trip_watch_hand(callback: CallbackQuery, state: FSMContext, message: Message, callback_data: str) -> None:
    await callback.answer()

    data = await state.get_data()
    data["current_trip"] += [1, -1][callback_data.split(":")[1] == "prev"]

    await state.set_data(data)
    await watch_user_trips(state, message, data["current_trip"])


@router.callback_query(F.data == "main_menu", F.message.as_("message"))
async def trip_create_break_hand(callback: CallbackQuery, state: FSMContext, message: Message) -> None:
    await callback.answer()

    data = await state.get_data()
    origin_msg = data["origin_msg"]

    await state.clear()
    await state.update_data(origin_msg=origin_msg)
    await message.edit_text(LEXICON_RU["back"], reply_markup=trips_menu_kb())


@router.callback_query(F.data == "delete_trip", F.message.as_("message"))
async def delete_trip_hand(callback: CallbackQuery, state: FSMContext, message: Message) -> None:
    await callback.answer()

    data = await state.get_data()
    origin_msg = data["origin_msg"]
    queue_name = settings.USER_MESSAGES_QUEUE
    trip_id = data["usr_trips"]["trips"][data["current_trip"]]["id"]
    trip = TripDeleteMessage(trip_id=trip_id, event="trip", action="delete_trip")

    correlation_id = get_or_create_correlation_id()
    await rmq.publish_message(trip, queue_name, correlation_id)

    await state.clear()
    await state.update_data(origin_msg=origin_msg)
    await message.edit_text(LEXICON_RU["trip_deleted"], reply_markup=trips_menu_kb())
