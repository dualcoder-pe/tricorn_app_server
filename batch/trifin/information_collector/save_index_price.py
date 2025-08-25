"""
save_index_price.py

FRED API에서 주요 경제지표(DGS10, CPIAUCSL, UNRATE)의 시계열 데이터를 조회하여 DB에 저장하는 스크립트

- 의존성: requests, SQLAlchemy, dotenv
- 사용법:
    python save_index_price.py
- 버전: 1.0.0
- 작성일: 2025-05-18
- 참고: save_symbol_price.py, fred_service.py
"""

import logging

from src.external_service.fred_service import get_fred_index_price
from src.repository.index_repository import insert_indexes_ignore_bulk
from src.repository.price_repository import insert_prices_ignore_bulk

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

index_list = ["DGS10", "CPIAUCSL", "UNRATE", "VIXCLS"]


def save_index_price(start: str):
    """
    FRED API에서 index_list의 시계열 데이터를 모두 조회하여 DB에 bulk 저장합니다.

    Raises:
        Exception: 저장 실패 또는 데이터 조회 실패 시
    """
    try:
        for symbol in index_list:
            prices = get_fred_index_price(symbol, start)
            logger.info(f"{symbol} 지표 데이터 {len(prices)}건 수신")
            insert_indexes_ignore_bulk(prices)
            logger.info(f"{symbol} 지표 데이터 일괄 저장 완료")
    except Exception as e:
        logger.error(f"지표 저장 실패: {e}")
        raise


if __name__ == "__main__":
    save_index_price()

# TODO: 다양한 지표 지원, 스케줄러 연동, 로깅 개선, 에러 상세화
# 단위 테스트 예시 (pytest 등에서 활용):
# def test_save_dgs10(monkeypatch):
#     class DummySession:
#         def add(self, obj): pass
#         def commit(self): pass
#         def refresh(self, obj): pass
#         def close(self): pass
#     def dummy_get_index(symbol):
#         from datetime import datetime
#         from src.repository.models.price_table import Price
#         return [Price(symbol=symbol, open=1, high=1, low=1, close=1, volume=0, timestamp=datetime(2024,1,1))]
#     monkeypatch.setattr("external_service.fred_service.get_fred_index_price", dummy_get_index)
#     monkeypatch.setattr("repository.price_repository.insert_prices_ignore_bulk", lambda p: len(p))
#     save_index_price()
