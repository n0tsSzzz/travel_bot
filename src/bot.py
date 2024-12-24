from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from config.settings import settings
from db.storages.redis import redis_storage
from src.handlers.router import router as command_router
from src.keyboards.set_menu import set_main_menu

storage = RedisStorage(redis=redis_storage)
dp = Dispatcher(storage=storage)
default = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=settings.BOT_TOKEN, default=default)
dp.include_router(command_router)

# async def setup_bot() -> (Bot, Dispatcher):
#     await set_main_menu(bot)
#     return bot, dp