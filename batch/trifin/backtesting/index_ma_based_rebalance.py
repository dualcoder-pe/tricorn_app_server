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
    from index_based_rebalance import get_index_based_rebalance_history
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

# =====================
# 성장자산 구간별 비중 테이블 (dynamic_ma_based_rebalance.py에서 가져옴)
# =====================
GROWTH_WEIGHTS_BY_ZONE = {
    1: [0.27, 0.30],  # 1구간 이하
    2: [0.24, 0.27],  # 2구간
    3: [0.21, 0.24],  # 3구간
    4: [0.18, 0.21],  # 4구간
    5: [0.15, 0.18],  # 5구간 이상
    # 1: [0.22, 0.26],  # 1구간 이하
    # 2: [0.20, 0.24],  # 2구간
    # 3: [0.18, 0.22],  # 3구간
    # 4: [0.16, 0.20],  # 4구간
    # 5: [0.14, 0.18],  # 5구간
}

BTC_WEIGHTS = [0.05, 0.05]

INTEREST_WEIGHT = 0.4
INFLATION_WEIGHT = 0.2
UNEMPLOYMENT_WEIGHT = 0.2
VIX_WEIGHT = 0.2

MA_STEP = 5
DEFAULT_ZONE = 3


def normalize(value, min_val, max_val, range: list = [0, 1]):
    return max(range[0], min(range[1], (min_val - value) / (min_val - max_val)))


def normalize_inverse(value, min_val, max_val, range: list = [0, 1]):
    return max(range[0], min(range[1], (max_val - value) / (max_val - min_val)))


# =====================
# MA 구간 계산 함수 (dynamic_ma_based_rebalance.py에서 가져옴)
# =====================
def calc_ma_zone(price_df, date, window):
    """
    지정된 symbol의 가격 데이터에서 window 구간 최고/최저값 기준 현 위치 구간(1~5) 반환
    데이터 부족 시 3 반환
    """
    try:
        start_idx = price_df.index.get_loc(date)
    except KeyError:
        # 날짜가 없으면 가장 가까운 이전 날짜 사용
        start_idx = price_df.index.get_indexer([date], method="pad")[0]
    if start_idx - window + 1 < 0:
        return DEFAULT_ZONE
    window_prices = price_df.iloc[start_idx - window + 1: start_idx + 1]["price"]
    lowest = window_prices.min()
    highest = window_prices.max()
    price_now = window_prices.iloc[-1]
    if highest == lowest:
        return DEFAULT_ZONE
    step = (highest - lowest) / MA_STEP
    for zone in range(1, MA_STEP + 1):
        upper = lowest + step * zone
        if price_now <= upper or zone >= MA_STEP:
            return zone
    return DEFAULT_ZONE  # fallback


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

    interest_point = normalize_inverse(interest_rate, 1, 4)  # 금리 높을수록 수비적
    inflation_point = normalize_inverse(inflation_rate, 250, 300)
    unemployment_point = normalize_inverse(unemployment_rate, 5, 14)
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
            # score += 0.3 * (ma[sym][5] / ma[sym][20])  # 5일 MA가 20MA보다 높을수록 공격적 (단기추세 높으면 공격, 모멘텀)
            # score += 0.1 * momentum_point
            # score += 0.1 * midterm_zone_point
            # score += 0.1 * (1 - ma[sym][20] / ma[sym][120]) # 20일 MA가 120MA보다 높을수록 수비적 (오래 올랐으면 좀 자제)
            # score += 0.1 * ath_point  # 가격이 전고점에 가까울수록 수비적

            score += INTEREST_WEIGHT * interest_point
            score += INFLATION_WEIGHT * inflation_point  # 물가 높을수록 수비적
            score += UNEMPLOYMENT_WEIGHT * unemployment_point  # 실업률 높을수록 수비적
            score += VIX_WEIGHT * vix_point  # VIX 높을수록 수비적
            scores[sym] = max(0, min(score, 1))  # 위험 성향 점수: 0 ~ 1
    return scores


def allocate_growth_weights(scores, growth_alloc):
    """
    성장(공격) 자산에 대해 min/max 비율 기반 동적 비중 산출 (normalize)
    """

    return {
        # asset: growth_alloc.get(asset, 0.2) * scores.get(asset, 0.0)
        asset: growth_alloc[asset][0]
               + (growth_alloc[asset][1] - growth_alloc[asset][0]) * scores.get(asset, 0.0)
        for asset in GROWTH_ASSETS
    }


def get_index_ma_based_rebalance_history(
        price_data,
        index_data,
        reb_date,
        days,
        cash,
        portfolio,
        history,
        is_cut_loss_dict=None
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
    prices_now = _get_latest_price(price_data, reb_date)

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

    target_alloc = _get_target_alloc(price_data, reb_date, prices_now, index_row, reb_date, is_cut_loss_dict)

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
        {"date": reb_date, "index_ma_based_rebalance": total_value, **asset_values}
    )


