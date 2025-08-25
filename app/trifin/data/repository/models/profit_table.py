"""
profit_table.py

수익률(Profit) 테이블에 대응하는 SQLAlchemy ORM 모델 파일.

- 의존성: SQLAlchemy
- 용도: 수익률 정보 저장 및 ORM 매핑
- 사용법:
    from profit_table import Profit
- 버전: 1.0.0
- 작성일: 2025-06-07
- 작성자: 사용자 요청 기반
- 변경이력:
    - v1.0.0: 최초 작성

"""

from sqlalchemy import Column, BigInteger, Float, ForeignKey

from app.trifin.data.repository.models.base import Base


class Profit(Base):
    """
    Profit(수익률) 테이블에 대응하는 SQLAlchemy ORM 모델 클래스.

    Attributes:
        id (int): 고유 식별자, 기본키, 자동 증가
        user_id (int): 유저 ID (FK)
        account_id (int): 계좌 ID (FK)
        profit (float): 수익률
    """
    __tablename__ = "profit"
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="고유 식별자")
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, comment="유저 ID")
    account_id = Column(BigInteger, ForeignKey("account.id"), nullable=False, comment="계좌 ID")
    profit = Column(Float, nullable=False, comment="수익률")

    def __repr__(self) -> str:
        return f"<Profit(id={self.id}, user_id={self.user_id}, account_id={self.account_id}, profit={self.profit})>"
