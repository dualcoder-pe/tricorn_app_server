"""
order_router.py

Order 관련 API 라우터 정의
"""
from typing import List

from fastapi import APIRouter, Depends

from app.trifin.domain.order.order_handler import OrderHandler
from app.trifin.domain.order.order_model import OrderCreate, OrderRead
from app.trifin.domain.order.order_service import OrderService

order_router = APIRouter(prefix="/api/order")


def get_order_service():
    return OrderService()


def get_order_handler(order_service: OrderService = Depends(get_order_service)):
    return OrderHandler(order_service)


@order_router.post("/", response_model=OrderRead)
async def create_order(order: OrderCreate, handler: OrderHandler = Depends(get_order_handler)):
    return await handler.create_order(order)


@order_router.get("/{order_id}", response_model=OrderRead)
async def get_order(order_id: int, handler: OrderHandler = Depends(get_order_handler)):
    return await handler.get_order(order_id)


@order_router.get("/account/{account_id}", response_model=List[OrderRead])
async def list_orders_by_account(account_id: int, limit: int = 100, handler: OrderHandler = Depends(get_order_handler)):
    return await handler.list_orders_by_account(account_id, limit)


@order_router.get("/user/{user_id}", response_model=List[OrderRead])
async def list_orders_by_user(user_id: int, limit: int = 100, handler: OrderHandler = Depends(get_order_handler)):
    return await handler.list_orders_by_user(user_id, limit)
