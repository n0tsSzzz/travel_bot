import aio_pika
import msgpack
from aio_pika import ExchangeType
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, CallbackQuery
from aiogram import html, F, Bot
from aiogram.fsm.context import FSMContext

from .router import router
from src.states.auth import AuthGroup
from db.storages.rabbit import channel_pool
from src.handlers.utils.utils import initialize_queue, publish_starting_message

from src.keyboards.menu_kb import start_kb
from src.lexicon.lexicon_ru import LEXICON_RU

from config.settings import settings


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.set_state()
    await state.set_data({})

    async with channel_pool.acquire() as channel:  # type: aio_pika.Channel
        exchange = await channel.declare_exchange(settings.USER_EXCHANGE, ExchangeType.TOPIC, durable=True)

        items_queue = await initialize_queue(exchange, channel, settings.USER_ITEMS_QUEUE_TEMPLATE.format(user_id=message.from_user.id))
        trips_queue = await initialize_queue(exchange, channel, settings.USER_TRIPS_QUEUE_TEMPLATE.format(user_id=message.from_user.id))
        users_queue = await initialize_queue(exchange, channel, settings.USER_MESSAGES_QUEUE)

        await publish_starting_message(exchange, message)

    # await state.set_data({
    #     'button1': 1,
    #     'button2': 1,
    # })

    # # callback buttons
    # inline_btn_1 = InlineKeyboardButton(text='Первая кнопка!', callback_data='button1')
    # inline_btn_2 = InlineKeyboardButton(text='Вторая кнопка!', callback_data='button2')
    # markup = InlineKeyboardMarkup(
    #     inline_keyboard=[[inline_btn_1, inline_btn_2]]
    # )

    # button = KeyboardButton(text=START_GIFTING)
    # markup = ReplyKeyboardMarkup(keyboard=[[button]])

    # await message.answer("Клавиатура удалена.", reply_markup=ReplyKeyboardRemove())
    await message.answer(LEXICON_RU["menu"].format(user_name=message.from_user.full_name), reply_markup=start_kb())
    # await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@router.message(Command('help'))
async def command_help_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(AuthGroup.authorized)
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

# AuthGroup.authorized,
@router.message(F.text == "hi")
async def echo_handler(message: Message, state: FSMContext) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")
