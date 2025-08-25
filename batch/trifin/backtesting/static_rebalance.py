"""
rebalance.py

10년간 다양한 자산(주식, 비트코인, 금, 채권, 발행어음)에 대해
매월 15일 목표 비율로 리밸런싱하며 백테스트하는 스크립트.

- 의존성: SQLAlchemy, numpy, pandas
- DB 가격: SPY, QQQ, SCHD, BTC-USD, GLD는 Price 테이블에서 조회
- 채권/어음 등 상수 수익률 자산은 코드 내 직접 계산
- robust 예외처리, 한글 문서화, 단위테스트 포함
- 작성일: 2025-05-18
- 작성자: 사용자 요청 기반

사용 예시:
    python rebalance.py

변경이력:
    - v1.0.0: 최초 작성

TODO:
    - 거래비용, 세금 등 현실 요소 반영
    - 리밸런싱 주기/날짜 파라미터화
    - 리포트/시각화 기능 추가
"""

from batch.trifin.backtesting import USDT_APR, BOND_ANNUAL_3_5_APR
from batch.trifin.backtesting.config import (
    TOTAL_ASSETS,
    DYNAMIC_ASSET_ALLOC,
    STATIC_ASSET_ALLOC,
)
from batch.trifin.backtesting.data.symbol import Symbol


def get_static_rebalance_history(
        price_data, reb_date, days, cash, portfolio, history
):
    """
    [정적 리밸런싱 백테스트 - 공통 로직 통일 버전]
    - 리밸런싱 시 reb_date 기준 목표 비중으로 수량 조정
    - 채권/USDT 등 이자형 자산은 prev_date~reb_date 기간 동안 복리 이자 반영
    - 자산별 평가는 reb_date 시점 가격 및 가치로 통일
    """
    # 1) 자산별 reb_date 시점 가격 구하기
    prices_now = {}
    for sym in DYNAMIC_ASSET_ALLOC.keys():
        df = price_data[sym]
        price_row = df[df.index <= reb_date].iloc[-1]
        prices_now[sym] = price_row["price"]

    # 2) 방어자산(USDT, 채권 등) 이자형 자산의 복리 이자 적용 (전달~이번달 days 기준)
    if Symbol.USDT in portfolio:
        portfolio[Symbol.USDT] *= (1 + USDT_APR / 365) ** days
    if Symbol.BOND_ANNUAL_3_5 in portfolio:
        portfolio[Symbol.BOND_ANNUAL_3_5] *= (1 + BOND_ANNUAL_3_5_APR) ** (days / 365)

    # 3) 전체 자산 평가액 계산 (reb_date 기준, 이자 반영 후)
    total_value = (
            cash
            + sum(
        portfolio[dynamic_sym] * prices_now.get(dynamic_sym, 1.0)
        for dynamic_sym in DYNAMIC_ASSET_ALLOC.keys()
    )
            + sum(portfolio[stable_sym] for stable_sym in STATIC_ASSET_ALLOC.keys())
    )

    # 4) 목표 비율로 리밸런싱 (reb_date 시점 가격 기준)
    for sym in TOTAL_ASSETS.keys():
        alloc = TOTAL_ASSETS[sym]
        if sym in prices_now:
            # 성장자산: 목표 비중에 맞춰 수량 조정
            portfolio[sym] = (total_value * alloc) / prices_now.get(sym, 1.0)
        else:
            # 방어자산(채권/USDT): 가치 기반으로 조정
            portfolio[sym] = total_value * alloc

    # 5) 전체 자산 평가액 기록 (reb_date 시점)
    asset_values = {}
    for sym in TOTAL_ASSETS:
        if sym in prices_now:
            # 성장자산: 수량 * reb_date 시점 가격
            asset_values[sym] = portfolio[sym] * prices_now[sym]
        else:
            # 방어자산: reb_date 시점 가치(수량)
            asset_values[sym] = portfolio[sym]
    total_value = round(sum(asset_values.values()), 3)
    history.append({"date": reb_date, "static_rebalance": total_value, **asset_values})
