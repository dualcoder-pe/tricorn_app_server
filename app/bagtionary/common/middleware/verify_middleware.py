from typing import Callable, Awaitable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class VerifyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if request.url.path.startswith("/api"):
            if ('X-Bagtionary-Version' not in request.headers or
                    'X-Bagtionary-Package' not in request.headers):
                return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        is_debug = request.headers.get('X-Bagtionary-Package', '').endswith('.debug')
        request.state.is_debug = is_debug

        request.state.language = request.headers.get('X-Bagtionary-Language', 'KO')

        response = await call_next(request)

        return response
