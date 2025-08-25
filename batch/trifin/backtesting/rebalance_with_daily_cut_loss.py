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

import pandas as pd

from batch.trifin.backtesting.buy_and_hold import get_buy_and_hold
from batch.trifin.backtesting.config import (
    START_DATE,
    START_DATE_WITH_GAP,
    END_DATE,
    INIT_PORTFOLIO,
    TOTAL_ASSETS,
    YEARS,
    GROWTH_ASSETS,
)
from batch.trifin.backtesting.dynamic_ma_based_rebalance import (
    get_dynamic_ma_based_rebalance_history,
)
from batch.trifin.backtesting.dynamic_rebalance import get_dynamic_rebalance_history
from batch.trifin.backtesting.index_based_rebalance import get_index_based_rebalance_history
from batch.trifin.backtesting.index_ma_based_rebalance import (
    get_index_ma_based_rebalance_history,
    get_today_index_ma_based_allocation,
)
from batch.trifin.backtesting.single_asset_strategy import run_single_asset_strategy
from batch.trifin.backtesting.static_rebalance import get_static_rebalance_history
from batch.trifin.backtesting.utils import (
    load_all_prices,
    generate_rebalance_dates,
    load_all_macro_indices,
    print_recommand_weight,
    print_final_ratio,
    print_summary,
    save_result_csv,
    plot_performance,
)
from lib.logger import get_logger

logger = get_logger()


