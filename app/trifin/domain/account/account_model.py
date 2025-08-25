"""
account_model.py (Domain)

- 목적: 계좌(Account) 도메인용 Pydantic Request/Response 모델 정의
- 작성일: 2025-06-07
"""

from pydantic import BaseModel, Field

from app.trifin.data.repository.models.account_table import Account


class AccountCreate(BaseModel):
    user_id: int = Field(..., description="유저 ID")
    name: str = Field(..., description="계좌 이름")

    def to_orm(self) -> Account:
        """
        Pydantic AccountCreate → SQLAlchemy Account 변환
        balance는 항상 0으로 저장
        """
        data = self.model_dump()
        data["balance"] = 0  # balance를 항상 0으로 강제
        return Account(**data)


class AccountRead(BaseModel):
    id: int
    user_id: int
    name: str
    balance: float

    class Config:
        orm_mode = True
        from_attributes = True
