"""
index_model.py

MySQL의 index 테이블에 대응하는 Index 모델 정의 파일.

- 의존성: SQLAlchemy
- 용도: 경제지표(OHLCV 아님, value 단일값) 저장 및 ORM 매핑
- 사용법:
    from index_model import Index
    # SQLAlchemy 세션에서 사용
- 버전: 1.0.0
- 작성일: 2025-05-18
- 작성자: 사용자 요청 기반
- 변경이력:
    - v1.0.0: 최초 작성

참고: symbol+date 복합 unique, 단일값(value) 저장, 확장성 고려
"""

from datetime import date

from sqlalchemy import Column, Float, BigInteger, Date, String
from sqlalchemy import UniqueConstraint

from src.repository.models.base import Base


class Index(Base):
    """
    MySQL의 index 테이블에 대응하는 SQLAlchemy ORM 모델 클래스.

    Attributes:
        id (int): 고유 식별자, 기본키, 자동 증가
        symbol (str): 인덱스 심볼 (예: 'DGS10', 'CPIAUCSL', 'UNRATE')
        value (float): 지표 값
        date (date): 데이터 기준 일자 (YYYY-MM-DD)

    예시:
        >>> idx = Index(symbol='DGS10', value=4.21, date=date(2024, 1, 1))
    """

    __tablename__ = "index"
    __table_args__ = (UniqueConstraint("symbol", "date", name="uq_symbol_date"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="고유 식별자")
    symbol = Column(String(20), nullable=False, comment="인덱스 심볼")
    value = Column(Float, nullable=False, comment="지표 값")
    date = Column(
        Date, nullable=False, index=True, comment="데이터 기준 일자 (YYYY-MM-DD)"
    )

    def __repr__(self) -> str:
        """
        Index 객체의 문자열 표현 반환.
        """
        return f"<Index(id={self.id}, symbol={self.symbol}, value={self.value}, date={self.date})>"

# 에러 처리 및 확장성 참고:
# - 모든 필드는 nullable=False로 설정하여 데이터 누락 방지
# - symbol/date 복합 unique로 데이터 중복 방지
# - value 타입, 범위 등은 실제 데이터 특성에 맞게 조정 가능
# - 추후 컬럼 확장(예: source, 단위 등) 가능

# 단위 테스트 예시 (pytest 등에서 활용):
# def test_index_model_fields():
#     idx = Index(symbol="DGS10", value=4.21, date=date(2024,1,1))
#     assert isinstance(idx.value, float)
#     assert idx.id is None  # 아직 flush/commit 전
#     assert idx.date is not None
