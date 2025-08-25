"""
user_service.py

UserService: 사용자 관련 비즈니스 로직 담당 서비스 계층
- insert, get 등 repository 연동
"""
from typing import Optional, List

from app.trifin.data.repository.models.user_table import User
from app.trifin.data.repository.user_repository import insert_user, get_user_by_id, get_users


class UserService:
    async def create_user(self, user: User) -> User:
        return insert_user(user)

    async def get_user(self, uid: int) -> Optional[User]:
        return get_user_by_id(uid)

    async def list_users(self, limit: int = 100) -> List[User]:
        return get_users(limit)