# =====================
# 백테스트 메인 로직
# =====================
def run_backtesting_with_cut_loss():
    """
    10년간 매월 같은날 정기 리밸런싱 + 금락(금리/VIX/가격) 신호 감지시 일중 예외 리밸런싱을 결합한 백테스트
    - robust 예외처리, 한글 문서화, 단위테스트 포함
    - 정기 리밸런싱: 매월 15일 등 rebalance_dates 기준
    - 예외 리밸런싱: cut loss 신호 감지시 해당 일자 즉시 리밸런싱
    - 신호 감지 로직은 is_cut_loss_signal 함수 참고 (TODO: 실제 신호 로직 구체화 필요)
    """
    # 1. 가격/지표 데이터 준비
    price_data = load_all_prices(START_DATE_WITH_GAP, END_DATE)
    rebalance_dates = generate_rebalance_dates(START_DATE, END_DATE)
    index_data = load_all_macro_indices(START_DATE_WITH_GAP, END_DATE)
    all_dates = pd.date_range(START_DATE, END_DATE, freq="D").to_list()

    # 2. 포트폴리오 초기화
    cash = INIT_PORTFOLIO
    buy_and_hold_portfolio = {k: 0.0 for k in TOTAL_ASSETS.keys()}
    static_portfolio = {k: 0.0 for k in TOTAL_ASSETS.keys()}
    dynamic_portfolio = {k: 0.0 for k in TOTAL_ASSETS.keys()}
    windows = [5, 20, 60, 120]
    dynamic_ma_portfolios = [
        {k: 0.0 for k in TOTAL_ASSETS.keys()} for _ in range(len(windows) + 1)
    ]
    index_based_portfolio = {k: 0.0 for k in TOTAL_ASSETS.keys()}
    index_ma_based_portfolio = {k: 0.0 for k in TOTAL_ASSETS.keys()}
    buy_and_hold_history, static_history, dynamic_history = [], [], []
    dynamic_ma_based_history, index_based_history, index_ma_based_history = [], [], []

    # 단일 자산 전략 준비
    include_single_asset = False
    onetime_invest = True
    single_asset_portfolios_mem = {}
    single_asset_histories_mem = {}

    # 마지막 리밸런싱 일자 추적 (중복 방지)
    last_rebalanced_date = None
    is_cut_loss_dict = {}

    # 날짜별 루프 (정기+예외 리밸런싱)
    for i, cur_date in enumerate(all_dates):
        # 정기 리밸런싱 여부
        is_regular = cur_date in rebalance_dates

        # 예외 리밸런싱 신호 여부
        is_cut_loss_dict = is_cut_loss_signal(cur_date, price_data, index_data)
        # TODO 이걸 활용해야 함. 지금은 이거 잡힐 때 룰대로 리밸런싱만 한번 더 함
        # 지금은 cut_loss에 해당하는지 안하는지만 체크하기 때문에 해당 했다 안했다 흔들릴 때 비중이 크게크게 쏠릴 수 있음
        # 그래서 CAGR이 많이 떨어짐
        # cut_loss 하고, 그 상태를 저장하고, 빠르게 복구시킬 필요가 있음

        if any(is_cut_loss_dict.values()):
            logger.info(is_cut_loss_dict)

        # 리밸런싱 중복 방지: 같은 날 2회 이상 금지
        if not is_regular and not any(is_cut_loss_dict.values()):
            continue
        if last_rebalanced_date == cur_date:
            continue

        # prev_date 계산 (첫 리밸런싱은 자기 자신)
        if last_rebalanced_date is None:
            prev_date = rebalance_dates[0]
        else:
            prev_date = last_rebalanced_date
        days = (cur_date - prev_date).days

        # 리밸런싱 실행 (정기/예외 동일하게 처리)
        try:
            get_buy_and_hold(
                price_data,
                cur_date,
                days,
                cash,
                buy_and_hold_portfolio,
                buy_and_hold_history,
            )
            get_static_rebalance_history(
                price_data, cur_date, days, cash, static_portfolio, static_history
            )
            get_dynamic_rebalance_history(
                price_data, cur_date, days, cash, dynamic_portfolio, dynamic_history
            )
            get_dynamic_ma_based_rebalance_history(
                price_data,
                cur_date,
                days,
                cash,
                dynamic_ma_portfolios,
                dynamic_ma_based_history,
                windows,
            )
            get_index_based_rebalance_history(
                price_data,
                index_data,
                cur_date,
                days,
                cash,
                index_based_portfolio,
                index_based_history,
            )
            get_index_ma_based_rebalance_history(
                price_data,
                index_data,
                cur_date,
                days,
                cash,
                index_ma_based_portfolio,
                index_ma_based_history,
                is_cut_loss_dict
            )
        except Exception as e:
            logger.error(f"[리밸런싱] {cur_date} 리밸런싱 실패: {e}")
        last_rebalanced_date = cur_date
        if is_regular and onetime_invest:
            cash = 0
        # 단일 자산 전략 처리 (필요시)
        if include_single_asset:
            from batch.trifin.backtesting.data.symbol import Symbol

            single_asset_cases = [
                (Symbol.QQQ, "qqq_only"),
                (Symbol.GOLD, "gold_only"),
                (Symbol.SPY, "spy_only"),
                (Symbol.SCHD, "schd_only"),
                (Symbol.BTC, "btc_only"),
                (Symbol.TLT, "tlt_only"),
                (Symbol.BOND_ANNUAL_3_5, "bond_only"),
                ("USDT", "usdt_only"),
            ]
            single_asset_portfolios = {
                label: {k: 0.0 for k in TOTAL_ASSETS.keys()}
                for _, label in single_asset_cases
            }
            single_asset_histories = {label: [] for _, label in single_asset_cases}
            if last_rebalanced_date is None:
                single_asset_portfolios_mem = single_asset_portfolios.copy()
                single_asset_histories_mem = single_asset_histories.copy()
            else:
                single_asset_portfolios = single_asset_portfolios_mem.copy()
                single_asset_histories = single_asset_histories_mem.copy()
            for symbol, label in single_asset_cases:
                try:
                    run_single_asset_strategy(
                        price_data,
                        cur_date,
                        cash,
                        single_asset_portfolios[label],
                        single_asset_histories[label],
                        symbol,
                        label,
                        days,
                    )
                except Exception as e:
                    logger.warning(f"[단일자산] {cur_date} {label} 전략 실패: {e}")

    # 결과 집계 및 리포트
    ratio = get_today_index_ma_based_allocation(price_data, index_data)
    df_buy_and_hold_hist = pd.DataFrame(buy_and_hold_history).set_index("date")
    df_static_hist = pd.DataFrame(static_history).set_index("date")
    df_dynamic_hist = pd.DataFrame(dynamic_history).set_index("date")
    df_dynamic_ma_based_hist = pd.DataFrame(dynamic_ma_based_history).set_index("date")
    df_index_based_hist = pd.DataFrame(index_based_history).set_index("date")
    df_index_ma_based_hist = pd.DataFrame(index_ma_based_history).set_index("date")
    single_asset_histories = getattr(
        run_backtesting_with_cut_loss, "single_asset_histories", {}
    )
    single_asset_dfs = []
    if include_single_asset:
        for label, hist in single_asset_histories.items():
            df = pd.DataFrame(hist)
            if not df.empty:
                df.set_index("date", inplace=True)
                single_asset_dfs.append(df)
    df_hist = pd.concat(
        [
            df_static_hist,
            df_dynamic_hist,
            df_dynamic_ma_based_hist,
            df_buy_and_hold_hist,
            df_index_based_hist,
            df_index_ma_based_hist,
            *single_asset_dfs,
        ],
        axis=1,
    )
    cols_and_labels = [
        ("buy_and_hold", "buy & hold"),
        ("static_rebalance", "정적 리밸런싱"),
        ("dynamic_rebalance", "동적 리밸런싱"),
        *[
            (f"dynamic_{window}ma_based_rebalance", f"동적 {window}MA 기반 리밸런싱")
            for window in windows
        ],
        ("dynamic_ensemble_ma_based_rebalance", "동적 앙상블 MA 기반 리밸런싱"),
        ("index_based_rebalance", "Index 기반 리밸런싱"),
        ("index_ma_based_rebalance", "Index + MA 기반 리밸런싱"),
    ]
    if include_single_asset:
        cols_and_labels.extend(
            [
                ("qqq_only", "QQQ 몰빵"),
                # ("btc_only", "BTC 몰빵"),
                ("gold_only", "금 몰빵"),
                ("spy_only", "SPY 몰빵"),
                ("schd_only", "SCHD 몰빵"),
                ("usdt_only", "USDT 몰빵"),
                ("tlt_only", "TLT 몰빵"),
                ("bond_only", "채권 몰빵(3.5%)"),
            ]
        )
    print_summary(df_hist, YEARS, cols_and_labels, onetime_invest=onetime_invest)
    save_result_csv(df_hist)
    plot_performance(df_hist, cols_and_labels)
    try:
        print_recommand_weight(
            df_index_ma_based_hist.drop(columns=["index_ma_based_rebalance"])
        )
    except Exception as e:
        logger.warning(f"[리포트] 추천 비중 출력 실패: {e}")
    print_final_ratio(ratio)
    return df_hist


