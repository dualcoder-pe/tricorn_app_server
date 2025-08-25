from typing import Optional

from app.bagtionary.data.repository.product_repository import ProductRepository
from app.bagtionary.data.repository.product_view_count_repository import ProductViewCountRepository
from app.bagtionary.domain.product.product_model import FilterOptions, GetProductListVO, ProductVO


class ProductService:
    def __init__(self, product_repository: ProductRepository, product_view_count_repository: ProductViewCountRepository):
        self.product_repository = product_repository
        self.product_view_count_repository = product_view_count_repository

    async def get_product_list(self,
                               language: str,
                               country: str,
                               sort: str,
                               page: Optional[int],
                               size: Optional[int],
                               filter_options: FilterOptions,
                               ) -> GetProductListVO:
        return await self.product_repository.find_products_by_option(language, country, sort, page, size, filter_options)

    async def get_product(self, raw_id: str, is_debug: bool = False) -> ProductVO:
        if not is_debug:
            await self.product_view_count_repository.add_count(raw_id)

        result = await self.product_repository.select({"rawId": raw_id}, projection={"productId": 0})
        result = result[0] if len(result) > 0 else {}
        result["id"] = str(result.pop("_id"))
        return ProductVO(**result)
