import logging.config

import aio_pika
import msgpack


from consumer.logger import LOGGING_CONFIG, logger, correlation_id_ctx
# from consumer.metrics import TOTAL_RECEIVED_MESSAGES
from schema.user import UserMessage
from schema.item import ItemMessage, ItemQueueInitMessage
from db.storages import rabbit
from config.settings import settings

from consumer.handlers.user import handle_event_user
from consumer.handlers.item import handle_event_item
from consumer.handlers.trip import handle_event_trip

async def start_consumer() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)
    logger.info('Starting consumer...')

    async with rabbit.channel_pool.acquire() as channel:  # type: aio_pika.Channel

        # Will take no more than 10 messages in advance
        await channel.set_qos(prefetch_count=10) # TODO почитать

        # Declaring queue
        queue = await channel.declare_queue(settings.USER_MESSAGES_QUEUE, durable=True)

        logger.info('Consumer started!')
        async with queue.iterator() as queue_iter:
            async for message in queue_iter: # type: aio_pika.Message
                # TOTAL_RECEIVED_MESSAGES.inc()
                correlation_id_ctx.set(message.correlation_id)

                body: UserMessage | ItemMessage | ItemQueueInitMessage = msgpack.unpackb(message.body)
                logger.info("Message: %s", body)

                try:
                    if body.get('event') == 'users':
                        await handle_event_user(body)
                    elif body.get('event') == 'items':
                        await handle_event_item(body)
                    elif body.get('event') == 'trip':
                        await handle_event_trip(body)

                    await message.ack()
                except Exception as e:
                    logger.error("Error processing message: %s", e)
                    await message.reject(requeue=False)
                    # await message.nack(requeue=False)

# Возможно более понятный код вида консмура
# queue: Queue
# while True:
#     message = await queue.get()
#     async with message.process():  # после выхода из with будет ack (есть еще no_ack)
#         correlation_id_ctx.set(message.correlation_id)
#         logger.info("Message ...")
#
#         body: GiftMessage = msgpack.unpackb(message.body)
#         if body['event'] == 'gift':
#             await handle_event_gift(body)