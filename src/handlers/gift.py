# import asyncio
#
# import aio_pika
# import msgpack
# from aio_pika.exceptions import QueueEmpty
# from aiogram.fsm.context import FSMContext
# from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
# from aio_pika import Queue
#
# from config.settings import settings
# from src.storage.rabbit import channel_pool
# from .router import router
# from ...templates.env import render
#
#
# # async def listen(callback_query: CallbackQuery, user_id: str):
# #     async with channel_pool.acquire() as channel:  # type: aio_pika.Channel
# #         queue: Queue = await channel.declare_queue(settings.USER_GIFT_QUEUE_TEMPLATE.format(user_id=user_id), durable=True)
# #         message = await queue.get()
# #         parsed_message: Gift = msgpack.unpackb(message)
# #         await callback_query.answer(parsed_message)
# #
#
# @router.callback_query()
# async def next_gift(callback_query: CallbackQuery, state: FSMContext) -> None:
#     # user_data = await state.get_data()
#     # user_data_per_callback = user_data[callback_query.data]
#     await callback_query.message.delete_reply_markup()
#     async with channel_pool.acquire() as channel:  # type: aio_pika.Channel
#         queue: Queue = await channel.declare_queue(
#             settings.USER_GIFT_QUEUE_TEMPLATE.format(user_id=callback_query.from_user.id),
#             durable=True,
#         )
#
#         retries = 3
#         for _ in range(retries):
#             try:
#                 gift = await queue.get()
#                 parsed_gift = msgpack.unpackb(gift.body)
#
#                 # async with aiohttp.ClientSession() as session:
#                 #     async with session.get('https://cdn.velostrana.ru/upload/models/velo/63352/full.jpg') as response:
#                 #         content = await response.read()
#                 #
#                 # photo = BufferedInputFile(content, 'test')
#                 # # callback buttons
#
#                 inline_btn_1 = InlineKeyboardButton(text='Следующий подарок', callback_data='next_gift')
#                 markup = InlineKeyboardMarkup(
#                     inline_keyboard=[[inline_btn_1]]
#                 )
#
#                 await callback_query.message.answer_photo(
#                     photo=parsed_gift['photo'],
#                     caption=render('gift/gift.jinja2', gift=parsed_gift),
#                     reply_markup=markup,
#                 )
#                 return
#             except QueueEmpty:
#                 await asyncio.sleep(1)
#
#         await callback_query.message.answer('Нет подарков')