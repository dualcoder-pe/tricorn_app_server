from fastapi import APIRouter, Depends, Request

from app.bagtionary.common.middleware.verifier import verify_country
from app.bagtionary.domain.product.product_handler import ProductHandler
from app.bagtionary.domain.product.product_model import GetProductListResult
from app.bagtionary.inject import get_product_handler
from core.util.log_util import logger
from core.util.op_util import safe_int, safe_dict_value

router = APIRouter(
    prefix="/api"
)


@router.get("/products", response_model=GetProductListResult)
async def get_products(
        request: Request,
        ctr: str = Depends(verify_country),
        product_handler: ProductHandler = Depends(get_product_handler),
):
    logger.d(f"call get_products")
    query_params = dict(request.query_params)
    return await product_handler.get_product_list(
        request.state.language,
        ctr,
        safe_dict_value(query_params, ["brand"], ""),
        safe_dict_value(query_params, ["keyword"], ""),
        safe_dict_value(query_params, ["bag_size"], ""),
        safe_dict_value(query_params, ["colors"], ""),
        safe_dict_value(query_params, ["sort"], ""),
        safe_int(safe_dict_value(query_params, ["page"])),
        safe_int(safe_dict_value(query_params, ["size"])),
        safe_int(safe_dict_value(query_params, ["min_price"])),
        safe_int(safe_dict_value(query_params, ["max_price"])),
    )
