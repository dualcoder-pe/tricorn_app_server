"""
order_table.py

주문(Order) 테이블에 대응하는 SQLAlchemy ORM 모델 파일.

- 의존성: SQLAlchemy
- 용도: 주문 정보 저장 및 ORM 매핑
- 사용법:
    from order_table import Order
- 버전: 1.0.0
- 작성일: 2025-06-07
- 작성자: 사용자 요청 기반
- 변경이력:
    - v1.0.0: 최초 작성

"""

import enum

from sqlalchemy import Column, BigInteger, String, Float, ForeignKey, Enum as SAEnum

from app.trifin.data.repository.models.base import Base


class OrderTypeEnum(str, enum.Enum):
    buy = "buy"
    sell = "sell"


class UnitEnum(str, enum.Enum):
    KRW = "KRW"
    USD = "USD"


class Order(Base):
    """
    Order(주문) 테이블에 대응하는 SQLAlchemy ORM 모델 클래스.

    Attributes:
        id (int): 고유 식별자, 기본키, 자동 증가
        type (str): 주문 타입 (buy/sell)
        symbol (str): 종목 심볼
        account_id (int): 계좌 ID (FK)
        date (str): 주문일시 (ISO8601)
        size (float): 주문 수량
        price (float): 주문 단가
        unit (str): 화폐 단위 (KRW, USD)
    """

    __tablename__ = "order"
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="고유 식별자")
    type = Column(SAEnum(OrderTypeEnum), nullable=False, comment="주문 타입")
    symbol = Column(String(50), nullable=False, comment="종목 심볼")
    account_id = Column(
        BigInteger, ForeignKey("account.id"), nullable=False, comment="계좌 ID"
    )
    date = Column(String(30), nullable=False, comment="주문일시")
    size = Column(Float, nullable=False, comment="주문 수량")
    price = Column(Float, nullable=False, comment="주문 단가")
    unit = Column(
        SAEnum(UnitEnum),
        nullable=False,
        comment="화폐 단위 (KRW, USD)",
    )

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, type={self.type}, symbol={self.symbol}, account_id={self.account_id}, date={self.date}, size={self.size}, price={self.price}, unit={self.unit})>"
