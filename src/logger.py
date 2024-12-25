import logging.config
from contextlib import suppress
from contextvars import ContextVar
from typing import Any
from uuid import uuid4

import yaml
from starlette_context import context
from starlette_context.errors import ContextDoesNotExistError
from starlette_context.header_keys import HeaderKeys

with open("config/logging.conf.yml", "r") as f:
    LOGGING_CONFIG = yaml.full_load(f)


class ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        corr_id = correlation_id_ctx.get(None)
        if corr_id is not None:
            return "[%s] %s" % (corr_id, super().format(record))

        with suppress(ContextDoesNotExistError):
            if corr_id := context.get(HeaderKeys.correlation_id, None):
                return "[%s] %s" % (corr_id, super().format(record))

        return super().format(record)


logger = logging.getLogger("backend_logger")

correlation_id_ctx: ContextVar[Any | None] = ContextVar("correlation_id")


def get_or_create_correlation_id() -> Any | None:
    try:
        return context.get(HeaderKeys.correlation_id, None)
    except ContextDoesNotExistError:
        return str(uuid4())
