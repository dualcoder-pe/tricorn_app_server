import time
from typing import Optional

from pydantic import BaseModel, Field

from core.util.constants import MAX_INT, WEEK_EPOCH_MILLIS
from core.util.op_util import safe_dict_value


class GetProductListResult(BaseModel):
    products: list['ThumbnailProductVO'] = Field([])
    last_page: int = Field(-1, alias="lastPage", validation_alias="last_page")
    brands: Optional[list[str]] = Field(None)


class GetProductResult(BaseModel):
    raw_id: str = Field(..., alias="rawId", validation_alias="raw_id")
    brand: str
    type: str
    language: str
    country: str
    price: list['PriceVO']
    latest_price: 'PriceVO' = Field(..., alias="latestPrice", validation_alias="latest_price")
    product_url: str = Field(..., alias="productUrl", validation_alias="product_url")
    name: str
    material: str
    description: str
    spec: str
    color: list[str]
    color_code: list[str] = Field([], alias="colorCode", validation_alias="color_code")
    image_url: str = Field(..., alias="imageUrl", validation_alias="image_url")
    sub_images_url: list[str] = Field(..., alias="subImagesUrl", validation_alias="sub_images_url")
    size: Optional['SizeVO']
    created_date: int = Field(..., alias="createdDate", validation_alias="created_date")
    last_modified_date: int = Field(..., alias="lastModifiedDate", validation_alias="last_modified_date")


class FilterOptions(BaseModel):
    brand: Optional[list[str]] = Field(None)
    min_price: Optional[int] = Field(None, alias="minPrice", validation_alias="min_price")
    max_price: Optional[int] = Field(None, alias="maxPrice", validation_alias="max_price")
    keyword: Optional[str] = Field(None)
    bag_size: Optional[list[str]] = Field(None, alias="bagSize", validation_alias="bag_size")
    colors: Optional[list[str]] = Field(None)


class PriceVO(BaseModel):
    timestamp: int = Field(0)
    value: float = Field(0.0)
    display: str = Field("₩0")


class SizeVO(BaseModel):
    width: Optional[float | list] = Field(None)
    height: Optional[float | list] = Field(None)
    depth: Optional[float | list] = Field(None)
    unit: Optional[str] = Field(None)


class ProductSalesVO(BaseModel):
    price: list[PriceVO]
    product_url: str
    season: Optional[str] = Field(None)
    launched_date: int
    latest_price: PriceVO


class ProductDescVO(BaseModel):
    name: str
    material: str
    description: Optional[str]
    spec: Optional[str]
    color: list[str]


class ProductVO(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    raw_id: str = Field(..., alias="rawId", validation_alias="raw_id")
    brand: str
    type: str
    sales: dict
    desc: dict
    color_code: list[str] = Field([], alias="colorCode", validation_alias="color_code")
    image_url: str = Field(..., alias="imageUrl", validation_alias="image_url")
    sub_images_url: list[str] = Field([], alias="subImagesUrl", validation_alias="sub_images_url")
    size: dict
    created_date: int = Field(..., alias="createdDate", validation_alias="created_date")
    last_modified_date: int = Field(..., alias="lastModifiedDate", validation_alias="last_modified_date")

    def export(self, country: str, language: str) -> GetProductResult:
        return GetProductResult(
            raw_id=self.raw_id,
            brand=self.brand,
            type=self.type,
            country=country,
            language=language,
            price=safe_dict_value(self.sales, [country, "price"], []),
            latest_price=safe_dict_value(self.sales, [country, "latestPrice"], PriceVO()),
            product_url=safe_dict_value(self.sales, [country, "productUrl"], ""),
            name=safe_dict_value(self.desc, [language, "name"], ""),
            material=safe_dict_value(self.desc, [language, "material"], ""),
            description=safe_dict_value(self.desc, [language, "description"], ""),
            spec=safe_dict_value(self.desc, [language, "spec"], ""),
            color=safe_dict_value(self.desc, [language, "color"], []),
            color_code=self.color_code,
            image_url=self.image_url,
            sub_images_url=self.sub_images_url,
            size=self.size,
            created_date=self.created_date,
            last_modified_date=self.last_modified_date,
        )


class ThumbnailProductVO(BaseModel):
    id: str
    url: str
    brand: str
    name: str
    price: str
    is_new: bool = Field(alias="isNew")

    @classmethod
    def create(cls, language: str, country: str, data: dict) -> 'ThumbnailProductVO':
        now = int(time.time() * 1000)
        return cls(
            id=data["rawId"],
            url=data["imageUrl"],
            brand=data["brand"],
            name=safe_dict_value(data, ["desc", language, "name"], ""),
            price=safe_dict_value(data, ["sales", country, "latestPrice", "display"], ""),
            isNew=safe_dict_value(data, ["sales", country, "launchedDate"], MAX_INT) >= now - WEEK_EPOCH_MILLIS * 2,
        )


class GetProductListVO(BaseModel):
    products: list[dict]
    total_count: int
    last_page: int
    brands: Optional[list[str]]

    def export(self, language: str, country: str) -> GetProductListResult:
        return GetProductListResult(
            products=list(map(lambda x: ThumbnailProductVO.create(language, country, x), self.products)),
            last_page=self.last_page,
            brands=self.brands
        )