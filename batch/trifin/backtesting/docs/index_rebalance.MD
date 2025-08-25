### Experiments

<details>
<summary>Experiment 1</summary>

```
DEFENSE_WEIGHTS_RATIO = {
    Symbol.USDT: 5 / 7,
    Symbol.GOLD: 2 / 7,
}

score = 0
score += 0.40 * (1 - price_ratio)  # 가격이 전고점에 가까울수록 수비적
score += 0.30 * (1 - normalize_inverse(interest_rate, 0, 10)) # 금리 높을수록 수비적
score += 0.10 * (1 - normalize_inverse(inflation_rate, 100, 500)) # 물가 높을수록 수비적
score += 0.10 * (1 - normalize_inverse(unemployment_rate, 0, 50)) # 실업률 높을수록 수비적
score += 0.10 * (1 - normalize_inverse(vix, 0, 100))  # VIX 높을수록 수비적

min_weights = {
    Symbol.SPY: 0.15,
    Symbol.QQQ: 0.15,
    Symbol.SCHD: 0.15,
    Symbol.BTC: 0.04,
}
max_weights = {
    Symbol.SPY: 0.25,
    Symbol.QQQ: 0.25,
    Symbol.SCHD: 0.25,
    Symbol.BTC: 0.05,
}


2025-05-31 01:34:12 [INFO] rebalance: [Index 기반 리밸런싱 결과]
2025-05-31 01:34:12 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-31 01:34:12 [INFO] rebalance: - 최종 자산가치: 24,980.92만원
2025-05-31 01:34:12 [INFO] rebalance: - 누적 수익률: 208.17%
2025-05-31 01:34:12 [INFO] rebalance: - CAGR: 7.61%
2025-05-31 01:34:12 [INFO] rebalance: - 최대 낙폭(MDD): -9.86%
2025-05-31 01:34:12 [INFO] rebalance: - Calmar: 0.77%
2025-05-31 01:34:12 [INFO] rebalance: - 샤프지수: 1.29
```
```
은퇴 후
2025-05-31 02:15:17 [INFO] rebalance: [Index 기반 리밸런싱 결과]
2025-05-31 02:15:17 [INFO] rebalance: - 총 불입액: 100.00만원
2025-05-31 02:15:17 [INFO] rebalance: - 최종 자산가치: 375.46만원
2025-05-31 02:15:17 [INFO] rebalance: - 누적 수익률: 375.46%
2025-05-31 02:15:17 [INFO] rebalance: - CAGR: 14.14%
2025-05-31 02:15:17 [INFO] rebalance: - 최대 낙폭(MDD): -15.01%
2025-05-31 02:15:17 [INFO] rebalance: - Calmar: 0.94%
2025-05-31 02:15:17 [INFO] rebalance: - 샤프지수: 0.19
```

```
scores = {}
for sym, price_ratio in price_ratios.items():
    score = 0
    score += 0.3 * (ma[sym][5] / ma[sym][20])  # 5일 MA가 20MA보다 높을수록 공격적 (단기추세 높으면 공격, 모멘텀)
    score += 0.1 * (1 - ma[sym][20] / ma[sym][120]) # 20일 MA가 120MA보다 높을수록 수비적 (오래 올랐으면 좀 자제)
    score += 0.1 * (1 - price_ratio)  # 가격이 전고점에 가까울수록 수비적
    score += 0.2 * (1 - normalize_inverse(interest_rate, 0, 10))  # 금리 높을수록 수비적
    score += 0.1 * (1 - normalize_inverse(inflation_rate, 100, 500))  # 물가 높을수록 수비적
    score += 0.1 * (1 - normalize_inverse(unemployment_rate, 0, 50))  # 실업률 높을수록 수비적
    score += 0.1 * (1 - normalize_inverse(vix, 0, 100))  # VIX 높을수록 수비적
    scores[sym] = max(0, min(score, 1))  # 위험 성향 점수: 0 ~ 1
return scores

2025-05-31 02:17:39 [INFO] rebalance: [Index 기반 리밸런싱 결과]
2025-05-31 02:17:39 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-31 02:17:39 [INFO] rebalance: - 최종 자산가치: 25,884.15만원
2025-05-31 02:17:39 [INFO] rebalance: - 누적 수익률: 215.70%
2025-05-31 02:17:39 [INFO] rebalance: - CAGR: 7.99%
2025-05-31 02:17:39 [INFO] rebalance: - 최대 낙폭(MDD): -11.60%
2025-05-31 02:17:39 [INFO] rebalance: - Calmar: 0.69%
2025-05-31 02:17:39 [INFO] rebalance: - 샤프지수: 1.30
```

```
은퇴 후
2025-05-31 02:13:53 [INFO] rebalance: [Index 기반 리밸런싱 결과]
2025-05-31 02:13:53 [INFO] rebalance: - 총 불입액: 100.00만원
2025-05-31 02:13:53 [INFO] rebalance: - 최종 자산가치: 390.13만원
2025-05-31 02:13:53 [INFO] rebalance: - 누적 수익률: 390.13%
2025-05-31 02:13:53 [INFO] rebalance: - CAGR: 14.58%
2025-05-31 02:13:53 [INFO] rebalance: - 최대 낙폭(MDD): -16.19%
2025-05-31 02:13:53 [INFO] rebalance: - Calmar: 0.90%
2025-05-31 02:13:53 [INFO] rebalance: - 샤프지수: 0.22
```

결론
- 8% 언저리의 CAGR
- 10% 미만의 MDD 달성 가능
- Calmar: 0.77%로 비교 불가
</details>

<details>
<summary>Experiment 2</summary>
</details>