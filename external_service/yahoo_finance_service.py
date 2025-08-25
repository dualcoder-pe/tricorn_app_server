"""
파일명: yahoo_finance_service.py
설명: Yahoo Finance에서 시가(Open), 고가(High), 저가(Low), 종가(Close), 거래량(Volume) 데이터를 가져오는 서비스 모듈
의존성: yfinance (설치: pip install yfinance)
사용 예시:
    from yahoo_finance_service import get_yahoo_finance_ohlcv
    data = get_yahoo_finance_ohlcv('SPY')
    print(data)
버전 기록:
    - v1.0 2025-05-17 최초 작성
참고: https://github.com/ranaroussi/yfinance
"""

import datetime
from typing import List

import yfinance as yf

from src.repository.models.price_table import Price


def get_yahoo_finance_ohlcv(
    symbol: str,
    start: str,
    end: str = "",
    period: str = "1d",
    interval: str = "1d",
) -> List[Price]:
    """
    Yahoo Finance에서 지정한 종목의 OHLCV(시가, 고가, 저가, 종가, 거래량) 전체 데이터를 Price 객체 리스트로 조회합니다.

    Args:
        symbol (str): 조회할 종목명 (예: 'SPY', 'QQQ', 'SCHD', 'BTC-USD', 'GLD' 등)
        period (str): 조회 기간 (예: '1d', '5d', '1mo', '1y', 'max' 등)
        interval (str): 데이터 간격 (예: '1d', '1h', '1m' 등)
        start (str): 조회 시작일 (예: '2022-01-01')
        end (str): 조회 종료일 (예: '2022-12-31')

    Returns:
        List[Price]: 기간 내 모든 OHLCV가 Price 객체로 반환됨

    Raises:
        ValueError: 종목 데이터가 없거나 조회 실패 시 예외 발생

    예시:
        >>> prices = get_yahoo_finance_ohlcv('SPY', period='5d')
        >>> for price in prices:
        ...     print(price)

    TODO:
        - 멀티 심볼 지원
        - 타임존 옵션
        - 에러 로깅 개선
    """

    try:
        # 기본값 설정: end(오늘)
        if not end:
            end = datetime.datetime.now().strftime("%Y-%m-%d")
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval, start=start, end=end)
        if df.empty:
            raise ValueError(f"Yahoo Finance에서 데이터를 찾을 수 없습니다: {symbol}")
        prices = []
        for idx, row in df.iterrows():
            try:
                ts = idx.to_pydatetime()  # pyright: ignore[reportAttributeAccessIssue]
            except AttributeError:
                ts = idx
            price = Price(
                symbol=symbol,
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=float(row["Volume"]),
                timestamp=ts,
            )
            prices.append(price)
        return prices
    except Exception as e:
        # 에러 발생 시 상세 메시지와 함께 예외 재발생
        raise ValueError(f"Yahoo Finance 데이터 조회 중 오류 발생: {symbol}, {str(e)}")


# 모듈 단위 테스트 코드 (직접 실행 시 동작)
if __name__ == "__main__":
    import pprint

    test_symbols = ["SPY", "QQQ", "SCHD", "BTC-USD", "GLD"]
    for sym in test_symbols:
        try:
            print(f"\n[{sym}] OHLCV 데이터:")
            pprint.pprint(get_yahoo_finance_ohlcv(sym, "2015-01-01"))
        except Exception as ex:
            print(f"[ERROR] {sym}: {ex}")
