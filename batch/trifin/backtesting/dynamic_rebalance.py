"""
dynamic_rebalance.py

동적으로 자산별 비중을 조정하는 백테스팅 스크립트

- 목적: 시장 상황(상승/하락폭)에 따라 성장자산(나스닥, S&P, 배당성장, 코인 등)의 비중을 동적으로 조정하며, 나머지 자산은 방어/채권 등으로 배분
- 의존성: numpy, pandas, matplotlib, backtesting.utils, 가격 데이터 파일
- 사용법: python dynamic_rebalance.py
- 주요 함수:
    - get_dynamic_alloc: 시장 변동률에 따라 동적 비중 반환
    - run_dynamic_backtest: 동적 비중으로 백테스트 실행
- 예외처리 및 robust 설계
- 변경이력:
    - v1.0.0: 최초 작성 (2025-05-23)
- TODO:
    - 거래비용/세금 반영
    - 리밸런싱 주기/날짜 파라미터화
    - 리포트/시각화 기능 개선

참고: 자세한 비중 조정 방법은 Readme.MD 참조
"""

import pandas as pd

from batch.trifin.backtesting import USDT_APR, BOND_ANNUAL_3_5_APR
from batch.trifin.backtesting.config import (
    DYNAMIC_ASSET_ALLOC,
    STATIC_ASSET_ALLOC,
    TOTAL_ASSETS,
    GROWTH_ASSETS,
    DYNAMIC_DEFENSE_WEIGHTS,
)
from batch.trifin.backtesting.data.symbol import Symbol
from lib.logger import get_logger

logger = get_logger()

# =====================
# 동적 비중 테이블 정의
# =====================
CHANGE_ALLOC_TABLE = pd.DataFrame(
    [
        # change, QQQ, SPY, SCHD, BTC
        # [-100, 0.8, 0.5, 0.5, 0],
        [25, 0.12, 0.12, 0.12, 0.04],
        [20, 0.14, 0.14, 0.14, 0.04],
        [15, 0.16, 0.16, 0.16, 0.05],
        [10, 0.18, 0.18, 0.18, 0.05],
        [5, 0.19, 0.19, 0.19, 0.05],
        [0, 0.20, 0.20, 0.20, 0.05],
        [-5, 0.135, 0.14, 0.14, 0.04],
        [-10, 0.15, 0.16, 0.16, 0.04],
        [-15, 0.165, 0.18, 0.18, 0.04],
        [-20, 0.18, 0.20, 0.20, 0.04],
        [-25, 0.195, 0.20, 0.20, 0.05],
        [-30, 0.20, 0.20, 0.20, 0.05],
    ],
    columns=[
        "change",
        Symbol.QQQ.name,
        Symbol.SPY.name,
        Symbol.SCHD.name,
        Symbol.BTC.name,
    ],  # pyright: ignore[reportArgumentType]
)


# =====================
# 함수: 동적 비중 결정
# =====================
def get_dynamic_alloc(drawdown: float, table: pd.DataFrame, symbol: str) -> float:
    """
    하락폭에 따라 개별 성장자산의 동적 비중을 반환 (전고점 기준)
    Args:
        drawdown (float): 해당 자산의 전고점 대비 하락률(%)
        table (pd.DataFrame): drawdown-비중 매핑 테이블
        symbol (str): 자산 심볼
    Returns:
        float: 해당 자산의 목표 비중
    Example:
        >>> get_dynamic_alloc(-13, DRAWDOWN_ALLOC_TABLE, Symbol.QQQ)
        0.15
    """
    filtered_change: pd.Series
    filtered = table[table["change"] >= drawdown]
    # idxmin/idxmax는 pandas Series에서만 사용 가능
    if not isinstance(filtered["change"], pd.Series):
        filtered_change = pd.Series(filtered["change"])
    else:
        filtered_change = filtered["change"]  # pyright: ignore[reportAssignmentType]
    if not filtered.empty:
        idx = filtered_change.idxmin()
    else:
        idx = table["change"].idxmax()
    row = table.loc[[idx]]
    return float(row[symbol].values[0])


