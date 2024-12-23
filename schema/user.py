from .base import BaseMessage


class UserMessage(BaseMessage):
    user_id: int
    username: str