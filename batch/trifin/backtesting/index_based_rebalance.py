"""
index_based_rebalance.py

지표(매크로) 기반 동적 리밸런싱 전략 (v2)
- 성장(공격) 자산: macro/momentum score 기반 비율 리밸런싱 (allocate_weights 방식)
- 수비(방어) 자산: 남은 비중을 DEFENSE_WEIGHTS_RATIO로 분배
- 방어자산 이자/복리 반영

작성자: Cascade AI
버전: 1.0
변경이력:
- 최초 작성: 2025-05-29

사용 예시:
    from index_based_rebalance_v2 import get_index_based_rebalance_history_v2
"""

from batch.trifin.backtesting import USDT_APR, BOND_ANNUAL_3_5_APR
from batch.trifin.backtesting.config import (
    DYNAMIC_ASSET_ALLOC,
    STATIC_ASSET_ALLOC,
    DYNAMIC_DEFENSE_WEIGHTS,
    GROWTH_ASSETS,
)
from batch.trifin.backtesting.data.symbol import Symbol
from lib.logger import get_logger

logger = get_logger()

WEIGHTS = {
    Symbol.SPY: [0.15, 0.25],
    Symbol.QQQ: [0.15, 0.25],
    Symbol.SCHD: [0.15, 0.25],
    Symbol.BTC: [0.00, 0.0],
}

# MOMENTUM_WEIGHT = 0.2
MOMENTUM_WEIGHT = 0.0
# MIDTERM_ZONE_WEIGHT = 0.2
MIDTERM_ZONE_WEIGHT = 0.4
LONGTERM_HIGH_ZONE_WEIGHT = 0.0
ATH_WEIGHT = 0.0
# ATH_WEIGHT = 0.0
CPI_WEIGHT = 0.3
INFLATION_WEIGHT = 0.1
# INFLATION_WEIGHT = 0.2
UNEMPLOYMENT_WEIGHT = 0.1
# UNEMPLOYMENT_WEIGHT = 0.2
VIX_WEIGHT = 0.1


def normalize(value, min_val, max_val):
    return max(0, min(1, (min_val - value) / (min_val - max_val)))


def normalize_inverse(value, min_val, max_val):
    return max(0, min(1, (max_val - value) / (max_val - min_val)))


def calculate_asset_score(
        price_now,
        price_ratios,  # 각 자산별 전고점 대비 현재가 (0~1 사이)
        interest_rate,  # 미국 10년물 국채금리 (%)
        inflation_rate,  # 미국 CPI (%)
        unemployment_rate,  # 미국 실업률 (%)
        vix,  # VIX (공포지수)
        ma,  # 각 자산별 MA 정보 dict (예: {sym: {5: float, 20: float, ...}})
):
    """
    매크로 지표 및 가격비 기반 성장자산 위험 성향 점수 산출 (index_based_rebalance.py와 동일)
    """
    cpi_point = normalize_inverse(interest_rate, 1, 4)  # 금리 높을수록 수비적
    inflation_point = normalize_inverse(inflation_rate, 250, 300)
    unimployment_point = normalize_inverse(unemployment_rate, 4, 14)
    vix_point = normalize_inverse(vix, 10, 80)

    scores = {}
    for sym, price_ratio in price_ratios.items():
        if sym in GROWTH_ASSETS:
            momentum_point = normalize(
                price_now[sym] / ma[sym][20], 0.8, 1.2
            )  # 5일 MA가 20MA보다 높을수록 공격적 (단기추세 높으면 공격, 모멘텀)
            midterm_zone_point = normalize_inverse(
                price_now[sym] / ma[sym][60], 0.8, 1.2
            )  # 60일 MA 대비 현재가 (60일 이상 상승했을 때 공격적)
            ath_point = normalize(price_ratio, 0.8, 1.2)

            score = 0
            score += MOMENTUM_WEIGHT * momentum_point
            score += MIDTERM_ZONE_WEIGHT * midterm_zone_point
            score += LONGTERM_HIGH_ZONE_WEIGHT * (1 - ma[sym][20] / ma[sym][120])
            score += ATH_WEIGHT * ath_point  # 가격이 전고점에 가까울수록 수비적
            score += CPI_WEIGHT * cpi_point
            score += INFLATION_WEIGHT * inflation_point  # 물가 높을수록 수비적
            score += UNEMPLOYMENT_WEIGHT * unimployment_point  # 실업률 높을수록 수비적
            score += VIX_WEIGHT * vix_point  # VIX 높을수록 수비적
            scores[sym] = max(0, min(score, 1))  # 위험 성향 점수: 0 ~ 1
    return scores


def allocate_growth_weights(scores):
    """
    성장(공격) 자산에 대해 min/max 비율 기반 동적 비중 산출 (normalize)
    """
    return {
        asset: WEIGHTS[asset][0]
               + (WEIGHTS[asset][1] - WEIGHTS[asset][0]) * scores.get(asset, 0.0)
        for asset in WEIGHTS
    }


