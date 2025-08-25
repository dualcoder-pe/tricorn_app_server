"""
profit_service.py

ProfitService: 수익률 관련 비즈니스 로직 담당 서비스 계층
- insert, get 등 repository 연동
"""
from typing import Optional, List

from app.trifin.data.repository.models.profit_table import Profit
from app.trifin.data.repository.profit_repository import insert_profit, get_profit_by_id, get_profits_by_user_id, get_profits_by_account_id


class ProfitService:
    async def create_profit(self, profit: Profit) -> Profit:
        return insert_profit(profit)

    async def get_profit(self, profit_id: int) -> Optional[Profit]:
        return get_profit_by_id(profit_id)

    async def list_profits_by_user(self, user_id: int, limit: int = 100) -> List[Profit]:
        return get_profits_by_user_id(user_id, limit)

    async def list_profits_by_account(self, account_id: int, limit: int = 100) -> List[Profit]:
        return get_profits_by_account_id(account_id, limit)
