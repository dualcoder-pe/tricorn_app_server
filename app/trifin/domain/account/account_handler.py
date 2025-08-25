"""
account_handler.py

AccountHandler: 계좌 관련 API 요청 처리
- AccountService 의존
"""

from typing import Optional, List

from fastapi import HTTPException

from app.trifin.domain.account.account_model import AccountCreate, AccountRead
from app.trifin.domain.account.account_service import AccountService
from core.util.logger import get_logger

logger = get_logger()


class AccountHandler:
    def __init__(self, account_service: AccountService):
        self.account_service = account_service

    async def create_account(self, account: AccountCreate) -> AccountRead:
        try:
            obj = await self.account_service.create_account(account.to_orm())
            return AccountRead.from_orm(obj)
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=500, detail=str(e))

    async def get_account(self, account_id: int) -> Optional[AccountRead]:
        account = await self.account_service.get_account(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return AccountRead.model_validate(account)

    async def list_accounts_by_user(
            self, user_id: int, limit: int = 100
    ) -> List[AccountRead]:
        accounts = await self.account_service.list_accounts_by_user(user_id, limit)
        return [AccountRead.model_validate(a) for a in accounts]
