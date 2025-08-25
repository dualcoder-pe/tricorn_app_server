from typing import Optional

from fastapi import APIRouter, Depends, Request, Query

from app.bagtionary.common.middleware.injector import get_client_version
from app.bagtionary.common.middleware.verifier import verify_country, verify_page, verify_size
from app.bagtionary.domain.home.home_handler import HomeHandler
from app.bagtionary.domain.home.home_model import GetHomeCategoryListResult, GetHomeProductListItem
from app.bagtionary.inject import get_home_handler
from core.util.log_util import logger

home_router = APIRouter(
    prefix="/home",
    tags=["bagtionary/home"]
)


@home_router.get("/category/list", response_model=GetHomeCategoryListResult)
async def get_home_category_list(
        request: Request,
        ctr: str = Depends(verify_country),
        client_version: Optional[str] = Depends(get_client_version),
        handler: HomeHandler = Depends(get_home_handler),
):
    logger.d(f"call get_home_category_list {client_version}")

    return await handler.get_home_category_list(
        request.state.language,
        ctr,
        client_version
    )


@home_router.get("/product/list/{category}", response_model=GetHomeProductListItem)
async def get_home_product_list(
        category: str,
        request: Request,
        price: Optional[int] = Query(None),
        ctr: str = Depends(verify_country),
        page: int = Depends(verify_page),
        size: int = Depends(verify_size),
        handler: HomeHandler = Depends(get_home_handler),
):
    logger.d(f"call get_home_product_list_by_category {category}, {price}")

    return await handler.get_home_product_list(
        category,
        price,
        page,
        size,
        request.state.language,
        ctr,
    )
