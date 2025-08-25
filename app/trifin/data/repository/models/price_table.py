"""
price_model.py

MySQL의 price 테이블에 대응하는 Price 모델 정의 파일.

- 의존성: SQLAlchemy
- 용도: 가격 데이터(OHLCV) 저장 및 ORM 매핑
- 사용법:
    from price_model import Price
    # SQLAlchemy 세션에서 사용
- 버전: 1.0.0
- 작성일: 2025-05-17
- 작성자: 사용자 요청 기반
- 변경이력:
    - v1.0.0: 최초 작성

참고: 추후 인덱스, 복합키, 성능 최적화 등 확장 가능
"""

from datetime import datetime

from sqlalchemy import Column, Float, BigInteger, DateTime, String
from sqlalchemy import UniqueConstraint

from src.repository.models.base import Base


class Price(Base):
    """
    MySQL의 price 테이블에 대응하는 SQLAlchemy ORM 모델 클래스.

    Attributes:
        id (int): 고유 식별자, 기본키, 자동 증가
        open (float): 시가
        high (float): 고가
        low (float): 저가
        close (float): 종가
        volume (float): 거래량
        timestamp (datetime): 가격 데이터의 기준 시각 (UTC)

    예시:
        >>> price = Price(open=100.0, high=110.0, low=95.0, close=105.0, volume=12345.6, timestamp=datetime.utcnow())
    """

    __tablename__ = "price"
    __table_args__ = (
        UniqueConstraint("symbol", "timestamp", name="uq_symbol_timestamp"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="고유 식별자")
    symbol = Column(String(20), nullable=False, comment="종목 심볼")
    open = Column(Float, nullable=False, comment="시가")
    high = Column(Float, nullable=False, comment="고가")
    low = Column(Float, nullable=False, comment="저가")
    close = Column(Float, nullable=False, comment="종가")
    volume = Column(Float, nullable=False, comment="거래량")
    timestamp = Column(
        DateTime, nullable=False, index=True, comment="가격 데이터의 기준 시각 (UTC)"
    )

    def __repr__(self) -> str:
        """
        Price 객체의 문자열 표현 반환.
        """
        return (
            f"<Price(id={self.id}, symbol={self.symbol}, open={self.open}, high={self.high}, low={self.low}, "
            f"close={self.close}, volume={self.volume}, timestamp={self.timestamp})>"
        )

    # TODO: 복합 인덱스 추가, 데이터 정합성 검증, 추가 필드 확장 등

# 에러 처리 전략:
# - 모든 필드는 nullable=False로 설정하여 데이터 누락 방지
# - 타입 불일치, 값 누락 등은 SQLAlchemy에서 예외 발생
# - 예외 발생 시 상위 레이어에서 적절히 핸들링 필요

# 성능 및 확장 고려사항:
# - timestamp 필드에 인덱스 적용
# - 대량 데이터 처리 시 파티셔닝, 샤딩 등 고려
# - 추가 필드/인덱스 확장 용이하게 설계

# 단위 테스트 예시 (pytest 등에서 활용):
# def test_price_model_fields():
#     price = Price(open=1.0, high=2.0, low=0.5, close=1.5, volume=100, timestamp=datetime.utcnow())
#     assert isinstance(price.open, float)
#     assert price.id is None  # 아직 flush/commit 전
#     assert price.timestamp is not None
