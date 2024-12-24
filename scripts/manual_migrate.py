import asyncio
import logging.config

from sqlalchemy.exc import IntegrityError

from db.models.meta import Base
from db.storages.postgres import engine
from src.logger import LOGGING_CONFIG, logger

logging.config.dictConfig(LOGGING_CONFIG)


async def main() -> None:
    try:
        async with engine.begin() as conn:
            logger.info("Hand Migration")
            await conn.run_sync(Base.metadata.drop_all)
            # await conn.run_sync(Base.metadata.create_all)
    except IntegrityError:
        logger.exception("Already exists")


if __name__ == "__main__":
    asyncio.run(main())
