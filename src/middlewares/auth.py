from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.types import Message

from src.states.auth import AuthGroup


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        current_state = await data['state'].get_state()
        # print(event)
        print(current_state, '-------')
        if not current_state or current_state == AuthGroup.no_authorized:
            print(1)
            raise SkipHandler('Unauthorized')
        return await handler(event, data)