import uuid

import aio_pika
import msgpack
import pytest
from pathlib import Path

from sqlalchemy import select, func

from config.settings import settings
from consumer.app import start_consumer
from consumer.model.gift import Gift
from consumer.schema.gift import GiftMessage

from schema.item import Item
from tests.mocking.rabbit import MockExchange

BASE_DIR = Path(__file__).parent
SEED_DIR = BASE_DIR / 'seeds'


@pytest.mark.parametrize(
    ('predefined_queue', 'seeds', 'correlation_id'),
    [
        (
            {"user_items.1": Item(id=0, title=)},
            [SEED_DIR / 'public.gift.json'],
            str(uuid.uuid4()),
        ),
    ]
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_load_queue', '_load_seeds')
async def test_handle_gift(db_session, predefined_queue, correlation_id, mock_exchange: MockExchange) -> None:
    await start_consumer()
    expected_routing_key = settings.USER_GIFT_QUEUE_TEMPLATE.format(user_id=predefined_queue['user_id'])

    expected_calls = []
    async with db_session:
        not_fetched = await db_session.execute(select(Gift).order_by(func.random()))
        tuple_rows = not_fetched.all()
        gifts = [row for row, in tuple_rows]

        for gift in gifts:
            expected_message = aio_pika.Message(
                msgpack.packb({
                    'name': gift.name,
                    'photo': gift.photo,
                    'category': gift.category,
                }),
                correlation_id=correlation_id,
            )

            expected_calls.append(
                ('publish', (expected_message,), {'routing_key': expected_routing_key})
            )

        mock_exchange.assert_has_calls(expected_calls, any_order=True)