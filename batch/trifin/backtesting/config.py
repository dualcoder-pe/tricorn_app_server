from datetime import datetime

from dateutil.relativedelta import relativedelta

from batch.trifin.backtesting.data.symbol import Symbol

# =====================
# 자산별 목표 비중 정의
# =====================
DYNAMIC_ASSET_ALLOC = {
    Symbol.SPY: 0.30,
    Symbol.QQQ: 0.30,
    Symbol.SCHD: 0.30,
    Symbol.BTC: 0.05,
    Symbol.GOLD: 0.025,  # 금 ETF
    # Symbol.TLT: 0.05,  # 20년물 국채 ETF
}

STATIC_ASSET_ALLOC = {
    Symbol.USDT: 0.025,  # 연 7% 일복리 채권
    # Symbol.BOND_ANNUAL_3_5: 0.05,  # 연 3.5% 연복리 발행어음
}

DYNAMIC_DEFENSE_WEIGHTS = {
    Symbol.USDT: 5 / 7,
    # Symbol.BOND_ANNUAL_3_5: 1 / 12,
    Symbol.GOLD: 2 / 7,
    # Symbol.TLT: 1 / 7,
}

GROWTH_ASSETS = DYNAMIC_ASSET_ALLOC.keys() - DYNAMIC_DEFENSE_WEIGHTS.keys()

HISTORICAL_MDD = {"QQQ": 0.35, "SPY": 0.33, "SCHD": 0.33, "BTC": 0.83}

assert (
        int((sum(DYNAMIC_ASSET_ALLOC.values()) + sum(STATIC_ASSET_ALLOC.values())) * 100000)
        == 100000
)

TOTAL_ASSETS = {**DYNAMIC_ASSET_ALLOC, **STATIC_ASSET_ALLOC}

# =====================
# 백테스트 파라미터
# =====================
REBALANCE_DAY = 15  # 매월 15일 리밸런싱
YEARS = 10
START_DATE = (datetime.now() - relativedelta(years=YEARS)).replace(
    hour=0, minute=0, second=0, microsecond=0
)
START_DATE_WITH_GAP = (datetime.now() - relativedelta(years=YEARS + 1)).replace(
    hour=0, minute=0, second=0, microsecond=0
)
END_DATE = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
INIT_PORTFOLIO = 100  # 시작금액(원화기준, 임의)
MONTHLY_CONTRIBUTION = 100  # 매월 불입액(원화)
