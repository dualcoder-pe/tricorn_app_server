### Experiments

<details>
<summary>Experiment 1</summary>

```
DYNAMIC_ASSET_ALLOC = {
    Symbol.SPY: 0.20,
    Symbol.QQQ: 0.20,
    Symbol.SCHD: 0.20,
    Symbol.BTC: 0.05,
    Symbol.GOLD: 0.05,  # 금 ETF
    Symbol.TLT: 0.05,  # 20년물 국채 ETF
}

STATIC_ASSET_ALLOC = {
    Symbol.USDT: 0.25,  # 연 7% 일복리 채권
    # Symbol.BOND_ANNUAL_3_5: 0.05,  # 연 3.5% 연복리 발행어음
}

2025-05-29 00:33:58 [INFO] rebalance: [buy & hold 결과]
2025-05-29 00:33:58 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-29 00:33:58 [INFO] rebalance: - 최종 자산가치: 52,053.12만원
2025-05-29 00:33:58 [INFO] rebalance: - 누적 수익률: 433.78%
2025-05-29 00:33:58 [INFO] rebalance: - CAGR: 15.80%
2025-05-29 00:33:58 [INFO] rebalance: - 최대 낙폭(MDD): -46.14%
2025-05-29 00:33:58 [INFO] rebalance: - Calmar: 0.34%
2025-05-29 00:33:58 [INFO] rebalance: - 샤프지수: 1.25

2025-05-29 00:33:58 [INFO] rebalance: [정적 리밸런싱 결과]
2025-05-29 00:33:58 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-29 00:33:58 [INFO] rebalance: - 최종 자산가치: 25,790.92만원
2025-05-29 00:33:58 [INFO] rebalance: - 누적 수익률: 214.92%
2025-05-29 00:33:58 [INFO] rebalance: - CAGR: 7.95%
2025-05-29 00:33:58 [INFO] rebalance: - 최대 낙폭(MDD): -13.50%
2025-05-29 00:33:58 [INFO] rebalance: - Calmar: 0.59%
2025-05-29 00:33:58 [INFO] rebalance: - 샤프지수: 1.29

```

```
DYNAMIC_ASSET_ALLOC = {
    Symbol.SPY: 0.20,
    Symbol.QQQ: 0.20,
    Symbol.SCHD: 0.20,
    Symbol.BTC: 0.05,
    Symbol.GOLD: 0.1,  # 금 ETF
    Symbol.TLT: 0.05,  # 20년물 국채 ETF
}

STATIC_ASSET_ALLOC = {
    Symbol.USDT: 0.20,  # 연 7% 일복리 채권
    # Symbol.BOND_ANNUAL_3_5: 0.05,  # 연 3.5% 연복리 발행어음
}

2025-05-29 00:36:28 [INFO] rebalance: [buy & hold 결과]
2025-05-29 00:36:28 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-29 00:36:28 [INFO] rebalance: - 최종 자산가치: 52,488.05만원
2025-05-29 00:36:28 [INFO] rebalance: - 누적 수익률: 437.40%
2025-05-29 00:36:28 [INFO] rebalance: - CAGR: 15.90%
2025-05-29 00:36:28 [INFO] rebalance: - 최대 낙폭(MDD): -46.34%
2025-05-29 00:36:28 [INFO] rebalance: - Calmar: 0.34%
2025-05-29 00:36:28 [INFO] rebalance: - 샤프지수: 1.25

2025-05-29 00:36:28 [INFO] rebalance: [정적 리밸런싱 결과]
2025-05-29 00:36:28 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-29 00:36:28 [INFO] rebalance: - 최종 자산가치: 26,436.39만원
2025-05-29 00:36:28 [INFO] rebalance: - 누적 수익률: 220.30%
2025-05-29 00:36:28 [INFO] rebalance: - CAGR: 8.22%
2025-05-29 00:36:28 [INFO] rebalance: - 최대 낙폭(MDD): -14.29%
2025-05-29 00:36:28 [INFO] rebalance: - Calmar: 0.58%
2025-05-29 00:36:28 [INFO] rebalance: - 샤프지수: 1.29

```

