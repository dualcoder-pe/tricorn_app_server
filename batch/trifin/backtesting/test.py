from datetime import datetime

from batch.trifin.backtesting import USDT_APR, BOND_ANNUAL_3_5_APR
from batch.trifin.backtesting.rebalance import generate_rebalance_dates


# =====================
# 단위테스트 코드 (pytest 등에서 활용)
# =====================
def test_generate_rebalance_dates():
    start = datetime(2020, 1, 1)
    end = datetime(2020, 4, 20)
    dates = generate_rebalance_dates(start, end)
    assert dates == [
        datetime(2020, 1, 15),
        datetime(2020, 2, 15),
        datetime(2020, 3, 15),
        datetime(2020, 4, 15),
    ]


def test_bond_daily_7():
    val = 1000
    days = 365
    # 1년 후
    after = val * (1 + USDT_APR / 365) ** days
    assert abs(after - 1070) < 1


def test_note_annual_3_5():
    val = 1000
    after = val * (1 + BOND_ANNUAL_3_5_APR)
    assert abs(after - 1035) < 1
