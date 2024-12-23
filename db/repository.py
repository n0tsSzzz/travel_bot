import logging

from sqlalchemy import select, insert, update

from typing import Callable
from sqlalchemy.exc import DBAPIError

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.result import ChunkedIteratorResult

from db.models import User, Item, Trip
from schema.item import ItemMessage

logger = logging.getLogger(__name__)

class Repository:
    __slots__ = ('_session_pool',)

    def __init__(self, pool):
        self._session_pool = pool
        logging.info("Successfully connected to database!")

    async def _request_to_db(self, func: Callable, query: str) -> ChunkedIteratorResult:
        async with self._session_pool() as session:
            try:
                res = await (getattr(session, func.__name__))(query)
                await session.commit()

                return res
            except DBAPIError as e:
                logger.error(f'Db error: {e}')
                await session.rollback()

    async def add_user(self, user_id, username):
        await self._request_to_db(
            AsyncSession.execute,
            insert(User).
            values(
                user_id=user_id,
                username=username
            )
        )

    async def user_exists(self, user_id):
        return await self._request_to_db(
            AsyncSession.scalar,
            select(User.user_id).
            where(User.user_id == user_id)
        )

    async def create_item(
            self,
            title: str,
            user_id: int,
    ):
        await self._request_to_db(
            AsyncSession.execute,
            insert(Item)
            .values(
                title=title,
                user_id=user_id
            )
        )

    async def get_items(self, user_id: int):
        return await self._request_to_db(
            AsyncSession.execute,
            select(Item).
            where(Item.user_id == user_id).
            where(Item.trip_id.is_(None))
        )

    async def create_trip(self, user_id: int, title: str, days_needed: int):
        return await self._request_to_db(
            AsyncSession.execute,
            insert(Trip)
            .values(
                user_id=user_id,
                title=title,
                days_needed=days_needed,
            )
            .returning(Trip.id)
        )

    async def attach_item_to_trip(self, item_id: int, trip_id: int):
        await self._request_to_db(
            AsyncSession.execute,
            update(Item).
            where(Item.id == item_id).
            values(trip_id=trip_id)
        )

    async def get_trips(self, user_id: int):
        return await self._request_to_db(
            AsyncSession.execute,
            select(Trip).
            where(Trip.user_id == user_id)
        )