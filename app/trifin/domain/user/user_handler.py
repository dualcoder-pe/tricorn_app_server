"""
user_handler.py

UserHandler: 사용자 관련 API 요청 처리
- UserService 의존
"""

from typing import Optional, List

from fastapi import HTTPException

from app.trifin.domain.user.user_model import UserCreate, UserRead
from app.trifin.domain.user.user_service import UserService
from core.util.log_util import logger


class UserHandler:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def create_user(self, user: UserCreate) -> UserRead:
        try:
            obj = await self.user_service.create_user(user.to_orm())
            return UserRead.model_validate(obj)
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=500, detail=str(e))

    async def get_user(self, uid: int) -> Optional[UserRead]:
        user = await self.user_service.get_user(uid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserRead.model_validate(user)

    async def list_users(self, limit: int = 100) -> List[UserRead]:
        users = await self.user_service.list_users(limit)
        return [UserRead.model_validate(u) for u in users]
