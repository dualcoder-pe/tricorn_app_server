"""
account_router.py

Account 관련 API 라우터 정의
"""
from typing import List

from fastapi import APIRouter, Depends

from app.trifin.domain.account.account_handler import AccountHandler
from app.trifin.domain.account.account_model import AccountCreate, AccountRead
from app.trifin.domain.account.account_service import AccountService

account_router = APIRouter(prefix="/api/account")


def get_account_service():
    return AccountService()


def get_account_handler(account_service: AccountService = Depends(get_account_service)):
    return AccountHandler(account_service)


@account_router.post("/", response_model=AccountRead)
async def create_account(account: AccountCreate, handler: AccountHandler = Depends(get_account_handler)):
    return await handler.create_account(account)


@account_router.get("/{account_id}", response_model=AccountRead)
async def get_account(account_id: int, handler: AccountHandler = Depends(get_account_handler)):
    return await handler.get_account(account_id)


@account_router.get("/user/{user_id}", response_model=List[AccountRead])
async def list_accounts_by_user(user_id: int, limit: int = 100, handler: AccountHandler = Depends(get_account_handler)):
    return await handler.list_accounts_by_user(user_id, limit)
