"""
profit_router.py

Profit 관련 API 라우터 정의
"""

from typing import List

from fastapi import APIRouter, Depends

from app.trifin.domain.profit.profit_handler import ProfitHandler
from app.trifin.domain.profit.profit_model import ProfitRead
from app.trifin.domain.profit.profit_service import ProfitService

profit_router = APIRouter(prefix="/api/profit")


def get_profit_service():
    return ProfitService()


def get_profit_handler(profit_service: ProfitService = Depends(get_profit_service)):
    return ProfitHandler(profit_service)


@profit_router.get("/{profit_id}", response_model=ProfitRead)
async def get_profit(
        profit_id: int, handler: ProfitHandler = Depends(get_profit_handler)
):
    return await handler.get_profit(profit_id)


@profit_router.get("/user/{user_id}", response_model=List[ProfitRead])
async def list_profits_by_user(
        user_id: int, limit: int = 100, handler: ProfitHandler = Depends(get_profit_handler)
):
    return await handler.list_profits_by_user(user_id, limit)


@profit_router.get("/account/{account_id}", response_model=List[ProfitRead])
async def list_profits_by_account(
        account_id: int,
        limit: int = 100,
        handler: ProfitHandler = Depends(get_profit_handler),
):
    return await handler.list_profits_by_account(account_id, limit)
