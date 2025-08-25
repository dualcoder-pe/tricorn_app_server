from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.bagtionary.domain.product.product_model import ThumbnailProductVO


class HomeCategory(str, Enum):
    latest_added = "최근 출시된 가방"
    price_changed = "최근 가격 변동이 있는 가방"
    price_band = ""
    denim = "데님 소재 가방"
    unknown = "unknown"

    @staticmethod
    def get_by_name(name: str) -> 'HomeCategory':
        if name == "latest_added":
            return HomeCategory.latest_added
        elif name == "price_changed":
            return HomeCategory.price_changed
        elif name == "price_band":
            return HomeCategory.price_band
        elif name == "denim":
            return HomeCategory.denim
        else:
            return HomeCategory.unknown

    def create_item(self) -> 'HomeCategoryItem':
        return HomeCategoryItem(self)


class HomeCategoryItem(BaseModel):
    category: str = Field("")
    title: str = Field("")
    params: dict = Field({})

    def __init__(self, category: HomeCategory, price: Optional[int] = None):
        super().__init__()
        self.category = category.name
        if category is category.price_band:
            self.title = self.get_price_band_title(price)
            self.params["price"] = price
        else:
            self.title = category.value

    @staticmethod
    def get_price_band_title(price: int) -> str:
        if price >= 10000000:
            return f"1000만원 이상 가방"
        return f"{int(price / 10000)}만원대 가방"


class GetHomeCategoryListItem(BaseModel):
    category: str = Field("unknown")
    title: str = Field("")
    params: dict = Field({})
    products: list[ThumbnailProductVO] = Field([])

    def is_empty(self) -> bool:
        return len(self.products) <= 0

    # def to_product_list(self, last_page: int, brands: Optional[list[str]], params=None) -> 'GetHomeProductListItem':
    #     if params is None:
    #         params = {}
    #     return GetHomeProductListItem(
    #         category=self.category,
    #         title=self.title,
    #         params=params,
    #         products=self.products,
    #         last_page=last_page,
    #         brands=brands,
    #     )


class GetHomeCategoryListResult(BaseModel):
    category_list: list[GetHomeCategoryListItem] = Field([], serialization_alias="categoryList")


class GetHomeProductListItem(BaseModel):
    category: str = Field("unknown")
    title: str = Field("")
    products: list[ThumbnailProductVO] = Field([])
    last_page: int = Field(-1, serialization_alias="lastPage")
    brands: Optional[list[str]] = Field(None)

    def is_empty(self) -> bool:
        return len(self.products) <= 0
