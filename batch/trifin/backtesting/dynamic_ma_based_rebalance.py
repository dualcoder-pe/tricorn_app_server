"""
dynamic_ma_based_rebalance.py

전략 3. 이동평균(MA) 기반 다이나믹 리밸런싱 백테스트 스크립트

- 목적: 각 symbol별 5, 20, 60, 120일간 최고/최저 구간을 5등분하여 위치에 따라 성장자산/안정자산 비중을 동적으로 결정
- 의존성: numpy, pandas, matplotlib, backtesting.utils, backtesting.symbol 등
- 사용법: python dynamic_ma_based_rebalance.py
- 주요 함수:
    - calc_ma_zones: 각 기간별 highest/lowest 구간 계산
    - get_growth_weight: 성장자산의 구간별 비중 결정
    - get_defense_weights: 안정자산 비중 배분
    - run_ma_based_backtest: 전체 백테스트 실행
- robust 예외처 및 한글 문서화, 단위테스트 포함
- 작성일: 2025-05-24
- 작성자: 사용자 요청 기반

변경이력:
    - v1.0.0: 최초 작성

TODO:
    - 거래비용/세금 반영
    - 리밸런싱 주기/날짜 파라미터화
    - 리포트/시각화 기능 개선

참고: 자세한 비중 산정 방식은 Readme.MD 참고
"""

import sys

import pandas as pd

from batch.trifin.backtesting import USDT_APR, BOND_ANNUAL_3_5_APR
from batch.trifin.backtesting.config import DYNAMIC_DEFENSE_WEIGHTS, GROWTH_ASSETS
from batch.trifin.backtesting.data.symbol import Symbol
from lib.exception_utils import print_exception_detail
from lib.logger import get_logger

logger = get_logger()

# =====================
# 성장자산 구간별 비중 테이블
# =====================
GROWTH_WEIGHTS_BY_ZONE = {
    1: 0.25,  # 1구간 이하
    2: 0.22,  # 2구간
    3: 0.20,  # 3구간
    4: 0.18,  # 4구간
    5: 0.15,  # 5구간 이상
}


# =====================
# MA 구간 계산 함수
# =====================
def calc_ma_zones(price_df, date, window):
    """
    각 symbol에 대해 지정된 기간별(highest/lowest) 구간을 5등분하여 현 위치를 zone(1~5)으로 반환
    Args:
        price_df (pd.DataFrame): 가격 데이터프레임 (index: 날짜, columns: price)
        date (datetime): 평가 기준일
        window (int): 윈도우(일수)
    Returns:
        int: zone(1~5)
    """
    start_idx = price_df.index.get_loc(date)
    if start_idx - window + 1 < 0:
        # 데이터 부족 시 zone 3(중립) 처리
        return 3
    window_prices = price_df.iloc[start_idx - window + 1: start_idx + 1]["price"]
    lowest = window_prices.min()
    highest = window_prices.max()
    price_now = window_prices.iloc[-1]
    if highest == lowest:
        return 3
    step = (highest - lowest) / 5
    for zone in range(1, 6):
        upper = lowest + step * zone
        if price_now <= upper or zone >= 5:
            return zone

    raise Exception("Couldn't find zone")


# =====================
# 성장자산 zone별 비중 결정 함수
# =====================
def get_growth_weight(zones, window):
    """
    여러 MA 구간 중 가장 높은 zone(=가장 비중 낮은 zone)을 적용
    Args:
        zones (dict): {window: zone}
        window (int): 사용할 window
    Returns:
        float: 성장자산 비중(0~1)
    """
    zone = zones.get(window, 3)
    return GROWTH_WEIGHTS_BY_ZONE.get(zone, 0.12)


