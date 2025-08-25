import os
from datetime import datetime

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from matplotlib import pyplot as plt

from batch.trifin.backtesting.config import DYNAMIC_ASSET_ALLOC, REBALANCE_DAY
from batch.trifin.backtesting.data.index import Index as MacroIndex, IndexFromPrice
from lib.logger import get_logger
from src.config.db import get_db
from src.repository.models.index_table import Index
from src.repository.models.price_table import Price

logger = get_logger()


# =====================
# 가격 데이터 로딩 함수
# =====================
def load_price_history(symbol: str, start: datetime, end: datetime) -> pd.DataFrame:
    """
    지정 종목의 가격 데이터를 DB에서 읽어 DataFrame으로 반환
    :param symbol: 종목 심볼 (예: 'SPY')
    :param start: 시작일
    :param end: 종료일
    :return: index=timestamp, columns=[open, high, low, close, volume]
    """
    with get_db() as session:
        prices = (
            session.query(Price)
            .filter(Price.symbol == symbol)
            .filter(Price.timestamp >= start)
            .filter(Price.timestamp <= end)
            .order_by(Price.timestamp.asc())
            .all()
        )
    if not prices:
        raise ValueError(f"{symbol}의 가격 데이터가 없습니다.")
    df = pd.DataFrame(
        [
            {
                "timestamp": p.timestamp,
                "price": p.close,  # 종가 사용
            }
            for p in prices
        ]
    )
    df.set_index("timestamp", inplace=True)
    return df


# =====================
# 전체 가격 데이터 로딩
# =====================
def load_all_prices(start: datetime, end: datetime) -> dict:
    """
    모든 투자자산의 가격 히스토리를 dict로 반환
    :return: {symbol: DataFrame}
    """
    price_data = {}
    for sym in DYNAMIC_ASSET_ALLOC.keys():
        price_data[sym] = load_price_history(sym, start, end)
    return price_data


# =====================
# Macro 지표 데이터 로딩 함수
# =====================
def load_macro_index_history(
        symbol: str, start: datetime, end: datetime
) -> pd.DataFrame:
    """
    지정 macro 인덱스(symbol)의 기간별 값을 DataFrame으로 반환
    :param symbol: macro 인덱스 심볼 (예: 'DGS10')
    :param start: 시작일
    :param end: 종료일
    :return: index=date, columns=[value]
    """
    with get_db() as session:
        rows = (
            session.query(Index)
            .filter(Index.symbol == symbol)
            .filter(Index.date >= start.date())
            .filter(Index.date <= end.date())
            .order_by(Index.date.asc())
            .all()
        )
    if not rows:
        raise ValueError(f"{symbol}의 macro index 데이터가 없습니다.")
    df = pd.DataFrame([{"date": row.date, "value": row.value} for row in rows])
    df.set_index("date", inplace=True)
    return df


def load_all_macro_indices(start: datetime, end: datetime) -> pd.DataFrame:
    """
    여러 macro 인덱스(DGS10, CPIAUCSL, UNRATE, VIXCLS 등)를 모두 읽어 date-indexed DataFrame으로 반환
    :param symbols: macro 인덱스 심볼 리스트
    :param start: 시작일
    :param end: 종료일
    :return: index=date, columns=symbol별 value
    """
    all_dfs = []
    for sym in list(MacroIndex):
        df = load_macro_index_history(sym.value, start, end)
        df = df.rename(columns={"value": sym})
        all_dfs.append(df)
    for sym in list(IndexFromPrice):
        df = load_price_history(sym.value, start, end)
        # timestamp 컬럼을 'yyyy-mm-dd' 포맷 문자열로 변환하고, 컬럼명을 'date'로 변경
        df["date"] = df.index.date
        df = df.rename(columns={"price": sym})
        df.set_index("date", inplace=True)
        all_dfs.append(df)
    df_merged = pd.concat(all_dfs, axis=1)
    return df_merged


# =====================
# 리밸런싱 날짜 생성
# =====================
def generate_rebalance_dates(start: datetime, end: datetime) -> list:
    """
    매월 15일 기준 리밸런싱 날짜 리스트 생성
    """
    dates = []
    cur = start.replace(day=REBALANCE_DAY)
    if cur < start:
        cur += relativedelta(months=1)
    while cur <= end:
        dates.append(cur)
        cur += relativedelta(months=1)
    return dates


def print_final_ratio(ratio_dict: dict):
    for sym, ratio in ratio_dict.items():
        logger.info(f"{sym.name}: {ratio * 100:,.2f}%")
    import math
    assert math.isclose(sum(ratio_dict.values()), 1.0, rel_tol=1e-8)


def print_recommand_weight(df):
    df["total"] = df.sum(axis=1)
    ratio_df = df.drop(columns=["total"]).div(df["total"], axis=0)

    for sym in ratio_df.columns:
        logger.info(f"{sym}: {ratio_df[sym].min():,.2f} ~ {ratio_df[sym].max():,.2f}")
    logger.info("\n")
    for k, v in ratio_df.iloc[-1].items():
        logger.info(f"{k}: {v * 100:.2f}%")
    logger.info("\n")


