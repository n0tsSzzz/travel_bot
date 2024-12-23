from .base import BaseMessage
from .item import ItemMessage

class TripMessage(BaseMessage):
    title: str
    days_needed: int
    items: list[ItemMessage]
    user_id: int

class TripQueueInitMessage(BaseMessage):
    user_id: int


class TripUserMessage(BaseMessage):
    trips: list[TripMessage]