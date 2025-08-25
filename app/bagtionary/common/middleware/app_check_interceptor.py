from fastapi import Response
from starlette.requests import Request

from core.util.log_util import logger


async def app_check_interceptor(request: Request, response: Response) -> Response:
    logger.d(f"app_check_interceptor {request}")

    # if 'X-Firebase-AppCheck' in request.headers:
    #     token = request.headers.get('X-Firebase-AppCheck')
    #     if not token or not token_verify(token):
    #         logger.error(f"Failed to verify token: {token}")
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    logger.d(f"app_check_interceptor {response}")
    return response
