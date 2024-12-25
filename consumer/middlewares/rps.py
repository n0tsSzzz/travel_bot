from typing import Any, Callable

from fastapi import Request, Response

from consumer.metrics import REQUESTS_TOTAL


class RequestCountMiddleware:
    async def __call__(self, request: Request, call_next: Callable[[Request], Any]) -> Any:
        response: Response = await call_next(request)
        REQUESTS_TOTAL.labels(status_code=response.status_code, path=request.url.path).inc()
        return response
