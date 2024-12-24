from typing import TypedDict

from .base import BaseMessage
from .item import Item, ItemMessage


class TripMessage(BaseMessage):
    title: str
    days_needed: int
    items: list[ItemMessage]
    user_id: int


class TripQueueInitMessage(BaseMessage):
    user_id: int


class Trip(TypedDict):
    id: int
    title: str
    days_needed: int
    items: list[Item]
    user_id: int


class TripUser(TypedDict):
    trips: list[Trip]


class TripDeleteMessage(BaseMessage):
    trip_id: int