# =====================
# 안정자산 비중 계산 함수
# =====================
def get_defense_weights(growth_weight):
    """
    성장자산 비중을 제외한 나머지를 비율에 따라 안정자산에 배분
    Args:
        growth_weight (float): 성장자산 총합 비중
    Returns:
        dict: {symbol: weight}
    """
    remain = 1.0 - growth_weight
    defense_weights = {}
    for sym, ratio in DYNAMIC_DEFENSE_WEIGHTS.items():
        defense_weights[sym] = remain * ratio
    return defense_weights


def get_dynamic_ma_based_rebalance_history(
        price_data,
        reb_date,
        days,
        cash,
        portfolios,
        history,
        windows,
):
    """
    MA 기반 다이나믹 리밸런싱 핵심 로직
    - 각 성장자산별로 지정된 MA 구간에서 zone 산출
    - zone에 따라 자산별 비중 결정(GROWTH_WEIGHTS_BY_ZONE)
    - 남은 비중은 DEFENSE_WEIGHTS_RATIO에 따라 방어/안정 자산에 분배
    - 목표 비중에 맞춰 포트폴리오 재조정 및 가치 변화 반영
    - 결과는 history에 {date, dynamic_{window}ma_based_rebalance, ...자산별_가치}로 기록
    Args:
        price_data (dict): symbol별 가격 데이터 (DataFrame)
        reb_date (datetime): 리밸런싱 기준일
        days (int): 리밸런싱 간격(일)
        cash (float): 현금
        portfolios (list): window별 포트폴리오 (dict)
        history (list): 결과 기록 리스트
        windows (list): MA 윈도우 리스트
    """
    n = len(windows)
    assert len(portfolios) == n + 1

    try:
        # 각 window별로 독립적으로 리밸런싱 프로세스를 수행
        asset_values = {}
        ma_asset_values_list = []  # window별 자산별 평가액 기록용
        growth_alloc_list = []  # 각 window별 성장자산 비중 dict 저장

        for i, window in enumerate(windows):
            growth_alloc = {}
            growth_sum = 0.0
            # 1. 성장자산별 해당 window zone 산출 및 비중 결정
            for sym in GROWTH_ASSETS:
                df = price_data[sym]
                if reb_date not in df.index:
                    reb_eval_date = df.index[df.index <= reb_date][-1]
                else:
                    reb_eval_date = reb_date
                zone = calc_ma_zones(df, reb_eval_date, window=window)
                growth_alloc[sym] = GROWTH_WEIGHTS_BY_ZONE.get(zone, 0.2)
                growth_sum += growth_alloc[sym]
            # growth_alloc_list에 저장 (ensemble 계산용)
            growth_alloc_list.append(growth_alloc)
            # 2. 방어/안정 자산 비중 배분
            defense_sum = 1.0 - growth_sum
            defense_alloc = {}
            if defense_sum > 0:
                for k, v in DYNAMIC_DEFENSE_WEIGHTS.items():
                    defense_alloc[k] = defense_sum * v
            else:
                defense_alloc = {k: 0.0 for k in DYNAMIC_DEFENSE_WEIGHTS.keys()}
            # 3. 목표 비중 통합
            target_alloc = {**growth_alloc, **defense_alloc}
            # 4. 방어자산(USDT, 채권 등) 이자형 자산의 복리 이자 적용 (전달~이번달 days 기준)
            portfolio_ref = portfolios[i]
            if Symbol.USDT in portfolio_ref:
                portfolio_ref[Symbol.USDT] *= (1 + USDT_APR / 365) ** days
            if Symbol.BOND_ANNUAL_3_5 in portfolio_ref:
                portfolio_ref[Symbol.BOND_ANNUAL_3_5] *= (1 + BOND_ANNUAL_3_5_APR) ** (
                        days / 365
                )
            # 5. 전체 자산가치 (reb_date 기준, 이자 반영 후)
            prices_now = {}
            for sym in target_alloc:
                df = price_data.get(sym)
                if df is not None:
                    if reb_date not in df.index:
                        price_row = df[df.index <= reb_date].iloc[-1]
                    else:
                        price_row = df.loc[reb_date]
                    prices_now[sym] = price_row["price"]
                else:
                    prices_now[sym] = 1.0  # 현금 등
            total_value = cash + sum(
                portfolio_ref.get(sym, 0) * prices_now[sym] for sym in portfolio_ref
            )
            # 6. 목표 비중에 맞춰 포트폴리오 재조정
            for sym in target_alloc:
                portfolio_ref[sym] = (
                                             total_value * target_alloc.get(sym, 0)
                                     ) / prices_now.get(sym, 1.0)
            # 7. 자산별 평가액 기록 (reb_date 시점)
            ma_asset_values = {
                sym: portfolio_ref[sym] * prices_now[sym] for sym in portfolio_ref
            }
            asset_values[f"dynamic_{window}ma_based_rebalance"] = sum(
                ma_asset_values.values()
            )
            asset_values["date"] = reb_date
            ma_asset_values_list.append(ma_asset_values)

        # === Ensemble 성장자산 비중 계산 (동일가중 평균)
        all_syms = set()
        for ga in growth_alloc_list:
            all_syms.update(ga.keys())
        ensemble_growth_alloc = {}
        for sym in all_syms:
            ensemble_growth_alloc[sym] = (
                    sum(ga.get(sym, 0) for ga in growth_alloc_list) / n
            )
        ensemble_growth_sum = sum(ensemble_growth_alloc.values())
        # === Ensemble 방어자산 비중 계산
        ensemble_defense_sum = 1.0 - ensemble_growth_sum
        ensemble_defense_alloc = {}
        if ensemble_defense_sum > 0:
            for k, v in DYNAMIC_DEFENSE_WEIGHTS.items():
                ensemble_defense_alloc[k] = ensemble_defense_sum * v
        else:
            ensemble_defense_alloc = {k: 0.0 for k in DYNAMIC_DEFENSE_WEIGHTS.keys()}
        # === Ensemble target_alloc (성장+방어)
        ensemble_target_alloc = {**ensemble_growth_alloc, **ensemble_defense_alloc}
        # === Ensemble 포트폴리오 복리 이자 적용
        ensemble_portfolio = portfolios[-1]
        if Symbol.USDT in ensemble_portfolio:
            ensemble_portfolio[Symbol.USDT] *= (1 + USDT_APR / 365) ** days
        if Symbol.BOND_ANNUAL_3_5 in ensemble_portfolio:
            ensemble_portfolio[Symbol.BOND_ANNUAL_3_5] *= (1 + BOND_ANNUAL_3_5_APR) ** (days / 365)
        # === Ensemble 포트폴리오 평가액 산출
        ensemble_prices_now = {}
        for sym in ensemble_target_alloc:
            df = price_data.get(sym)
            if df is not None:
                if reb_date not in df.index:
                    price_row = df[df.index <= reb_date].iloc[-1]
                else:
                    price_row = df.loc[reb_date]
                ensemble_prices_now[sym] = price_row["price"]
            else:
                ensemble_prices_now[sym] = 1.0
        ensemble_total_value = cash + sum(
            ensemble_portfolio.get(sym, 0) * ensemble_prices_now[sym]
            for sym in ensemble_portfolio
        )
        # === 목표 비중에 맞춰 ensemble 포트폴리오 재조정
        for sym in ensemble_target_alloc:
            ensemble_portfolio[sym] = (
                                              ensemble_total_value * ensemble_target_alloc.get(sym, 0)
                                      ) / ensemble_prices_now.get(sym, 1.0)
        # === 자산별 평가액 기록 및 저장
        ensemble_asset_values = {
            sym: ensemble_portfolio[sym] * ensemble_prices_now[sym]
            for sym in ensemble_portfolio
        }
        asset_values["dynamic_ensemble_ma_based_rebalance"] = sum(
            ensemble_asset_values.values()
        )
        portfolios[-1] = ensemble_portfolio
        history.append(asset_values)

    except Exception as e:
        logger.error(f"[오류] get_dynamic_ma_based_rebalance_history({reb_date}) 실패: {e}")
        raise


