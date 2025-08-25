"""
user_router.py

User 관련 API 라우터 정의
"""
from typing import List

from fastapi import APIRouter, Depends

from app.trifin.domain.user.user_handler import UserHandler
from app.trifin.domain.user.user_model import UserCreate, UserRead
from app.trifin.domain.user.user_service import UserService

user_router = APIRouter(prefix="/api/user")


# DI: 실제 서비스/핸들러 인스턴스 주입
def get_user_service():
    return UserService()


def get_user_handler(user_service: UserService = Depends(get_user_service)):
    return UserHandler(user_service)


@user_router.post("/", response_model=UserRead)
async def create_user(user: UserCreate, handler: UserHandler = Depends(get_user_handler)):
    return await handler.create_user(user)


@user_router.get("/{uid}", response_model=UserRead)
async def get_user(uid: int, handler: UserHandler = Depends(get_user_handler)):
    return await handler.get_user(uid)


@user_router.get("/", response_model=List[UserRead])
async def list_users(limit: int = 100, handler: UserHandler = Depends(get_user_handler)):
    return await handler.list_users(limit)
