from typing import Optional

from fastapi import Depends

from app.bagtionary.data.repository.product_repository import ProductRepository
from app.bagtionary.data.repository.product_view_count_repository import ProductViewCountRepository
from app.bagtionary.domain.home.home_handler import HomeHandler
from app.bagtionary.domain.home.home_service import HomeService
from app.bagtionary.domain.product.product_handler import ProductHandler
from app.bagtionary.domain.product.product_service import ProductService

# Repository
__product_repository_instance: Optional[ProductRepository] = None
__product_view_count_repository_instance: Optional[ProductViewCountRepository] = None


def get_product_repository() -> ProductRepository:
    global __product_repository_instance
    if __product_repository_instance is None:
        __product_repository_instance = ProductRepository()
    return __product_repository_instance


def get_product_view_count_repository() -> ProductViewCountRepository:
    global __product_view_count_repository_instance
    if __product_view_count_repository_instance is None:
        __product_view_count_repository_instance = ProductViewCountRepository()
    return __product_view_count_repository_instance


# Home
__home_service_instance: Optional[HomeService] = None
__home_handler_instance: Optional[HomeHandler] = None


def get_home_service(product_repository: ProductRepository = Depends(get_product_repository)) -> HomeService:
    global __home_service_instance
    if __home_service_instance is None:
        __home_service_instance = HomeService(product_repository)
    return __home_service_instance


def get_home_handler(home_service: HomeService = Depends(get_home_service)) -> HomeHandler:
    global __home_handler_instance
    if __home_handler_instance is None:
        __home_handler_instance = HomeHandler(home_service)
    return __home_handler_instance


# Product
__product_service_instance: Optional[ProductService] = None
__product_handler_instance: Optional[ProductHandler] = None


def get_product_service(product_repository: ProductRepository = Depends(get_product_repository),
                        product_view_count_repository: ProductViewCountRepository = Depends(get_product_view_count_repository)) -> ProductService:
    global __product_service_instance
    if __product_service_instance is None:
        __product_service_instance = ProductService(product_repository, product_view_count_repository)
    return __product_service_instance


def get_product_handler(product_service: ProductService = Depends(get_product_service)) -> ProductHandler:
    global __product_handler_instance
    if __product_handler_instance is None:
        __product_handler_instance = ProductHandler(product_service)
    return __product_handler_instance
