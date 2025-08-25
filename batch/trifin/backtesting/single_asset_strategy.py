
def run_single_asset_strategy(
        price_data, reb_date, cash, portfolio, history, symbol, label, days=None
):
    """
    단일 자산 몰빵 전략: 매월 현금이 들어오면 해당 자산만 매수(수량 누적), 평가일 가격/이자만 반영
    - USDT: 연 5% 일복리 이자만 적용
    - BOND_ANNUAL_3_5: 연 3.5% 연복리 이자만 적용
    - 나머지: 가격 데이터로 수량 누적/평가
    """
    from batch.trifin.backtesting import USDT_APR, BOND_ANNUAL_3_5_APR
    from batch.trifin.backtesting.data.symbol import Symbol

    if symbol == "USDT":
        # USDT: 현금만 누적, 일복리 이자 적용
        if cash > 0:
            portfolio["USDT"] += cash
        if days is None:
            days = 30  # fallback
        portfolio["USDT"] *= (1 + USDT_APR / 365) ** days
        value = portfolio["USDT"]
        history.append({"date": reb_date, label: round(value, 3)})
        return
    elif symbol == Symbol.BOND_ANNUAL_3_5:
        # 채권: 현금만 누적, 연복리 이자 적용
        if cash > 0:
            portfolio[symbol] += cash
        if days is None:
            days = 30
        portfolio[symbol] *= (1 + BOND_ANNUAL_3_5_APR) ** (days / 365)
        value = portfolio[symbol]
        history.append({"date": reb_date, label: round(value, 3)})
        return
    else:
        # 일반 성장자산: 가격 기반 수량 누적/평가
        if cash > 0:
            df = price_data[symbol]
            price = df[df.index <= reb_date].iloc[-1]["price"]
            portfolio[symbol] += cash / price
        price = price_data[symbol][price_data[symbol].index <= reb_date].iloc[-1][
            "price"
        ]
        value = portfolio[symbol] * price
        history.append({"date": reb_date, label: round(value, 3)})
