from typing import Optional

from fastapi import HTTPException
from starlette import status

from app.bagtionary.domain.product.product_model import FilterOptions, GetProductListResult, GetProductResult
from app.bagtionary.domain.product.product_service import ProductService
from core.util.log_util import logger
from core.util.op_util import is_none_or_empty, split_list_params


class ProductHandler:
    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    async def get_product_list(self,
                               language: str,
                               country: str,
                               brand: str,
                               keyword: str,
                               bag_size: str,
                               colors: str,
                               sort: str,
                               page: Optional[int],
                               size: Optional[int],
                               min_price: Optional[int],
                               max_price: Optional[int],
                               ) -> GetProductListResult:
        logger.d(f"{language} {country} {brand} {keyword} {bag_size} {colors} {sort} {page} {size} {min_price} {max_price}")

        try:
            if (page is not None and (page < 0 or size is None)) \
                    or is_none_or_empty(language) \
                    or is_none_or_empty(country) \
                    or is_none_or_empty(sort):
                logger.i(f"{page} {size} {language} {country} {sort}")
                raise HTTPException(status_code=400, detail="Invalid Params")

            brand_list = split_list_params(brand)
            bag_size_list = split_list_params(bag_size)
            color_list = split_list_params(colors)
            filter_options = FilterOptions(brand=brand_list, min_price=min_price, max_price=max_price, keyword=keyword, bag_size=bag_size_list,
                                           colors=color_list)

            result = await self.product_service.get_product_list(
                language=language,
                country=country,
                sort=sort,
                page=page,
                size=size,
                filter_options=filter_options,
            )

            if len(result.products) <= 0:
                return GetProductListResult()

            return result.export(language, country)

        except Exception as e:
            logger.e(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_product(self,
                          raw_id: str,
                          language: str,
                          country: str,
                          is_debug: bool = False,
                          ) -> GetProductResult:
        logger.d(f"{raw_id} {language} {country}")
        result = await self.product_service.get_product(raw_id, is_debug)
        return result.export(country, language)
