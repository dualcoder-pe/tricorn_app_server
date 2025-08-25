"""
save_symbol_price.py

Yahoo Finance에서 symbol_list의 가격을 조회해 DB에 저장하는 스크립트

- 의존성: yfinance, SQLAlchemy
- 사용법:
    python save_symbol_price.py
- 버전: 1.0.0
- 작성일: 2025-05-17
- 작성자: 사용자 요청 기반
- 변경이력:
    - v1.0.0: 최초 작성
"""

import logging

from src.external_service.yahoo_finance_service import get_yahoo_finance_ohlcv
from src.repository.price_repository import insert_prices_ignore_bulk

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

symbol_list = ["SPY", "IVV", "SPLG", "QQQ", "QQQM", "SCHD", "BTC-USD", "GLD", "KRW=X", "TLT", "^TNX", "^VIX"]
# SPY, IVV, SPLG: S&P 500 추종
# QQQ, QQQM: Nasdaq 추종
# TNX: 미국채10년물
# VIX: VIX지수


def save_symbol_price(start: str):
    """
    Yahoo Finance에서 symbol_list의 가격 정보 전체를 가져와 DB에 bulk 저장합니다.

    Raises:
        Exception: 저장 실패 또는 데이터 조회 실패 시
    """
    try:
        for symbol in symbol_list:
            prices = get_yahoo_finance_ohlcv(symbol, start)
            logger.info(f"{symbol} 가격 데이터 {len(prices)}건 수신")
            insert_prices_ignore_bulk(prices)
            logger.info(f"{symbol} 가격 데이터 일괄 저장 완료")
    except Exception as e:
        logger.error(f"가격 저장 실패: {e}")
        raise


if __name__ == "__main__":
    save_symbol_price()

# TODO: 여러 종목 지원, 스케줄러 연동, 로깅 개선, 에러 상세화
# 단위 테스트 예시 (pytest 등에서 활용):
# def test_save_spy_price(monkeypatch):
#     class DummySession:
#         def add(self, obj): pass
#         def commit(self): pass
#         def refresh(self, obj): pass
#         def close(self): pass
#     def dummy_get_ohlcv(symbol):
#         return {"Open":1, "High":2, "Low":0.5, "Close":1.5, "Volume":100}
#     monkeypatch.setattr("external_service.yahoo_finance_service.get_yahoo_finance_ohlcv", dummy_get_ohlcv)
#     monkeypatch.setattr("repository.price_repository.insert_price", lambda s, p: p)
#     save_symbol_price()
