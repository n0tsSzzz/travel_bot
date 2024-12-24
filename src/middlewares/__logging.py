import logging
from typing import Any, Awaitable, Callable, Union

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery], # type: ignore[override]
        data: dict[str, Any],
    ) -> Any:
        user_id: int = event.from_user.id if isinstance(event, CallbackQuery) else event.chat.id
        user_name: str = event.from_user.full_name if event.from_user else "Unknown User"
        user_message = event.data if isinstance(event, CallbackQuery) else event.text
        state: FSMContext = data["state"]
        state_data: dict[str, Any] = await state.get_data()

        logger.info(
            '{ "user": %s, "name": %s, message: "%s", "state": { "context" : %s, "data": %s }',
            user_id,
            user_name,
            user_message,
            await state.get_state(),
            state_data
        )

        await handler(event, data)
