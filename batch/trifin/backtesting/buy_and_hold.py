from batch.trifin.backtesting import USDT_APR, BOND_ANNUAL_3_5_APR
from batch.trifin.backtesting.config import DYNAMIC_ASSET_ALLOC, TOTAL_ASSETS, STATIC_ASSET_ALLOC
from batch.trifin.backtesting.data.symbol import Symbol


def get_buy_and_hold(price_data, reb_date, days, cash, portfolio, history):
    """
    [적립식 구매 백테스트 - 공통 로직 통일 버전]
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

    # 3) 현금(cash)을 자산별 목표 비중대로 분배하여 portfolio에 반영
    # 성장자산: 현금을 가격으로 나눠 수량 증가, 방어자산: 가치 증가
    if cash > 0:
        for sym in TOTAL_ASSETS:
            alloc = TOTAL_ASSETS[sym]
            if sym in prices_now:
                # 성장자산: 현금을 가격으로 나눠 수량 증가
                portfolio[sym] += (cash * alloc) / prices_now[sym]
            else:
                # 방어자산: 현금 비중만큼 가치 증가
                portfolio[sym] += cash * alloc

    # 4) 전체 자산 평가액 계산 (reb_date 기준, 이자 반영 후)
    total_value = sum(
        portfolio[dynamic_sym] * prices_now.get(dynamic_sym, 1.0)
        for dynamic_sym in DYNAMIC_ASSET_ALLOC.keys()
    ) + sum(portfolio[stable_sym] for stable_sym in STATIC_ASSET_ALLOC.keys())
    total_value = round(total_value, 3)
    history.append({"date": reb_date, "buy_and_hold": total_value})
