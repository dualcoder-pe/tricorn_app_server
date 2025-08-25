"""
fred_service.py

FRED(Federal Reserve Economic Data) API에서 주요 경제지표(예: DGS10, CPIAUCSL, UNRATE)를 조회하여 Price 모델 리스트로 반환하는 서비스 모듈

- 의존성: requests, SQLAlchemy, dotenv
- 사용법:
    from fred_service import get_fred_index_price
    prices = get_fred_index_price('DGS10')
    print(prices)
- 환경변수: FRED_API_KEY (필수)
- 버전: 1.0.0
- 작성일: 2025-05-18
- 참고: https://fred.stlouisfed.org/docs/api/fred/
"""

import os
import logging
import datetime
from typing import List, Optional
import requests
from dotenv import load_dotenv

from src.repository.models.index_table import Index

# 환경변수(.env)에서 FRED_API_KEY를 읽음
load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

FRED_API_BASE = "https://api.stlouisfed.org/fred/series/observations"


def get_fred_index_price(symbol: str, start: str, end: str = "") -> List[Index]:
    """
    FRED API에서 지정한 symbol(지표코드)의 시계열 데이터를 조회하여 Index 객체 리스트로 반환합니다.
    OHLCV 구조가 아니며, value/date 필드만을 저장합니다.

    Args:
        symbol (str): FRED 지표 코드 (예: 'DGS10', 'CPIAUCSL', 'UNRATE')
        start (str, optional): 조회 시작일 (YYYY-MM-DD).
        end (str, optional): 조회 종료일 (YYYY-MM-DD). 기본값: 오늘

    Returns:
        List[Index]: Index 객체 리스트 (날짜별 시계열)

    Raises:
        ValueError: API 키 누락, symbol 미존재, 데이터 조회 실패 등

    예시:
        >>> indexes = get_fred_index_price('DGS10', start='2020-01-01')
        >>> for idx in indexes:
        ...     print(idx)

    참고:
        - FRED API 문서: https://fred.stlouisfed.org/docs/api/fred/series_observations.html
    """
    if not FRED_API_KEY:
        raise ValueError(
            "FRED_API_KEY 환경변수가 설정되어 있지 않습니다. .env 파일을 확인하세요."
        )

    if not end:
        end = datetime.datetime.now().strftime("%Y-%m-%d")

    params = {
        "series_id": symbol,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start,
        "observation_end": end,
    }
    try:
        resp = requests.get(FRED_API_BASE, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if "observations" not in data or not data["observations"]:
            raise ValueError(f"FRED에서 데이터가 존재하지 않습니다: {symbol}")
        indexes = []
        for obs in data["observations"]:
            date_str = obs.get("date")
            value_str = obs.get("value")
            # 결측치 처리
            try:
                value = float(value_str)
            except (TypeError, ValueError):
                continue  # 결측치는 스킵
            dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            idx = Index(
                symbol=symbol,
                value=value,
                date=dt,
            )
            indexes.append(idx)
        return indexes
    except requests.RequestException as e:
        logger.error(f"FRED API 요청 실패: {e}")
        raise ValueError(f"FRED API 요청 실패: {e}")
    except Exception as e:
        logger.error(f"FRED 데이터 파싱 오류: {e}")
        raise ValueError(f"FRED 데이터 파싱 오류: {e}")


if __name__ == "__main__":
    import pprint

    test_symbols = ["DGS10", "CPIAUCSL", "UNRATE"]
    for sym in test_symbols:
        try:
            print(f"\n[{sym}] FRED 데이터:")
            pprint.pprint(get_fred_index_price(sym))
        except Exception as ex:
            print(f"[ERROR] {sym}: {ex}")