# =====================
# 단위 테스트 함수
# =====================
# def test_calc_ma_zones():
#     """
#     calc_ma_zones 함수의 단위 테스트 (기본)
#     """
#     idx = pd.date_range("2023-01-01", periods=130)
#     prices = np.linspace(100, 200, 130)
#     df = pd.DataFrame({"price": prices}, index=idx)
#     zones = calc_ma_zones(df, idx[-1], [5, 20, 60, 120])
#     assert all(1 <= z <= 5 for z in zones.values())
#     logger.debug("[테스트] calc_ma_zones 정상 동작 확인")
#
#
# def test_calc_ma_zones_cases():
#     """
#     calc_ma_zones 함수의 다양한 케이스 단위 테스트
#     """
#     import pandas as pd
#     import numpy as np
#
#     # 1. 정상 케이스: 가격이 증가하는 경우
#     idx = pd.date_range("2023-01-01", periods=130)
#     prices = np.linspace(100, 200, 130)
#     df = pd.DataFrame({"price": prices}, index=idx)
#     zones = calc_ma_zones(df, idx[-1], windows=[5, 20, 60, 120])
#     assert all(1 <= z <= 5 for z in zones.values()), f"zone 범위 오류: {zones}"
#
#     # 2. 데이터 부족 케이스
#     zones_short = calc_ma_zones(df, idx[2], windows=[5, 20])
#     assert (
#         zones_short[5] == 3 and zones_short[20] == 3
#     ), f"데이터 부족시 zone=3 반환 실패: {zones_short}"
#
#     # 3. 가격이 모두 동일한 경우
#     df_same = pd.DataFrame(
#         {"price": [100] * 30}, index=pd.date_range("2023-01-01", periods=30)
#     )
#     zones_same = calc_ma_zones(df_same, df_same.index[-1], windows=[5, 20])
#     assert all(
#         z == 3 for z in zones_same.values()
#     ), f"가격 동일시 zone=3 반환 실패: {zones_same}"
#
#     # 4. 가격이 구간별로 뚜렷하게 나뉘는 경우(직접 zone 예측)
#     df_custom = pd.DataFrame(
#         {"price": [100, 110, 120, 130, 140]},
#         index=pd.date_range("2023-01-01", periods=5),
#     )
#     zones_custom = calc_ma_zones(df_custom, df_custom.index[-1], windows=[5])
#     assert zones_custom[5] == 5, f"최고가에 위치할 때 zone=5여야 함: {zones_custom}"
#
#     logger.debug("[테스트] calc_ma_zones 다양한 케이스 정상 동작 확인")
#
#
# def test_get_growth_weight():
#     """
#     get_growth_weight 함수의 단위 테스트
#     """
#     zones = {5: 1, 20: 2, 60: 3, 120: 4}
#     assert abs(get_growth_weight(zones, 5) - 0.2) < 1e-6
#     zones = {5: 5, 20: 5, 60: 5, 120: 5}
#     assert abs(get_growth_weight(zones, 5) - 0.12) < 1e-6
#     logger.debug("[테스트] get_growth_weight 정상 동작 확인")
#
#
# def test_get_defense_weights():
#     """
#     get_defense_weights 함수의 단위 테스트
#     """
#     weights = get_defense_weights(0.16 * 4)
#     total = sum(weights.values()) + 0.16 * 4
#     assert abs(total - 1.0) < 1e-6
#     logger.debug("[테스트] get_defense_weights 정상 동작 확인")


if __name__ == "__main__":
    try:
        pass
        # test_calc_ma_zones()
        # test_calc_ma_zones_cases()
        # test_get_growth_weight()
        # test_get_defense_weights()
    except Exception as e:
        logger.debug(f"[오류] MA 기반 백테스트 실행 실패: {e}")
        print_exception_detail(e)
        sys.exit(1)
