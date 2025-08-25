from fastapi import APIRouter, Depends, Request

from app.bagtionary.common.middleware.verifier import verify_country, verify_page, verify_size
from app.bagtionary.domain.product.product_handler import ProductHandler
from app.bagtionary.domain.product.product_model import GetProductListResult, GetProductResult
from app.bagtionary.inject import get_product_handler
from core.util.log_util import logger
from core.util.op_util import safe_int, safe_dict_value

product_router = APIRouter(
    prefix="/product",
    tags=["bagtionary/product"]
)


@product_router.get("/list", response_model=GetProductListResult)
async def get_product_list(
        request: Request,
        ctr: str = Depends(verify_country),
        page: int = Depends(verify_page),
        size: int = Depends(verify_size),
        product_handler: ProductHandler = Depends(get_product_handler),
):
    logger.d(f"call get_product_list")
    query_params = dict(request.query_params)
    return await product_handler.get_product_list(
        request.state.language,
        ctr,
        safe_dict_value(query_params, ["brand"], ""),
        safe_dict_value(query_params, ["keyword"], ""),
        safe_dict_value(query_params, ["bag_size"], ""),
        safe_dict_value(query_params, ["colors"], ""),
        safe_dict_value(query_params, ["sort"], ""),
        page,
        size,
        safe_int(safe_dict_value(query_params, ["min_price"])),
        safe_int(safe_dict_value(query_params, ["max_price"])),
    )


@product_router.get("/{raw_id}", response_model=GetProductResult)
async def get_product(
        raw_id: str,
        request: Request,
        ctr: str = Depends(verify_country),
        product_handler: ProductHandler = Depends(get_product_handler),
):
    logger.d(f"call get_product {raw_id}")
    return await product_handler.get_product(
        raw_id,
        request.state.language,
        ctr,
        request.state.is_debug,
    )