```
DYNAMIC_ASSET_ALLOC = {
    Symbol.SPY: 0.20,
    Symbol.QQQ: 0.20,
    Symbol.SCHD: 0.20,
    Symbol.BTC: 0.05,
    Symbol.GOLD: 0.1,  # 금 ETF
    Symbol.TLT: 0.05,  # 20년물 국채 ETF
}

STATIC_ASSET_ALLOC = {
    Symbol.USDT: 0.20,  # 연 7% 일복리 채권
    # Symbol.BOND_ANNUAL_3_5: 0.05,  # 연 3.5% 연복리 발행어음
}

2025-05-29 00:41:16 [INFO] rebalance: [buy & hold 결과]
2025-05-29 00:41:16 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-29 00:41:16 [INFO] rebalance: - 최종 자산가치: 52,488.05만원
2025-05-29 00:41:16 [INFO] rebalance: - 누적 수익률: 437.40%
2025-05-29 00:41:16 [INFO] rebalance: - CAGR: 15.90%
2025-05-29 00:41:16 [INFO] rebalance: - 최대 낙폭(MDD): -46.34%
2025-05-29 00:41:16 [INFO] rebalance: - Calmar: 0.34%
2025-05-29 00:41:16 [INFO] rebalance: - 샤프지수: 1.25

2025-05-29 00:41:16 [INFO] rebalance: [정적 리밸런싱 결과]
2025-05-29 00:41:16 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-29 00:41:16 [INFO] rebalance: - 최종 자산가치: 26,436.39만원
2025-05-29 00:41:16 [INFO] rebalance: - 누적 수익률: 220.30%
2025-05-29 00:41:16 [INFO] rebalance: - CAGR: 8.22%
2025-05-29 00:41:16 [INFO] rebalance: - 최대 낙폭(MDD): -14.29%
2025-05-29 00:41:16 [INFO] rebalance: - Calmar: 0.58%
2025-05-29 00:41:16 [INFO] rebalance: - 샤프지수: 1.29
```
```
DYNAMIC_ASSET_ALLOC = {
    Symbol.SPY: 0.20,
    Symbol.QQQ: 0.20,
    Symbol.SCHD: 0.20,
    Symbol.BTC: 0.05,
    Symbol.GOLD: 0.1,  # 금 ETF
    # Symbol.TLT: 0.05,  # 20년물 국채 ETF
}

STATIC_ASSET_ALLOC = {
    Symbol.USDT: 0.25,  # 연 7% 일복리 채권
    # Symbol.BOND_ANNUAL_3_5: 0.05,  # 연 3.5% 연복리 발행어음
}


2025-05-29 00:42:51 [INFO] rebalance: [정적 리밸런싱 결과]
2025-05-29 00:42:51 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-29 00:42:51 [INFO] rebalance: - 최종 자산가치: 27,038.13만원
2025-05-29 00:42:51 [INFO] rebalance: - 누적 수익률: 225.32%
2025-05-29 00:42:51 [INFO] rebalance: - CAGR: 8.46%
2025-05-29 00:42:51 [INFO] rebalance: - 최대 낙폭(MDD): -12.97%
2025-05-29 00:42:51 [INFO] rebalance: - Calmar: 0.65%
2025-05-29 00:42:51 [INFO] rebalance: - 샤프지수: 1.30
```

```
DYNAMIC_ASSET_ALLOC = {
    Symbol.SPY: 0.20,
    Symbol.QQQ: 0.20,
    Symbol.SCHD: 0.20,
    Symbol.BTC: 0.05,
    Symbol.GOLD: 0.15,  # 금 ETF
    # Symbol.TLT: 0.05,  # 20년물 국채 ETF
}

STATIC_ASSET_ALLOC = {
    Symbol.USDT: 0.20,  # 연 7% 일복리 채권
    # Symbol.BOND_ANNUAL_3_5: 0.05,  # 연 3.5% 연복리 발행어음
}

2025-05-29 00:44:12 [INFO] rebalance: [정적 리밸런싱 결과]
2025-05-29 00:44:12 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-29 00:44:12 [INFO] rebalance: - 최종 자산가치: 27,709.50만원
2025-05-29 00:44:12 [INFO] rebalance: - 누적 수익률: 230.91%
2025-05-29 00:44:12 [INFO] rebalance: - CAGR: 8.73%
2025-05-29 00:44:12 [INFO] rebalance: - 최대 낙폭(MDD): -13.34%
2025-05-29 00:44:12 [INFO] rebalance: - Calmar: 0.65%
2025-05-29 00:44:12 [INFO] rebalance: - 샤프지수: 1.31
```
결론
 - TLT는 필요 없고, 그 돈을 금에 투자하는 것이 더 좋다.
 - 테더는 25% 유지하는 것이 좋다.
 - 최적의 비율은 다음과 같다.
   - SPY: 20%
   - QQQ: 20%
   - SCHD: 20%
   - BTC: 5%
   - GOLD: 10%
   - USDT: 25%
 - 최적의 비율에 의하면 안전자산인 GOLD, USDT의 비율은 2:5다.
</details>

<details>
<summary>Experiment 2</summary>
</details>