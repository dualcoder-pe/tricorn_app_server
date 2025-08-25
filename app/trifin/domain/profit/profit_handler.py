"""
profit_handler.py

ProfitHandler: 수익률 관련 API 요청 처리
- ProfitService 의존
"""

from typing import Optional, List

from fastapi import HTTPException

from app.trifin.domain.profit.profit_model import ProfitRead
from app.trifin.domain.profit.profit_service import ProfitService


class ProfitHandler:
    def __init__(self, profit_service: ProfitService):
        self.profit_service = profit_service

    async def get_profit(self, profit_id: int) -> Optional[ProfitRead]:
        profit = await self.profit_service.get_profit(profit_id)
        if not profit:
            raise HTTPException(status_code=404, detail="Profit not found")
        return ProfitRead.model_validate(profit)

    async def list_profits_by_user(
            self, user_id: int, limit: int = 100
    ) -> List[ProfitRead]:
        profits = await self.profit_service.list_profits_by_user(user_id, limit)
        return [ProfitRead.model_validate(p) for p in profits]

    async def list_profits_by_account(
            self, account_id: int, limit: int = 100
    ) -> List[ProfitRead]:
        profits = await self.profit_service.list_profits_by_account(account_id, limit)
        return [ProfitRead.model_validate(p) for p in profits]