def get_index_based_rebalance_history(
        price_data,
        index_data,
        reb_date,
        days,
        cash,
        portfolio,
        history,
):
    """
    동적 인덱스 기반 리밸런싱 전략 v2 (공격자산: score 기반, 수비자산: 잔여 비중 비율)
    """
    # 1) reb_date 기준 macro row 찾기 (date 기준)
    reb_date_only = reb_date.date() if hasattr(reb_date, "date") else reb_date
    # reb_date_only 이하이면서 모든 컬럼이 NaN이 아닌 마지막 row를 찾음
    valid_rows = index_data.loc[
        (index_data.index <= reb_date_only) & index_data.notna().all(axis=1)
        ]
    index_row = valid_rows.iloc[-1] if not valid_rows.empty else None

    if index_row is None:
        logger.error(
            f"리밸런싱 날짜 {reb_date}에 해당하는 매크로 지표 데이터가 없습니다."
        )
        return
    # 2) 자산별 reb_date 시점 가격 구하기
    prices_now = {}
    for sym in DYNAMIC_ASSET_ALLOC.keys():
        df = price_data[sym]
        price_row = df[df.index <= reb_date].iloc[-1]
        prices_now[sym] = price_row["price"]
    # 3) 방어자산(USDT, 채권 등) 이자형 자산의 복리 이자 적용 (전달~이번달 days 기준)
    if Symbol.USDT in portfolio:
        portfolio[Symbol.USDT] *= (1 + USDT_APR / 365) ** days
    if Symbol.BOND_ANNUAL_3_5 in portfolio:
        portfolio[Symbol.BOND_ANNUAL_3_5] *= (1 + BOND_ANNUAL_3_5_APR) ** (days / 365)
    # 4) 전체 자산 평가액 계산 (reb_date 기준, 이자 반영 후)
    total_value = (
            cash
            + sum(
        portfolio.get(sym, 0) * prices_now.get(sym, 1.0)
        for sym in DYNAMIC_ASSET_ALLOC.keys()
    )
            + sum(portfolio.get(sym, 0) for sym in STATIC_ASSET_ALLOC.keys())
    )
    # 5) 성장(공격) 자산 위험점수 및 목표 비중 계산
    price_ratios = {
        sym: prices_now[sym] / df[df.index <= reb_date]["price"].max()
        for sym, df in price_data.items()
    }
    # MA 계산
    ma_windows = [5, 20, 60, 120]
    ma_dict = {}
    for sym, df in price_data.items():
        ma_dict[sym] = {}
        for w in ma_windows:
            # reb_date 기준 w일 이동평균
            df_valid = df[df.index <= reb_date]
            if len(df_valid) >= w:
                ma = df_valid["price"].iloc[-w:].mean()
            else:
                ma = df_valid["price"].mean() if not df_valid.empty else 0
            ma_dict[sym][w] = ma

    scores = calculate_asset_score(
        price_now=prices_now,
        price_ratios=price_ratios,
        interest_rate=index_row["DGS10"],
        inflation_rate=index_row["CPIAUCSL"],
        unemployment_rate=index_row["UNRATE"],
        vix=index_row["VIXCLS"],
        ma=ma_dict,
        # 필요시 zones_by_symbol=zones_by_symbol 등 인자 추가 가능
    )
    # 참고: zones_by_symbol, _zones 모두 동일 dict

    growth_weights = allocate_growth_weights(scores)
    growth_sum = sum(growth_weights.values())
    # 6) 방어/안정 자산 비중 배분 (잔여 비중)
    defense_sum = 1.0 - growth_sum
    defense_alloc = {}
    if defense_sum > 0:
        for k, v in DYNAMIC_DEFENSE_WEIGHTS.items():
            defense_alloc[k] = defense_sum * v
    else:
        defense_alloc = {k: 0.0 for k in DYNAMIC_DEFENSE_WEIGHTS.keys()}

    # 7) 목표 비중 통합
    target_alloc = {**growth_weights, **defense_alloc}

    # 8) 목표 비중에 맞춰 리밸런싱 (reb_date 시점 가격 기준)
    for sym in target_alloc:
        alloc = target_alloc.get(sym, 0.0)
        if sym in prices_now:
            # 성장자산: 목표 비중에 맞춰 수량 조정
            portfolio[sym] = (total_value * alloc) / prices_now.get(sym, 1.0)
        else:
            # 방어자산(채권/USDT): 가치 기반으로 조정
            portfolio[sym] = total_value * alloc
    # 9) 전체 자산 평가액 기록 (reb_date 시점)
    asset_values = {}
    for sym in target_alloc:
        if sym in prices_now:
            asset_values[sym] = portfolio[sym] * prices_now[sym]
        else:
            asset_values[sym] = portfolio[sym]
    total_value = round(sum(asset_values.values()), 3)
    history.append(
        {"date": reb_date, "index_based_rebalance": total_value, **asset_values}
    )
