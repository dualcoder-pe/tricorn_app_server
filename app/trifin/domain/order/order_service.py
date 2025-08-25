"""
order_service.py

OrderService: 주문 관련 비즈니스 로직 담당 서비스 계층
- insert, get 등 repository 연동
"""
from typing import Optional, List

from app.trifin.data.repository.models.order_table import Order
from app.trifin.data.repository.order_repository import insert_order, get_order_by_id, get_orders_by_account_id, get_orders_by_user_id


class OrderService:
    async def create_order(self, order: Order) -> Order:
        return insert_order(order)

    async def get_order(self, order_id: int) -> Optional[Order]:
        return get_order_by_id(order_id)

    async def list_orders_by_account(self, account_id: int, limit: int = 100) -> List[Order]:
        return get_orders_by_account_id(account_id, limit)

    async def list_orders_by_user(self, user_id: int, limit: int = 100) -> List[Order]:
        return get_orders_by_user_id(user_id, limit)
