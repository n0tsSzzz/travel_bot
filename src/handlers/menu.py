from aiogram import F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config.settings import settings
from db.storages.rabbit import rmq
from schema.user import UserMessage
from src.keyboards.menu_kb import start_kb
from src.lexicon.lexicon_ru import LEXICON_RU
from src.logger import get_or_create_correlation_id

from ..metrics import measure_time
from .router import router


@router.message(CommandStart(), F.from_user.id.as_("user_id"), F.from_user.full_name.as_("full_name"))
@measure_time
async def command_start_handler(message: Message, state: FSMContext, user_id: int, full_name: str) -> None:
    await state.set_state()
    await state.set_data({})

    await rmq.init_queue(settings.USER_ITEMS_QUEUE_TEMPLATE.format(user_id=user_id))
    await rmq.init_queue(settings.USER_TRIPS_QUEUE_TEMPLATE.format(user_id=user_id))

    user = UserMessage(
        user_id=user_id,
        username=full_name,
        event="users",
        action="register",
    )
    queue_name = settings.USER_MESSAGES_QUEUE

    # correlation_id = context.get(HeaderKeys.correlation_id)
    correlation_id = get_or_create_correlation_id()

    await rmq.publish_message(user, queue_name, correlation_id)
    sent_message = await message.answer(LEXICON_RU["menu"].format(user_name=full_name), reply_markup=start_kb())
    await state.update_data(origin_msg=sent_message.message_id)


@router.message(Command("help"))
@measure_time
async def command_help_handler(message: Message) -> None:
    await message.answer(LEXICON_RU["help"])
