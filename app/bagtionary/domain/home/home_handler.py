from typing import Optional

from fastapi import HTTPException
from starlette import status

from app.bagtionary.domain.home.home_model import GetHomeCategoryListResult, HomeCategory, GetHomeProductListItem
from app.bagtionary.domain.home.home_service import HomeService
from core.util.log_util import logger
from core.util.op_util import is_none_or_empty, version_compare


class HomeHandler:

    def __init__(self, service: HomeService):
        self.service = service

    async def get_home_category_list(self,
                                     language: str,
                                     country: str,
                                     client_version: Optional[str],
                                     ) -> GetHomeCategoryListResult:
        include_dynamic_category = True if client_version is not None and version_compare(client_version, '2.0.0') == -1 else False
        try:
            product_list = await self.service.get_home_category_list(
                language=language,
                country=country,
                include_dynamic_category=include_dynamic_category
            )

            return GetHomeCategoryListResult(category_list=product_list)

        except Exception as e:
            logger.e(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_home_product_list(self,
                                    category: str,
                                    price: Optional[int],
                                    page: int,
                                    size: int,
                                    language: str,
                                    country: str,
                                    ) -> GetHomeProductListItem:
        valid_category = HomeCategory.get_by_name(category)
        logger.d(f"category: {category} -> {valid_category}")
        try:
            product_list_item = await self.service.get_home_product_list(
                category=valid_category,
                price=price,
                page=page,
                size=size,
                language=language,
                country=country,
            )
            return product_list_item

        except Exception as e:
            logger.e(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    def split_list_params(param: Optional[str]) -> Optional[list[str]]:
        if is_none_or_empty(param):
            return None
        elif "," in param:
            return param.split(",")
        else:
            return [param]
