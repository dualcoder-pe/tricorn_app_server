<details>
<summary>Experiment 1</summary>

```
GROWTH_WEIGHTS_BY_ZONE = {
    1: 0.20,  # 1구간 이하
    2: 0.18,  # 2구간
    3: 0.16,  # 3구간
    4: 0.14,  # 4구간
    5: 0.12,  # 5구간 이상
}

DEFENSE_WEIGHTS_RATIO = {
    Symbol.USDT: 5 / 7,
    Symbol.GOLD: 2 / 7,
}

2025-05-29 01:25:36 [INFO] rebalance: [동적 5MA 기반 리밸런싱 결과]
2025-05-29 01:25:36 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-29 01:25:36 [INFO] rebalance: - 최종 자산가치: 39,274.52만원
2025-05-29 01:25:36 [INFO] rebalance: - 누적 수익률: 327.29%
2025-05-29 01:25:36 [INFO] rebalance: - CAGR: 12.59%
2025-05-29 01:25:36 [INFO] rebalance: - 최대 낙폭(MDD): -22.48%
2025-05-29 01:25:36 [INFO] rebalance: - Calmar: 0.56%
2025-05-29 01:25:36 [INFO] rebalance: - 샤프지수: 1.33
```

```
GROWTH_WEIGHTS_BY_ZONE = {
    1: 0.20,  # 1구간 이하
    2: 0.18,  # 2구간
    3: 0.16,  # 3구간
    4: 0.14,  # 4구간
    5: 0.12,  # 5구간 이상
}

# =====================
# 안정자산 비중 배분 규칙
# =====================
# 성장자산 비중을 제외한 나머지를 아래 비율로 분배
DEFENSE_WEIGHTS_RATIO = {
    Symbol.USDT: 4 / 7,
    Symbol.GOLD: 2 / 7,
    Symbol.TLT: 1 / 7,
}
2025-05-29 01:28:31 [INFO] rebalance: [동적 5MA 기반 리밸런싱 결과]
2025-05-29 01:28:31 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-29 01:28:31 [INFO] rebalance: - 최종 자산가치: 38,484.91만원
2025-05-29 01:28:31 [INFO] rebalance: - 누적 수익률: 320.71%
2025-05-29 01:28:31 [INFO] rebalance: - CAGR: 12.36%
2025-05-29 01:28:31 [INFO] rebalance: - 최대 낙폭(MDD): -24.24%
2025-05-29 01:28:31 [INFO] rebalance: - Calmar: 0.51%
2025-05-29 01:28:31 [INFO] rebalance: - 샤프지수: 1.33

2025-05-29 01:28:31 [INFO] rebalance: [동적 20MA 기반 리밸런싱 결과]
2025-05-29 01:28:31 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-29 01:28:31 [INFO] rebalance: - 최종 자산가치: 35,479.97만원
2025-05-29 01:28:31 [INFO] rebalance: - 누적 수익률: 295.67%
2025-05-29 01:28:31 [INFO] rebalance: - CAGR: 11.45%
2025-05-29 01:28:31 [INFO] rebalance: - 최대 낙폭(MDD): -25.12%
2025-05-29 01:28:31 [INFO] rebalance: - Calmar: 0.46%
2025-05-29 01:28:31 [INFO] rebalance: - 샤프지수: 1.31

2025-05-29 01:28:31 [INFO] rebalance: [동적 60MA 기반 리밸런싱 결과]
2025-05-29 01:28:31 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-29 01:28:31 [INFO] rebalance: - 최종 자산가치: 36,003.81만원
2025-05-29 01:28:31 [INFO] rebalance: - 누적 수익률: 300.03%
2025-05-29 01:28:31 [INFO] rebalance: - CAGR: 11.61%
2025-05-29 01:28:31 [INFO] rebalance: - 최대 낙폭(MDD): -22.52%
2025-05-29 01:28:31 [INFO] rebalance: - Calmar: 0.52%
2025-05-29 01:28:31 [INFO] rebalance: - 샤프지수: 1.32

2025-05-29 01:28:31 [INFO] rebalance: [동적 120MA 기반 리밸런싱 결과]
2025-05-29 01:28:31 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-29 01:28:31 [INFO] rebalance: - 최종 자산가치: 35,339.90만원
2025-05-29 01:28:31 [INFO] rebalance: - 누적 수익률: 294.50%
2025-05-29 01:28:31 [INFO] rebalance: - CAGR: 11.41%
2025-05-29 01:28:31 [INFO] rebalance: - 최대 낙폭(MDD): -23.74%
2025-05-29 01:28:31 [INFO] rebalance: - Calmar: 0.48%
2025-05-29 01:28:31 [INFO] rebalance: - 샤프지수: 1.31

2025-05-29 01:28:31 [INFO] rebalance: [동적 앙상블 MA 기반 리밸런싱 결과]
2025-05-29 01:28:31 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-29 01:28:31 [INFO] rebalance: - 최종 자산가치: 36,334.28만원
2025-05-29 01:28:31 [INFO] rebalance: - 누적 수익률: 302.79%
2025-05-29 01:28:31 [INFO] rebalance: - CAGR: 11.72%
2025-05-29 01:28:31 [INFO] rebalance: - 최대 낙폭(MDD): -23.90%
2025-05-29 01:28:31 [INFO] rebalance: - Calmar: 0.49%
2025-05-29 01:28:31 [INFO] rebalance: - 샤프지수: 1.32
```
결론: 여기서도 TLT는 의미 없다.
</details>