def get_today_index_ma_based_allocation(
        price_data: dict,
        index_data,
) -> dict:
    """
    오늘(최신 데이터 기준) 인덱스+MA 기반 투자전략 자산별 비중(total_ratio) 계산 함수

    :param price_data: 각 자산별 가격 데이터 (symbol: pd.DataFrame, index=date)
    :param index_data: macro 인덱스 데이터 (index=date)
    :return: {symbol: 비중(float)}

    예시:
        ratios = get_today_index_ma_based_allocation(price_data, index_data)
        # ratios: {Symbol.SPY: 0.21, Symbol.QQQ: 0.21, ...}
    """
    # 1) 최신 macro row 추출
    if index_data.empty:
        raise ValueError("index_data가 비어 있습니다.")
    index_row = index_data.iloc[-1]
    latest_macro_date = index_data.index[-1]

    # 2) 자산별 최신 가격 추출
    prices_now = _get_latest_price(price_data)

    return _get_target_alloc(price_data, latest_macro_date, prices_now, index_row)

def get_symbol_alloc(symbol, zone, is_cut_loss):
    if is_cut_loss is not None and symbol in is_cut_loss and is_cut_loss[symbol]:
        return [0.15, 0.15]
    if symbol == Symbol.BTC:
        return BTC_WEIGHTS
    else:
        return GROWTH_WEIGHTS_BY_ZONE.get(zone, [0.21, 0.24])


def _get_target_alloc(price_data, latest_date, prices_now, index_row, reb_date=None, is_cut_loss_dict=None):
    # 3) 성장자산별 전고점 대비 현재가
    price_ratios = {}
    for sym, df in price_data.items():
        valid_df = df[df.index <= reb_date] if reb_date is not None else df
        price_ratios[sym] = prices_now[sym] / valid_df["price"].max() if valid_df["price"].max() else 1.0

    # 4) MA 계산
    ma_windows = [5, 20, 60, 120]
    ma_dict = {}
    for sym, df in price_data.items():
        ma_dict[sym] = {}
        for w in ma_windows:
            # reb_date 기준 w일 이동평균
            df_valid = df[df.index <= reb_date] if reb_date is not None else df
            if len(df_valid) >= w:
                ma = df_valid["price"].iloc[-w:].mean()
            else:
                ma = df_valid["price"].mean() if not df_valid.empty else 0
            ma_dict[sym][w] = ma

    # 5) 성장자산별 60일 zone 계산
    zones_by_symbol = {}
    growth_alloc = {}
    for sym in DYNAMIC_ASSET_ALLOC.keys():
        w = 60
        try:
            zones_by_symbol[sym] = calc_ma_zone(price_data[sym], latest_date, w)
        except Exception as e:
            logger.warning(f"[zone 계산 실패] {sym} {w}: {e}")
            zones_by_symbol[sym] = DEFAULT_ZONE
        growth_alloc[sym] = get_symbol_alloc(sym, zones_by_symbol[sym], is_cut_loss_dict)

    # 6) 성장(공격) 자산 위험점수 및 목표 비중 계산
    scores = calculate_asset_score(
        price_now=prices_now,
        price_ratios=price_ratios,
        interest_rate=index_row["^TNX"],
        inflation_rate=index_row["CPIAUCSL"],
        unemployment_rate=index_row["UNRATE"],
        vix=index_row["^VIX"],
        ma=ma_dict,
    )
    growth_weights = allocate_growth_weights(scores, growth_alloc)
    growth_sum = sum(growth_weights.values())

    # 7) 방어/안정 자산 비중 배분 (잔여 비중)
    defense_sum = 1.0 - growth_sum
    defense_alloc = {}
    if defense_sum > 0:
        for k, v in DYNAMIC_DEFENSE_WEIGHTS.items():
            defense_alloc[k] = defense_sum * v
    else:
        defense_alloc = {k: 0.0 for k in DYNAMIC_DEFENSE_WEIGHTS.keys()}

    # 8) 목표 비중 통합
    total_ratio = {**growth_weights, **defense_alloc}
    return total_ratio


def _get_latest_price(price_data, latest_date=None):
    prices_now = {}
    for sym in DYNAMIC_ASSET_ALLOC.keys():
        df = price_data[sym]

        if df.empty:
            raise ValueError(f"{sym}의 price_data가 비어 있습니다.")

        if latest_date is None:
            price_row = df.iloc[-1]
        else:
            price_row = df[df.index <= latest_date].iloc[-1]
        prices_now[sym] = price_row["price"]
    return prices_now
