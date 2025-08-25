"""
account_service.py

AccountService: 계좌 관련 비즈니스 로직 담당 서비스 계층
- insert, get 등 repository 연동
"""
from typing import Optional, List

from app.trifin.data.repository.account_repository import insert_account, get_account_by_id, get_accounts_by_user_id
from app.trifin.data.repository.models.account_table import Account


class AccountService:
    async def create_account(self, account: Account) -> Account:
        return insert_account(account)

    async def get_account(self, account_id: int) -> Optional[Account]:
        return get_account_by_id(account_id)

    async def list_accounts_by_user(self, user_id: int, limit: int = 100) -> List[Account]:
        return get_accounts_by_user_id(user_id, limit)
