from typing import Any, Callable

from fastapi import Request

from src.metrics import REQUESTS_TOTAL


class RequestCountMiddleware:
    async def __call__(self, request: Request, call_next: Callable[[Request], Any]) -> Any:
        REQUESTS_TOTAL.labels(method=request.method, path=request.url.path).inc()
        response = await call_next(request)
        return response
