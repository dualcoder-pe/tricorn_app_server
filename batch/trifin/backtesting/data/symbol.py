from enum import Enum


class Symbol(str, Enum):
    QQQ = "QQQ"  # QQQ ETF
    SPY = "SPY"  # S&P500 ETF
    SCHD = "SCHD"  # 배당 ETF
    BTC = "BTC-USD"  # 비트코인
    GOLD = "GLD"  # 금 ETF
    TLT = "TLT"  # 미국 장기채 ETF
    BOND_ANNUAL_3_5 = "BOND_ANNUAL_3_5"  # 연 3.5% 이자 채권(가상)
    USDT = "USDT"
