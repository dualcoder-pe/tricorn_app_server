"""
order_model.py (Domain)

- 목적: 주문(Order) 도메인용 Pydantic Request/Response 모델 정의
- 작성일: 2025-06-07
"""

from enum import Enum

from pydantic import BaseModel, Field

from app.trifin.data.repository.models.order_table import Order


class OrderType(str, Enum):
    buy = "buy"
    sell = "sell"


from datetime import datetime


class OrderCreate(BaseModel):
    type: OrderType = Field(..., description="주문 타입 (buy/sell)")
    symbol: str = Field(..., description="종목 심볼")
    account_id: int = Field(..., description="계좌 ID")
    size: float = Field(..., description="주문 수량")
    price: float = Field(..., description="주문 단가")

    def to_orm(self) -> Order:
        """
        Pydantic OrderCreate → SQLAlchemy Order 변환
        date는 서버에서 UTC 기준 현재 시간으로 자동 지정
        """
        data = self.model_dump()
        data["date"] = datetime.utcnow().isoformat()
        return Order(**data)


class OrderRead(BaseModel):
    id: int
    type: OrderType
    symbol: str
    account_id: int
    date: str
    size: float
    price: float

    class Config:
        orm_mode = True
