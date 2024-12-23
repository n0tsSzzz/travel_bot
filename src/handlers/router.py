from aiogram import Router

from src.middlewares.__logging import LoggingMiddleware
from src.middlewares.auth import AuthMiddleware

router = Router()
# router.message.middlewares(AuthMiddleware())
router.message.middleware(LoggingMiddleware())
router.callback_query.middleware(LoggingMiddleware())