def get_change_alloc(change: float, table: pd.DataFrame, symbol: str) -> float:
    """
    상승폭에 따라 개별 성장자산의 동적 비중을 반환 (전저점 기준)
    Args:
        change (float): 해당 자산의 전저점 대비 상승률(%)
        table (pd.DataFrame): change-비중 매핑 테이블
        symbol (str): 자산 심볼
    Returns:
        float: 해당 자산의 목표 비중
    Example:
        >>> get_change_alloc(13, CHANGE_ALLOC_TABLE, Symbol.QQQ)
        0.16
    """
    filtered_change: pd.Series
    filtered = table[table["change"] <= change]
    if not isinstance(filtered["change"], pd.Series):
        filtered_change = pd.Series(filtered["change"])
    else:
        filtered_change = filtered["change"]  # pyright: ignore[reportAssignmentType]
    if not filtered.empty:
        idx = filtered_change.idxmax()
    else:
        idx = table["change"].idxmin()
    row = table.loc[[idx]]
    return float(row[symbol.name].values[0])


# =====================
# 메인 백테스트 함수
# =====================
def get_dynamic_rebalance_history(price_data, reb_date, days, cash, portfolio, history):
    """
    [다이나믹 리밸런싱 백테스트 - 공통 로직 통일 버전]
    - days는 prev_date~reb_date 구간의 일수
    - USDT, 채권 등 이자형 자산은 days만큼 복리 이자를 선반영
    - 성장자산은 reb_date 시점 가격 기준으로 평가 및 리밸런싱
    - 자산별 평가액 기록 방식도 static과 동일하게 통일
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

    # 4) 동적 리밸런싱 전략의 목표 비중 계산
    target_alloc = get_dynamic_target_alloc(
        reb_date, price_data
    )  # 실제 구현에 맞게 호출
    for sym in TOTAL_ASSETS.keys():
        alloc = target_alloc.get(sym, 0.0)
        if sym in prices_now:
            portfolio[sym] = (total_value * alloc) / prices_now.get(sym, 1.0)
        else:
            portfolio[sym] = total_value * alloc

    # 5) 자산별 평가액 기록 (reb_date 시점)
    asset_values = {}
    for sym in TOTAL_ASSETS:
        if sym in prices_now:
            asset_values[sym] = portfolio[sym] * prices_now[sym]
        else:
            asset_values[sym] = portfolio[sym]
    total_value = round(sum(asset_values.values()), 3)
    history.append({"date": reb_date, "dynamic_rebalance": total_value, **asset_values})


def get_dynamic_target_alloc(reb_date, price_data):
    # 성장자산별 전고점/전저점 추적 및 drawdown/upward 계산
    growth_alloc = {}
    growth_sum = 0.0

    # 각 자산별 전고점(pastPeak) 및 역대 최고가(highest) 상태 관리
    pastPeak = {sym: None for sym in GROWTH_ASSETS}
    highest = {sym: None for sym in GROWTH_ASSETS}
    in_downtrend = {sym: False for sym in GROWTH_ASSETS}

    for sym in GROWTH_ASSETS:
        price_series = price_data[sym]["price"]
        # pandas Series로 보장: idxmin/idxmax 등 사용 가능
        price_now = price_series[price_series.index <= reb_date].iloc[-1]

        # 전고점/최고가 관리 (Readme.MD 규칙)
        if highest[sym] is None:
            highest[sym] = price_now
            pastPeak[sym] = price_now
            in_downtrend[sym] = False

        # 최고가 갱신
        if price_now >= highest[sym]:
            highest[sym] = price_now
            # 상승장: 최고가 갱신 시 pastPeak는 그대로 유지
            # 단, 하락장에서 최고가를 돌파하면 pastPeak도 갱신
            if in_downtrend[sym]:
                pastPeak[sym] = highest[sym]
                in_downtrend[sym] = False
        elif price_now < highest[sym]:
            # 하락장 진입: pastPeak = highest
            if not in_downtrend[sym]:
                pastPeak[sym] = highest[sym]
                in_downtrend[sym] = True
            # 하락장에서 가격이 다시 상승장으로 전환될 때 pastPeak = 이 순간의 highest
            # (위의 if문에서 처리)
        # 상승장에서 가격이 최고가보다 낮아지는 순간, pastPeak = 현재가격
        if not in_downtrend[sym] and price_now < highest[sym]:
            pastPeak[sym] = price_now
            in_downtrend[sym] = True

        # delta만 계산 (전고점 기준)
        change = (price_now - pastPeak[sym]) / pastPeak[sym] * 100  # %

        alloc = get_change_alloc(change, CHANGE_ALLOC_TABLE, sym)
        # if change >= 0:
        #     alloc = get_upward_alloc(change, UPWARD_ALLOC_TABLE, sym)
        # else:
        #     alloc = get_dynamic_alloc(change, DRAWDOWN_ALLOC_TABLE, sym)
        # 디버깅/분석용 로그 (필요시 주석 해제)
        # print(
        #     f"[{reb_date.date()}] {sym}: pastPeak={pastPeak[sym]:.2f}, highest={highest[sym]:.2f}, now={price_now:.2f}, change={change:.3f} -> alloc={alloc:.3f}"
        # )
        growth_alloc[sym] = alloc
        growth_sum += alloc
    # 방어/균형/안정 자산 배분 (Readme.MD 최신 규칙 적용)
    defense_sum = 1.0 - growth_sum
    defense_alloc = {}

    if defense_sum > 0:
        for k, v in DYNAMIC_DEFENSE_WEIGHTS.items():
            defense_alloc[k] = defense_sum * v
    else:
        defense_alloc = {k: 0.0 for k in DYNAMIC_DEFENSE_WEIGHTS.keys()}
    # 목표 비중 통합
    return {**growth_alloc, **defense_alloc}

    # # 성장자산별 전고점/전저점 추적 및 drawdown/upward 계산
    # growth_alloc = {}
    # growth_sum = 0.0

    # # 각 자산별 전고점(pastPeak) 및 역대 최고가(highest) 상태 관리
    # if "pastPeak" not in locals():
    #     pastPeak = {sym: None for sym in GROWTH_ASSETS}
    #     highest = {sym: None for sym in GROWTH_ASSETS}
    #     in_downtrend = {sym: False for sym in GROWTH_ASSETS}

    # for sym in GROWTH_ASSETS:
    #     price_series = price_data[sym]["price"]
    #     price_now = price_series[price_series.index <= reb_date].iloc[-1]

    #     # 전고점/최고가 관리 (Readme.MD 규칙)
    #     if highest[sym] is None:
    #         highest[sym] = price_now
    #         pastPeak[sym] = price_now
    #         in_downtrend[sym] = False

    #     # 최고가 갱신
    #     if price_now >= highest[sym]:
    #         highest[sym] = price_now
    #         # 상승장: 최고가 갱신 시 pastPeak는 그대로 유지
    #         # 단, 하락장에서 최고가를 돌파하면 pastPeak도 갱신
    #         if in_downtrend[sym]:
    #             pastPeak[sym] = highest[sym]
    #             in_downtrend[sym] = False
    #     elif price_now < highest[sym]:
    #         # 하락장 진입: pastPeak = highest
    #         if not in_downtrend[sym]:
    #             pastPeak[sym] = highest[sym]
    #             in_downtrend[sym] = True
    #         # 하락장에서 가격이 다시 상승장으로 전환될 때 pastPeak = 이 순간의 highest
    #         # (위의 if문에서 처리)
    #     # 상승장에서 가격이 최고가보다 낮아지는 순간, pastPeak = 현재가격
    #     if not in_downtrend[sym] and price_now < highest[sym]:
    #         pastPeak[sym] = price_now
    #         in_downtrend[sym] = True

    #     # delta만 계산 (전고점 기준)
    #     change = (price_now - pastPeak[sym]) / pastPeak[sym] * 100  # %
    #     if change >= 0:
    #         alloc = get_upward_alloc(change, UPWARD_ALLOC_TABLE, sym)
    #     else:
    #         alloc = get_dynamic_alloc(change, DRAWDOWN_ALLOC_TABLE, sym)
    #     # 디버깅/분석용 로그 (필요시 주석 해제)
    #     # print(
    #     #     f"[{reb_date.date()}] {sym}: pastPeak={pastPeak[sym]:.2f}, highest={highest[sym]:.2f}, now={price_now:.2f}, change={change:.3f} -> alloc={alloc:.3f}"
    #     # )
    #     growth_alloc[sym] = alloc
    #     growth_sum += alloc
    # # 방어/균형/안정 자산 배분 (Readme.MD 최신 규칙 적용)
    # defense_sum = 1.0 - growth_sum
    # defense_alloc = {}
    # if defense_sum > 0:
    #     defense_alloc[Symbol.USDT] = defense_sum * (2 / 3)
    #     defense_alloc[Symbol.BOND_ANNUAL_3_5] = defense_sum * (1 / 12)
    #     defense_alloc[Symbol.GOLD] = defense_sum * (1 / 6)
    #     defense_alloc[Symbol.TLT] = defense_sum * (1 / 12)
    # else:
    #     defense_alloc = {k: 0.0 for k in DEFENSE_ASSETS}
    # # 목표 비중 통합
    # target_alloc = {**growth_alloc, **defense_alloc}
    # # 자산별 현재가
    # prices_now = {}
    # for sym in target_alloc:
    #     df = price_data.get(sym)
    #     if df is not None:
    #         price_row = df[df.index <= reb_date].iloc[-1]
    #         prices_now[sym] = price_row["price"]
    #     else:
    #         prices_now[sym] = 1.0  # 현금 등
    # # 전체 자산가치
    # total_value = cash + sum(portfolio[sym] * prices_now[sym] for sym in portfolio)
    # # 목표 비중에 맞춰 리밸런싱
    # for sym in portfolio:
    #     portfolio[sym] = (total_value * target_alloc.get(sym, 0)) / prices_now.get(
    #         sym, 1.0
    #     )
    # # ===== 리밸런싱 후, 다음 리밸런싱일까지 복리 이자율 적용 =====
    # # 성장자산(ETF/코인 등) 가격 변동 반영
    # for sym in portfolio.keys():
    #     # 성장자산만 가격 변동 반영 (이자형 자산은 아래에서 따로 처리)
    #     if sym in price_data and sym not in [Symbol.USDT, Symbol.BOND_ANNUAL_3_5]:
    #         df = price_data[sym]
    #         try:
    #             price_start = df[df.index <= reb_date].iloc[-1]["price"]
    #             price_end = df[df.index <= next_date].iloc[-1]["price"]
    #             portfolio[sym] *= price_end / price_start
    #         except Exception as e:
    #             # 데이터 누락 등 예외 발생 시 경고 출력 후 스킵
    #             print(f"[경고] {sym} 자산의 가격 변동 반영 실패: {e}")
    #             continue
    # # USDT(플립스터) 복리 이자율 적용 (예: 연 7%)
    # if Symbol.USDT in portfolio:
    #     portfolio[Symbol.USDT] *= (1 + USDT_APR / 365) ** days
    # # 채권 복리 이자율 적용
    # if Symbol.BOND_ANNUAL_3_5 in portfolio:
    #     portfolio[Symbol.BOND_ANNUAL_3_5] *= (1 + BOND_ANNUAL_3_5_APR) ** (days / 365)
    # # 기타 이자율 자산이 있다면 동일하게 추가 적용
    # # 자산별 평가액 기록
    # asset_values = {
    #     sym: round(portfolio[sym] * prices_now[sym], 3) for sym in portfolio
    # }
    # asset_values["dynamic_rebalance"] = sum(asset_values.values())
    # asset_values["dynamic_rebalance_change"] = change
    # asset_values["date"] = reb_date
    # history.append(asset_values)


# =====================
# 테스트 함수
# =====================
def test_get_change_alloc():
    """
    get_upward_alloc 함수의 단위 테스트
    - upward 값이 특정 구간에 속하면 해당 구간의 값을 계속 반환하는지 검증
    """
    assert get_change_alloc(3, CHANGE_ALLOC_TABLE, Symbol.QQQ) == 0.20
    assert get_change_alloc(5, CHANGE_ALLOC_TABLE, Symbol.QQQ) == 0.18
    assert get_change_alloc(7, CHANGE_ALLOC_TABLE, Symbol.QQQ) == 0.18
    assert get_change_alloc(10, CHANGE_ALLOC_TABLE, Symbol.QQQ) == 0.16
    assert get_change_alloc(12, CHANGE_ALLOC_TABLE, Symbol.QQQ) == 0.16
    assert get_change_alloc(15, CHANGE_ALLOC_TABLE, Symbol.QQQ) == 0.14
    assert get_change_alloc(40, CHANGE_ALLOC_TABLE, Symbol.QQQ) == 0.12
    logger.debug("[테스트] get_upward_alloc 정상 동작 확인")
