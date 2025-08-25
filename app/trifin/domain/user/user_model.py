"""
user_model.py (Domain)

- 목적: 유저(User) 도메인용 Pydantic Request/Response 모델 정의
- 작성일: 2025-06-07
"""

from pydantic import BaseModel, Field

from app.trifin.data.repository.models.user_table import User


class UserCreate(BaseModel):
    uid: str = Field(..., description="외부 시스템 연동용 유저 식별자")
    name: str = Field(..., description="사용자 이름")

    def to_orm(self) -> User:
        """
        Pydantic UserCreate → SQLAlchemy User 변환
        """
        return User(**self.model_dump())


class UserRead(BaseModel):
    id: int = Field(..., description="고유 식별자")
    uid: str = Field(..., description="외부 시스템 연동용 유저 식별자")
    name: str = Field(..., description="사용자 이름")

    class Config:
        from_attributes = True
