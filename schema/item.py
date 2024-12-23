from datetime import datetime

from pydantic import BaseModel

from typing import TypedDict

class ItemBase(BaseModel):
    name: str
    days_needed: int
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


from .base import BaseMessage


class ItemMessage(BaseMessage):
    title: str
    user_id: int


class ItemQueueInitMessage(BaseMessage):
    user_id: int


class ItemForTrip(BaseMessage):
    id: int
    title: str
    user_id: int