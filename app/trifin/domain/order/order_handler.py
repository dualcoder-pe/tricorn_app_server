"""
order_handler.py

OrderHandler: 주문 관련 API 요청 처리
- OrderService 의존
"""

from typing import Optional, List

from fastapi import HTTPException

from app.trifin.domain.order.order_model import OrderCreate, OrderRead
from app.trifin.domain.order.order_service import OrderService


class OrderHandler:
    def __init__(self, order_service: OrderService):
        self.order_service = order_service

    async def create_order(self, order: OrderCreate) -> OrderRead:
        try:
            obj = await self.order_service.create_order(order.to_orm())
            return OrderRead.model_validate(obj)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_order(self, order_id: int) -> Optional[OrderRead]:
        order = await self.order_service.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return OrderRead.model_validate(order)

    async def list_orders_by_account(
            self, account_id: int, limit: int = 100
    ) -> List[OrderRead]:
        orders = await self.order_service.list_orders_by_account(account_id, limit)
        return [OrderRead.model_validate(o) for o in orders]

    async def list_orders_by_user(
            self, user_id: int, limit: int = 100
    ) -> List[OrderRead]:
        orders = await self.order_service.list_orders_by_user(user_id, limit)
        return [OrderRead.model_validate(o) for o in orders]