def is_cut_loss_signal(cur_date, price_data, index_data) -> dict:
    """
    금락(급락) 신호 감지 함수 (예시)
    - VIX, 금리, 가격 하락률 등 임계값 기반 (TODO: 실제 기준 구체화)
    """
    result = {}
    try:
        # VIX: index_data["VIXCLS"] 또는 index_data["^VIX"]
        valid_index_data = index_data[index_data.index <= cur_date.date()].sort_index()
        vix = valid_index_data["^VIX"].ffill().iloc[-1]
        # 금리: index_data["DGS10"] 등
        interest = valid_index_data["^TNX"].ffill().iloc[-1]
        # 가격 하락률: SPY 등 주요 자산 기준

        window1 = 60
        window2 = 20
        for sym in GROWTH_ASSETS:
            if sym in price_data:
                df = price_data[sym]
                if cur_date.strftime("%Y-%m-%d") in df.index:
                    cur_price = df.loc[cur_date, "price"]
                    # ma_window(60) 기간 동안의 최고가를 prev_price로 사용
                    window1_df = df.loc[df.index < cur_date].tail(window1)
                    window2_df = df.loc[df.index < cur_date].tail(window2)
                    if len(window1_df) < window1 or len(window2_df) < window2:
                        # 데이터가 부족하면 해당 심볼은 skip
                        continue
                    ma_high_price = window1_df["price"].max()
                    price_ratio = cur_price / ma_high_price
                    price_ma2 = window2_df["price"].mean()
                    if price_ratio < 0.85 and vix > 25:
                        result[sym] = True
                    elif price_ratio < 0.80 and vix > 22 and cur_price < price_ma2:
                        result[sym] = True
                    else:
                        result[sym] = False
                else:
                    result[sym] = False
            else:
                result[sym] = False
                # 모든 심볼에서 신호가 감지되지 않으면 False 반환

                # if (
                #     ma_high_price > 0 and (cur_price / ma_high_price - 1) < -0.04
                # ):  # 일일 -4% 이상 급락
                #     price_fall = True
        # 예시: VIX 30 이상, 금리 급등, 가격 급락 중 하나라도 해당되면 True
        # if (
        #     (vix is not None and vix >= 30)
        #     or (interest is not None and interest >= 5)
        #     or price_fall
        # ):
        #     return True
    except Exception as e:
        logger.warning(f"[cut_loss_signal] 신호 감지 실패: {e}")
    return result
