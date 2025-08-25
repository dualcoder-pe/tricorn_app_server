from math import ceil
from typing import Optional

from app.bagtionary.data.repository.base.base_mongo_repository import DefaultMongoRepository
from app.bagtionary.domain.product.product_model import FilterOptions, GetProductListVO
from core.util.constants import MAX_SIZE
from core.util.log_util import logger


class ProductRepository(DefaultMongoRepository):
    def __init__(self):
        super().__init__("product")

    async def find_products_by_option(self, language: str, country: str, sort: str, page: Optional[int], size: Optional[int],
                                      filter_options: FilterOptions) -> GetProductListVO:
        logger.d(f"findProducts {page} {size} {language} {country} {sort} {filter_options}")

        if size > MAX_SIZE:
            size = MAX_SIZE

        filters = [
            {"imageUrl": {"$ne": ""}},
            {"sales.KR.price.value": {"$ne": -1}}
        ]

        if filter_options.brand is not None:
            filters.append({"brand": {"$in": filter_options.brand}})

        if filter_options.keyword is not None:
            enhanced_keyword = filter_options.keyword.replace(" ", ".*")
            or_filter = [
                {f"desc.{language}.name": {"$regex": enhanced_keyword, "$options": "i"}},
                {f"desc.{language}.description": {"$regex": enhanced_keyword, "$options": "i"}},
                {f"desc.{language}.spec": {"$regex": enhanced_keyword, "$options": "i"}}
            ]
            filters.append({"$or": or_filter})

        if filter_options.min_price is not None:
            filters.append({f"sales.{country}.latestPrice.value": {"$gt": filter_options.min_price}})

        if filter_options.max_price is not None:
            filters.append({f"sales.{country}.latestPrice.value": {"$lt": filter_options.max_price}})

        if filter_options.bag_size is not None:
            filters.append({"bagSize": {"$in": filter_options.bag_size}})

        if filter_options.colors is not None:
            filters.append({"standardizedColor": {"$in": filter_options.colors}})

        query = {"$and": filters}

        if sort == "price_asc":
            sort_condition = {"sales.KR.latestPrice.value": 1, "rawId": 1}
        elif sort == "price_desc":
            sort_condition = {"sales.KR.latestPrice.value": -1, "rawId": -1}
        elif sort == "oldest":
            sort_condition = {"sales.KR.launchedDate": 1, "rawId": 1}
        else:  # latest
            sort_condition = {"sales.KR.launchedDate": -1, "rawId": -1}

        return await self.find_products(query, sort_condition, page, size)

    async def find_products(self, query: dict, sort: dict, page: Optional[int], size: Optional[int]) -> GetProductListVO:
        count = await self.count(filter=query, default=0)

        brand_list = await self.aggregate(
            pipeline=[
                {"$match": query},
                {"$group": {"_id": "$brand"}},
                {"$project": {
                    "brand": "$_id",
                    "_id": 0
                }}
            ]
        )
        brands = list(map(lambda x: x['brand'], brand_list))

        logger.d(f"query option: {query} {sort} {page} {size}")

        products = await self.paged_select(filter=query, sort=sort, page=page, size=size)
        divided = size if size is not None else len(products)
        last_page = int(ceil((count / divided)) - 1)

        logger.d(f"result: {count} {brands} {divided} {last_page}")

        res = {"products": products, "total_count": count, "last_page": last_page, "brands": brands}
        # logger.debug(f"res: {res}")

        return GetProductListVO(**res)
