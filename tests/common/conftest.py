from pathlib import Path
from typing import Any, AsyncGenerator

import aio_pika
import msgpack
import pytest
import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession



import aio_pika
import pytest_asyncio
import pytest

from tests.mocking.rabbit import MockRMQManager, MockMessage
from db.storages import rabbit
from db.storages.postgres import async_session, get_db
from scripts.load_fixture import load_fixture

BASE_DIR = Path(__file__).parent
SEED_DIR = BASE_DIR / 'seeds'


@pytest.fixture(scope='session')
def app() -> FastAPI:
    return create_app()


@pytest_asyncio.fixture()
async def db_session(app: FastAPI) -> AsyncSession:
    async with async_session() as session:

        async def overrided_db_session() -> AsyncGenerator[AsyncSession, None]:
            yield session
            await session.rollback()

        app.dependency_overrides[get_db] = overrided_db_session
        yield session
        await session.rollback()


@pytest_asyncio.fixture()
async def _load_seeds(db_session: AsyncSession, seeds: list[Path]) -> None:
    await load_fixture(seeds, db_session)


@pytest_asyncio.fixture()
async def _load_queue(
    monkeypatch: pytest.MonkeyPatch, predefined_queue: Any, correlation_id
):

    mock_rmq = MockRMQManager(None)
    queue = mock_rmq.init_queue()
    if predefined_queue is not None:
        await queue.put(msgpack.packb(predefined_queue), correlation_id=correlation_id)

    monkeypatch.setattr(rabbit, 'rmq', mock_rmq)
    monkeypatch.setattr(aio_pika, 'Message', MockMessage)