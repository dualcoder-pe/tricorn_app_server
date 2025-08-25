import random
import time
from typing import Optional

from app.bagtionary.data.repository.product_repository import ProductRepository
from app.bagtionary.domain.home.home_model import GetHomeCategoryListItem, HomeCategory, GetHomeProductListItem, HomeCategoryItem
from app.bagtionary.domain.product.product_model import ThumbnailProductVO, GetProductListVO
from core.util.constants import WEEK_EPOCH_MILLIS
from core.util.log_util import logger


class HomeService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    async def get_home_category_list(self, language: str, country: str, include_dynamic_category: bool) -> list[GetHomeCategoryListItem]:
        result_list = []
        # 최근 추가 가방
        latest_added_product = await self.get_latest_added_product(country, 0, 10)
        if len(latest_added_product.products) > 0:
            result_list.append(self.create_category_list(language, country, HomeCategory.latest_added.create_item(), latest_added_product))

        # 가격 변동 가방
        price_changed_product = await self.get_price_changed_product(country, 0, 10)
        if len(price_changed_product.products) > 0:
            result_list.append(self.create_category_list(language, country, HomeCategory.price_changed.create_item(), price_changed_product))

        if include_dynamic_category:
            # 가격대별 가방
            min_price, price_band_product = await self.get_price_band_product(country, 0, 10)
            if len(price_band_product.products) > 0:
                result_list.append(
                    self.create_category_list(language, country, HomeCategoryItem(HomeCategory.price_band, min_price), price_band_product))

        # 데님 소재 가방
        denim_product = await self.get_denim_product(language, country, 0, 10)
        if len(denim_product.products) > 0:
            result_list.append(self.create_category_list(language, country, HomeCategory.denim.create_item(), denim_product))

        # 브랜드별 고가 가방
        # 친환경 소재 가방(키워드:재활용,재생,에코,리사이클)

        return result_list

    async def get_home_product_list(self, category: HomeCategory, price: Optional[int], page: int, size: int, language: str,
                                    country: str) -> GetHomeProductListItem:
        if category == HomeCategory.latest_added:
            product_list = await self.get_latest_added_product(country, page, size)
            return self.create_product_list(language, country, category.create_item(), product_list)

        elif category == HomeCategory.price_changed:
            product_list = await self.get_price_changed_product(country, page, size)
            return self.create_product_list(language, country, category.create_item(), product_list)

        elif category == HomeCategory.price_band:
            min_price, product_list = await self.get_price_band_product(country, page, size, price)
            return self.create_product_list(language, country, HomeCategoryItem(category, min_price), product_list)

        elif category == HomeCategory.denim:
            product_list = await self.get_denim_product(language, country, page, size)
            return self.create_product_list(language, country, category.create_item(), product_list)
        else:
            return GetHomeProductListItem()

    async def get_latest_added_product(self, country: str, page: int, size: int) -> GetProductListVO:
        # 최근 추가 가방 (new 붙은 애들만)
        now = int(time.time() * 1000)
        two_weeks_ago = now - (WEEK_EPOCH_MILLIS * 2)
        return await self.repository.find_products(query={f"sales.{country}.launchedDate": {"$gt": two_weeks_ago}},
                                                   sort={f"sales.{country}.launchedDate": -1, "rawId": -1}, page=page, size=size)

    async def get_price_changed_product(self, country: str, page: int, size: int) -> GetProductListVO:
        return await self.repository.find_products(query={
            "$expr": {
                "$gt": [
                    {"$size": {
                        "$filter": {
                            "input": f"$sales.{country}.price",
                            "as": "price",
                            "cond": {"$gt": ["$$price.value", 0]}
                        }
                    }},
                    1
                ]
            }
        },
            sort={f"sales.{country}.latestPrice.timestamp": -1, "rawId": -1},
            page=page,
            size=size)

    async def get_price_band_product(self, country: str, page: int, size: int, price: Optional[int] = None) -> (int, GetProductListVO):
        ranges = [(1000000, 2000000), (2000000, 3000000), (3000000, 4000000), (4000000, 5000000), (5000000, 6000000), (6000000, 7000000),
                  (10000000, None)]

        selected_range = None
        if price is not None:
            for r in ranges:
                if r[0] == price:
                    selected_range = r

        if selected_range is None:
            selected_range = random.choice(ranges)
        logger.d(selected_range)

        min_price: int = selected_range[0]
        max_price: Optional[int] = selected_range[1]

        comparator = {"$gte": min_price}
        if max_price is not None:
            comparator["$lt"] = max_price
        logger.d(f"comparator: {comparator}")

        return min_price, await self.repository.find_products(query={f"sales.{country}.latestPrice.value": comparator},
                                                              sort={f"sales.{country}.latestPrice.value": 1, "rawId": -1},
                                                              page=page,
                                                              size=size)

    async def get_denim_product(self, language: str, country: str, page: int, size: int) -> GetProductListVO:
        return await self.repository.find_products(query={f"desc.{language}.description": {"$regex": "데님"}},
                                                   sort={f"sales.{country}.launchedDate": -1, "rawId": -1},
                                                   page=page,
                                                   size=size)

    @staticmethod
    def create_category_list(language: str, country: str, category_item: HomeCategoryItem, product_list: GetProductListVO) -> GetHomeCategoryListItem:
        return GetHomeCategoryListItem(category=category_item.category,
                                       title=category_item.title,
                                       params=category_item.params,
                                       products=map(lambda x: ThumbnailProductVO.create(language=language, country=country, data=x),
                                                    product_list.products))

    @staticmethod
    def create_product_list(language: str, country: str, category_item: HomeCategoryItem, product_list: GetProductListVO) -> GetHomeProductListItem:
        logger.d(f"create_product_list {product_list}")
        return GetHomeProductListItem(category=category_item.category,
                                      title=category_item.title,
                                      products=map(lambda x: ThumbnailProductVO.create(language=language, country=country, data=x),
                                                   product_list.products),
                                      last_page=product_list.last_page,
                                      brands=product_list.brands
                                      )
