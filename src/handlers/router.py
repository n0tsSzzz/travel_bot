from aiogram import Router

from src.middlewares.__logging import LoggingMiddleware

router = Router()
router.message.middleware(LoggingMiddleware())
router.callback_query.middleware(LoggingMiddleware())
