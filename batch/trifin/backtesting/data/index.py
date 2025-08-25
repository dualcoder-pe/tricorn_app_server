from enum import Enum


class Index(str, Enum):
    Interest = "DGS10"  # 10년 만기 미국 국채 금리
    CPI = "CPIAUCSL"  # 미국 소비자물가지수 (CPI)
    UNR = "UNRATE"  # 미국 실업률
    VIX = "VIXCLS"  # CBOE 변동성 지수 (VIX)


class IndexFromPrice(str, Enum):
    Interest = "^TNX"
    VIX = "^VIX"
