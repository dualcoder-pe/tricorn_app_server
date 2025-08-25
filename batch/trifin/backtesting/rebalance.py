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
)
from batch.trifin.backtesting.dynamic_ma_based_rebalance import (
    get_dynamic_ma_based_rebalance_history,
)
from batch.trifin.backtesting.dynamic_rebalance import get_dynamic_rebalance_history
from batch.trifin.backtesting.index_based_rebalance import get_index_based_rebalance_history
from batch.trifin.backtesting.index_ma_based_rebalance import get_index_ma_based_rebalance_history, get_today_index_ma_based_allocation
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
def run_backtesting():
    include_single_asset = False
    onetime_invest = True
    """
    10년간 매월 15일 리밸런싱하며 누적/연환산 수익률 계산
    """
    # 1. 가격 데이터 준비
    price_data = load_all_prices(START_DATE_WITH_GAP, END_DATE)
    rebalance_dates = generate_rebalance_dates(START_DATE, END_DATE)
    index_data = load_all_macro_indices(START_DATE_WITH_GAP, END_DATE)

    # 2. 포트폴리오 초기화
    cash = INIT_PORTFOLIO

    buy_and_hold_portfolio = {k: 0.0 for k in TOTAL_ASSETS.keys()}
    static_portfolio = {k: 0.0 for k in TOTAL_ASSETS.keys()}
    dynamic_portfolio = {k: 0.0 for k in TOTAL_ASSETS.keys()}

    windows = [5, 20, 60, 120]
    dynamic_ma_portfolios = []
    for _ in range(len(windows) + 1):
        dynamic_ma_portfolios.append({k: 0.0 for k in TOTAL_ASSETS.keys()})

    index_based_portfolio = {k: 0.0 for k in TOTAL_ASSETS.keys()}
    index_ma_based_portfolio = {k: 0.0 for k in TOTAL_ASSETS.keys()}

    buy_and_hold_history = []
    static_history = []
    dynamic_history = []
    dynamic_ma_based_history = []
    index_based_history = []
    index_ma_based_history = []

    # 3. 매월 리밸런싱
    single_asset_portfolios_mem = {}
    single_asset_histories_mem = {}
    for i, reb_date in enumerate(rebalance_dates):
        # prev_date는 첫 번째 리밸런싱 시 rebalance_dates[0]로 대체(혹은 None 처리)
        if i == 0:
            prev_date = rebalance_dates[0]
        else:
            prev_date = rebalance_dates[i - 1]
        # days는 prev_date ~ reb_date 구간의 일수
        days = (reb_date - prev_date).days

        get_buy_and_hold(
            price_data,
            reb_date,
            days,
            cash,
            buy_and_hold_portfolio,
            buy_and_hold_history,
        )
        get_static_rebalance_history(
            price_data,
            reb_date,
            days,
            cash,
            static_portfolio,
            static_history,
        )
        get_dynamic_rebalance_history(
            price_data, reb_date, days, cash, dynamic_portfolio, dynamic_history
        )
        get_dynamic_ma_based_rebalance_history(
            price_data,
            reb_date,
            days,
            cash,
            dynamic_ma_portfolios,
            dynamic_ma_based_history,
            windows,
        )
        get_index_based_rebalance_history(
            price_data,
            index_data,
            reb_date,
            days,
            cash,
            index_based_portfolio,
            index_based_history,
        )
        get_index_ma_based_rebalance_history(
            price_data,
            index_data,
            reb_date,
            days,
            cash,
            index_ma_based_portfolio,
            index_ma_based_history,
        )

        if onetime_invest:
            cash = 0

        if include_single_asset:
            # 단일 자산 몰빵 전략들 (QQQ, GOLD, SPY, SCHD, BTC, USDT, TLT)
            from batch.trifin.backtesting.data.symbol import Symbol

            single_asset_cases = [
                (Symbol.QQQ, "qqq_only"),
                (Symbol.GOLD, "gold_only"),
                (Symbol.SPY, "spy_only"),
                (Symbol.SCHD, "schd_only"),
                (Symbol.BTC, "btc_only"),
                (Symbol.TLT, "tlt_only"),
                (Symbol.BOND_ANNUAL_3_5, "bond_only"),
                ("USDT", "usdt_only"),  # USDT는 심볼에서 제외, 별도 처리
            ]
            single_asset_portfolios = {
                label: {k: 0.0 for k in TOTAL_ASSETS.keys()}
                for _, label in single_asset_cases
            }
            single_asset_histories = {label: [] for _, label in single_asset_cases}

            if i == 0:
                single_asset_portfolios_mem = single_asset_portfolios.copy()
                single_asset_histories_mem = single_asset_histories.copy()
            else:
                single_asset_portfolios = single_asset_portfolios_mem.copy()
                single_asset_histories = single_asset_histories_mem.copy()

            for symbol, label in single_asset_cases:
                run_single_asset_strategy(
                    price_data,
                    reb_date,
                    cash,
                    single_asset_portfolios[label],
                    single_asset_histories[label],
                    symbol,
                    label,
                    days,
                )

    ratio = get_today_index_ma_based_allocation(price_data, index_data)

    df_buy_and_hold_hist = pd.DataFrame(buy_and_hold_history)
    df_buy_and_hold_hist.set_index("date", inplace=True)
    df_static_hist = pd.DataFrame(static_history)
    df_static_hist.set_index("date", inplace=True)
    df_dynamic_hist = pd.DataFrame(dynamic_history)
    df_dynamic_hist.set_index("date", inplace=True)
    df_dynamic_ma_based_hist = pd.DataFrame(dynamic_ma_based_history)
    df_dynamic_ma_based_hist.set_index("date", inplace=True)
    df_index_based_hist = pd.DataFrame(index_based_history)
    df_index_based_hist.set_index("date", inplace=True)
    df_index_ma_based_hist = pd.DataFrame(index_ma_based_history)
    df_index_ma_based_hist.set_index("date", inplace=True)

    # 단일 자산 전략 결과 DataFrame 생성 및 합치기
    single_asset_histories = getattr(run_backtesting, "single_asset_histories", {})
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

    # ====== 공통 함수로 결과 요약/저장/그래프 ======
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
    # 'index_ma_based_rebalance' 컬럼 제외 후 전달
    print_recommand_weight(
        df_index_ma_based_hist.drop(columns=["index_ma_based_rebalance"])
    )
    print_final_ratio(ratio)
    return df_hist