def print_summary(
        df,
        years,
        cols_and_labels,
        monthly_contribution=100,
        onetime_invest=False,
):
    """
    결과 DataFrame에서 불입액, 자산가치, 수익률, CAGR, MDD를 계산/출력

    Parameters
    ----------
    예시:
        print_summary(df, 10, 'total_value', '동적 리밸런싱', monthly_contribution=100)

        :param df:pd.DataFrame
            전략별 자산가치 시계열 데이터프레임
        :param years:int
            전체 투자 연수
        :param cols_and_labels:str
            평가할 자산가치 컬럼명 (예: 'total_value', 'buy_and_hold' 등)
        :param monthly_contribution:float
            월별 불입액(만원 단위)
        :param onetime_invest:
    """

    if onetime_invest:
        total_contributed = monthly_contribution
    else:
        total_contributed = monthly_contribution * years * 12

    summary = []

    for column_name, strategy_name in cols_and_labels:
        final_value = df[column_name].iloc[-1]
        logger.info(f"[{strategy_name} 결과]")
        logger.info(f"- 총 불입액: {total_contributed:,.2f}만원")
        logger.info(f"- 최종 자산가치: {final_value:,.2f}만원")
        logger.info(f"- 누적 수익률: {(final_value / total_contributed) * 100:.2f}%")
        cagr = ((final_value / total_contributed) ** (1 / years) - 1) * 100
        logger.info(f"- CAGR: {cagr:.2f}%")
        mdd = get_mdd(df[column_name])
        logger.info(f"- 최대 낙폭(MDD): {mdd:.2f}%")
        logger.info(f"- Calmar: {cagr / (-1 * mdd) if mdd != 0 else 0:.2f}%\n")
        # sharpe_ratio = get_sharpe_ratio(df[column_name])
        # logger.info(f"- 샤프지수: {sharpe_ratio:.2f}\n")

        summary.append(
            {
                "strategy": strategy_name,
                "total_contributed": total_contributed,
                "final_value": final_value,
                "cumulative_return": (final_value / total_contributed) * 100,
                "cagr": cagr,
                "mdd": mdd,
                "calmar_ratio": cagr / (-1 * mdd) if mdd != 0 else 0,
                # "sharpe_ratio": sharpe_ratio,
            }
        )

    save_result_csv(pd.DataFrame(summary), "Summary")


def save_result_csv(df, name="Result"):
    result_dir = os.path.join(os.path.dirname(__file__), "../backtesting/result")
    os.makedirs(result_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_path = os.path.join(result_dir, f"{name}_{timestamp}.csv")
    df.to_csv(result_path, encoding="utf-8-sig")
    logger.info(f"[INFO] 결과가 {result_path}에 저장되었습니다.")


def plot_performance(df, cols_and_labels):
    plt.rcParams["font.family"] = "AppleGothic"
    plt.rcParams["axes.unicode_minus"] = False
    plt.figure(figsize=(14, 7))

    for column, label in cols_and_labels:
        plt.plot(df.index, df[column], label=label, linewidth=2)

    # for sym in list(Symbol):
    #     plt.plot(df.index, df[sym.value], label=sym.value, linewidth=2)

    plt.title("전략별 자산가치 추이")
    plt.xlabel("날짜")
    plt.ylabel("평가액(원화 기준)")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()


def print_asset_values(df, strategy_name="전략"):
    """
    각 전략별 심볼(자산)별 평가액을 마지막 시점 기준으로 요약 출력
    - df: 결과 DataFrame (index: date, columns: 자산명 + total_value)
    - strategy_name: 전략 이름
    예시:
        print_asset_values(df, "동적리밸런싱")
    """
    if df.empty:
        logger.warning(f"[{strategy_name}] 데이터가 없습니다.")
        return
    last = df.iloc[-1]
    logger.info(f"[{strategy_name} 자산별 평가액]")
    for col in df.columns:
        if col not in ("total_value", "date") and np.issubdtype(
                df[col].dtype, np.number
        ):
            logger.info(f"- {col}: {last[col]:,.0f}원")
    logger.info(f"- 총 자산가치: {last['total_value']:,.0f}원\n")


def get_mdd(df):
    rolling_max = df.cummax()
    drawdown = (df - rolling_max) / rolling_max
    return drawdown.min() * 100


def get_sharpe_ratio(
        df, risk_free_rate=0.035, invest_per_period=100, periods_per_year=12
):
    """
    적립식 투자(불입액 포함) 기준 월간 수익률 기반 샤프지수 계산
    Args:
        df (pd.Series): 각 시점의 총자산 시계열 (예: total_value)
        risk_free_rate (float): 연간 무위험 수익률 (기본값 0.035)
        invest_per_period (float): 한 시점마다 불입하는 금액 (기본값 100)
        periods_per_year (int): 1년 동안의 기간 수 (월별 데이터면 12)
    Returns:
        float: 샤프지수 (Sharpe Ratio)
    Example:
        sharpe = get_sharpe_ratio(df['total_value'])
    Note:
        - 적립식 투자(불입액 포함) 기준 월간 수익률 시계열로 샤프지수 계산
        - 총자산이 누적불입액보다 작아 음수 수익률이 나올 수 있음
        - 표준편차가 0일 경우 NaN을 반환
        - 첫 달은 수익률 계산에서 제외
    """

    try:
        n = len(df)
        if n < 2:
            raise ValueError("데이터가 2개 미만이면 샤프지수 계산 불가")
        # 매월 불입 후 기준 자산: 이전달 총자산 + 이번달 불입액
        prev_total = df.shift(1).fillna(0) + invest_per_period
        prev_total.iloc[0] = invest_per_period  # 첫 달은 불입액만
        # 월간 수익률 계산
        monthly_return = (df - prev_total) / prev_total
        monthly_return = monthly_return.iloc[1:]  # 첫 달 제외
        # 월간 무위험수익률
        rf_monthly = risk_free_rate / periods_per_year
        excess_return = monthly_return - rf_monthly
        # 연율화 평균 및 표준편차
        mean_excess = excess_return.mean() * periods_per_year
        std_excess = excess_return.std() * np.sqrt(periods_per_year)
        sharpe = mean_excess / std_excess if std_excess != 0 else np.nan
        return sharpe
    except Exception as e:
        logger.error(f"[ERROR][get_sharpe_ratio] 샤프지수 계산 중 오류 발생: {e}")
        return np.nan
