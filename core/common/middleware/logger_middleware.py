import time
from typing import Callable, Awaitable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from core.util.log_util import logger


class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        formatted_process_time = '{0:.2f}'.format(process_time * 1000)
        logger.d(f"Request: {request.method} {request.url} completed in {formatted_process_time}ms")

        return response
