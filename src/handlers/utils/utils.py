# utils.py
import re

import aio_pika
import msgpack
from aio_pika import ExchangeType
from aiogram.types import CallbackQuery
from msgpack import packb

from db.storages.rabbit import channel_pool
from schema.item import ItemQueueInitMessage
from schema.user import UserMessage
from config.settings import settings

from src.lexicon.lexicon_ru import ERROR_LEXICON_RU


FORBIDDEN_CHARS: tuple[str, ...] = ('_', '@', '/', "\\", '-', '+', '[', ']', '|')

no_numbers_regex = re.compile(r"^[^0-9]*$")
only_digits_regex = re.compile(r"^\d+$")



async def initialize_queue(exchange, channel, queue_name):
    queue = await channel.declare_queue(queue_name, durable=True)

    await queue.bind(
        exchange,
        queue_name
    )

    return queue


async def publish_starting_message(exchange, message):
    user = UserMessage(
        user_id=message.from_user.id,
        username=message.from_user.full_name,
        event='users',
        action='register',
    )

    await exchange.publish(
        aio_pika.Message(packb(user)),
        settings.USER_MESSAGES_QUEUE
    )

def check_valid_msg(text: str) -> tuple[str | None, ...]:
    if any(ch in text for ch in FORBIDDEN_CHARS):
        return None, ERROR_LEXICON_RU["incorrect_format"] + ERROR_LEXICON_RU["prohibited_symbol"] + repr(FORBIDDEN_CHARS)
    return text, None


def check_valid_title(text: str):
    _, exc_msg = check_valid_msg(text)
    if exc_msg:
        return None, exc_msg

    if not bool(no_numbers_regex.match(text)):
        return None, ERROR_LEXICON_RU["incorrect_format"] + ERROR_LEXICON_RU["is_digits"]

    if not 2 <= len(text) <= 40:
        return None, ERROR_LEXICON_RU["incorrect_format"] + ERROR_LEXICON_RU["length_val"]
    return text, None


def check_valid_days(text: str):
    _, exc_msg = check_valid_msg(text)
    if exc_msg:
        return None, exc_msg

    if not bool(only_digits_regex.match(text)):
        return None, ERROR_LEXICON_RU["incorrect_format"] + ERROR_LEXICON_RU["not_digit"]

    return text, None

async def load_queue(callback: CallbackQuery):
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange(settings.USER_EXCHANGE, ExchangeType.TOPIC, durable=True)
        queue_name = settings.USER_MESSAGES_QUEUE
        await channel.declare_queue(queue_name, durable=True)

        await exchange.publish(
            aio_pika.Message(msgpack.packb(
                ItemQueueInitMessage(
                    user_id=callback.from_user.id,
                    event='items',
                    action='get_items',
                )
            )),
        queue_name)