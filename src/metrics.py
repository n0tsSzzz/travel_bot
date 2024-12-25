import time
from functools import wraps
from typing import Any, Callable, TypeVar

from prometheus_client import Counter, Histogram

BUCKETS = [
    0.2,
    0.4,
    0.6,
    0.8,
    1.0,
    1.2,
    1.4,
    1.6,
    1.8,
    2.0,
    float("+inf"),
]


REQUESTS_TOTAL = Counter("producer_http_requests_total", "Total HTTP Requests", ["method", "path"])
INTEGRATION_METHOD_DURATION = Histogram(
    "producer_integration_method_duration_seconds",
    "Time spent in\
integration methods",
    buckets=BUCKETS,
)
RABBITMQ_MESSAGES_PRODUCED = Counter("producer_rabbitmq_messages_produced_total", "Total messages produced to RabbitMQ")
RABBITMQ_MESSAGES_CONSUMED = Counter(
    "producer_rabbitmq_messages_consumed_total", "Total messages consumed from RabbitMQ"
)


R = TypeVar("R")


def measure_time(func: Callable[..., R]) -> Callable[..., R]:
    @wraps(func)
    def wrapper(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> R:
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        duration = time.monotonic() - start_time
        INTEGRATION_METHOD_DURATION.observe(duration)
        return result

    return wrapper
