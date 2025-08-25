from typing import Annotated, Optional

from fastapi import Header, HTTPException, status, Query

from core.util.op_util import is_none_or_empty, safe_int


async def verify_package(x_bagtionary_package: Annotated[str, Header(None)]):
    if is_none_or_empty(x_bagtionary_package):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


async def verify_country(ctr: Optional[str] = Query(None)) -> str:
    if is_none_or_empty(ctr):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return ctr


async def verify_page(page: Optional[str] = Query(None)) -> int:
    if is_none_or_empty(page):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return safe_int(page, 0)


async def verify_size(size: Optional[str] = Query(None)) -> int:
    if is_none_or_empty(size):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return safe_int(size, 0)
