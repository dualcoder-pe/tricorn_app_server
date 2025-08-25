"""
account_table.py

계좌(Account) 테이블에 대응하는 SQLAlchemy ORM 모델 파일.

- 의존성: SQLAlchemy
- 용도: 계좌 정보 저장 및 ORM 매핑
- 사용법:
    from account_table import Account
- 버전: 1.0.0
- 작성일: 2025-06-07
- 작성자: 사용자 요청 기반
- 변경이력:
    - v1.0.0: 최초 작성

"""

from sqlalchemy import Column, BigInteger, String, Float, ForeignKey

from app.trifin.data.repository.models.base import Base


class Account(Base):
    """
    Account(계좌) 테이블에 대응하는 SQLAlchemy ORM 모델 클래스.

    Attributes:
        id (int): 고유 식별자, 기본키, 자동 증가
        user_id (int): 유저 ID (FK)
        name (str): 계좌 이름
        balance (float): 계좌 잔고
    """
    __tablename__ = "account"
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="고유 식별자")
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, comment="유저 ID")
    name = Column(String(50), nullable=False, comment="계좌 이름")
    balance = Column(Float, nullable=False, comment="계좌 잔고")

    def __repr__(self) -> str:
        return f"<Account(id={self.id}, user_id={self.user_id}, name={self.name}, balance={self.balance})>"
