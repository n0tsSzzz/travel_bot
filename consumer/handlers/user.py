from db.storages.postgres import db
from schema.user import UserMessage

import logging.config
from consumer.logger import LOGGING_CONFIG, logger

async def handle_event_user(message: UserMessage) -> None:
    logging.config.dictConfig(LOGGING_CONFIG)
    if message['action'] == 'register':
        try:
            if not await db.user_exists(message['user_id']):
                await db.add_user(user_id=message['user_id'], username=message['username'])
                logger.info('Added User %s into db', message)
        except Exception as e:
            logger.error("Error processing message: %s", e)