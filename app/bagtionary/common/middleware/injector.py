from typing import Optional

from fastapi import Header, HTTPException
from starlette import status

from core.util.op_util import is_none_or_empty


async def get_client_version(x_bagtionary_version: str = Header(None)) -> Optional[str]:
    if is_none_or_empty(x_bagtionary_version):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return x_bagtionary_version
