"""
profit_model.py (Domain)

- 목적: 수익률(Profit) 도메인용 Pydantic Request/Response 모델 정의
- 작성일: 2025-06-07
"""

from pydantic import BaseModel


class ProfitRead(BaseModel):
    id: int
    user_id: int
    account_id: int
    profit: float

    class Config:
        orm_mode = True
