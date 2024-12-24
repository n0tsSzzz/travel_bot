from typing import TypedDict

from .base import BaseMessage


class Item(TypedDict):
    id: int
    title: str
    user_id: int
    trip_id: int | None

class ItemMessage(BaseMessage):
    title: str
    user_id: int


class ItemQueueInitMessage(BaseMessage):
    user_id: int


class ItemForTrip(BaseMessage):
    id: int
    title: str
    user_id: int