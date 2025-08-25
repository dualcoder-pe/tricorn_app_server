### Experiments
<details>
<summary>Experiment 1</summary>

```
TLT 포함 비율
2025-05-29 00:44:12 [INFO] rebalance: [동적 리밸런싱 결과]
2025-05-29 00:44:12 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-29 00:44:12 [INFO] rebalance: - 최종 자산가치: 3,859.05만원
2025-05-29 00:44:12 [INFO] rebalance: - 누적 수익률: 32.16%
2025-05-29 00:44:12 [INFO] rebalance: - CAGR: -10.72%
2025-05-29 00:44:12 [INFO] rebalance: - 최대 낙폭(MDD): -24.44%
2025-05-29 00:44:12 [INFO] rebalance: - Calmar: -0.44%
2025-05-29 00:44:12 [INFO] rebalance: - 샤프지수: 0.81
```

```
DRAWDOWN_ALLOC_TABLE = pd.DataFrame(
    [
        # drawdown, QQQ, SPY, SCHD, BTC
        [-5, 0.135, 0.14, 0.14, 0.04],
        [-10, 0.15, 0.16, 0.16, 0.04],
        [-15, 0.165, 0.18, 0.18, 0.04],
        [-20, 0.18, 0.20, 0.20, 0.04],
        [-25, 0.195, 0.20, 0.20, 0.04],
        [-30, 0.20, 0.20, 0.20, 0.04],
    ],
    columns=["drawdown", Symbol.QQQ, Symbol.SPY, Symbol.SCHD, Symbol.BTC],
)

# =====================
# 상승장 비중 테이블 정의
# =====================
# readme.MD 기준, 상승폭(%)별 성장자산 비중
UPWARD_ALLOC_TABLE = pd.DataFrame(
    [
        # upward, QQQ, SPY, SCHD, BTC
        [-5, 0.20, 0.20, 0.20, 0.05],
        [0, 0.18, 0.175, 0.175, 0.05],
        [5, 0.16, 0.15, 0.15, 0.05],
        [10, 0.14, 0.125, 0.125, 0.05],
        [15, 0.12, 0.12, 0.12, 0.05],
        [20, 0.12, 0.12, 0.12, 0.04],
    ],
    columns=["upward", Symbol.QQQ, Symbol.SPY, Symbol.SCHD, Symbol.BTC],
)

DEFENSE_WEIGHTS_RATIO = {
    Symbol.USDT: 5 / 7,
    Symbol.GOLD: 2 / 7,
}

2025-05-29 00:57:59 [INFO] rebalance: [동적 리밸런싱 결과]
2025-05-29 00:57:59 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-29 00:57:59 [INFO] rebalance: - 최종 자산가치: 26,431.55만원
2025-05-29 00:57:59 [INFO] rebalance: - 누적 수익률: 220.26%
2025-05-29 00:57:59 [INFO] rebalance: - CAGR: 8.22%
2025-05-29 00:57:59 [INFO] rebalance: - 최대 낙폭(MDD): -11.65%
2025-05-29 00:57:59 [INFO] rebalance: - Calmar: 0.71%
2025-05-29 00:57:59 [INFO] rebalance: - 샤프지수: 1.30
```

```
CHANGE_ALLOC_TABLE = pd.DataFrame(
    [
        # change, QQQ, SPY, SCHD, BTC
        [25, 0.15, 0.12, 0.12, 0.04],
        [20, 0.16, 0.12, 0.12, 0.04],
        [15, 0.17, 0.12, 0.12, 0.05],
        [10, 0.18, 0.125, 0.125, 0.05],
        [5, 0.19, 0.15, 0.15, 0.05],
        [0, 0.20, 0.175, 0.175, 0.05],
        [-5, 0.12, 0.14, 0.14, 0.04],
        [-10, 0.14, 0.16, 0.16, 0.04],
        [-15, 0.16, 0.18, 0.18, 0.04],
        [-20, 0.18, 0.20, 0.20, 0.04],
        [-25, 0.20, 0.20, 0.20, 0.05],
    ],
    columns=["change", Symbol.QQQ, Symbol.SPY, Symbol.SCHD, Symbol.BTC],
)

2025-05-29 01:14:17 [INFO] rebalance: [동적 리밸런싱 결과]
2025-05-29 01:14:17 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-29 01:14:17 [INFO] rebalance: - 최종 자산가치: 26,760.41만원
2025-05-29 01:14:17 [INFO] rebalance: - 누적 수익률: 223.00%
2025-05-29 01:14:17 [INFO] rebalance: - CAGR: 8.35%
2025-05-29 01:14:17 [INFO] rebalance: - 최대 낙폭(MDD): -12.01%
2025-05-29 01:14:17 [INFO] rebalance: - Calmar: 0.70%
2025-05-29 01:14:17 [INFO] rebalance: - 샤프지수: 1.30
```

```
CHANGE_ALLOC_TABLE = pd.DataFrame(
    [
        # change, QQQ, SPY, SCHD, BTC
        [25, 0.12, 0.12, 0.12, 0.04],
        [20, 0.14, 0.14, 0.14, 0.04],
        [15, 0.16, 0.16, 0.16, 0.05],
        [10, 0.18, 0.18, 0.18, 0.05],
        [5, 0.19, 0.19, 0.19, 0.05],
        [0, 0.20, 0.20, 0.20, 0.05],
        [-5, 0.135, 0.14, 0.14, 0.04],
        [-10, 0.15, 0.16, 0.16, 0.04],
        [-15, 0.165, 0.18, 0.18, 0.04],
        [-20, 0.18, 0.20, 0.20, 0.04],
        [-25, 0.195, 0.20, 0.20, 0.05],
        [-30, 0.20, 0.20, 0.20, 0.05],
    ],
    columns=["change", Symbol.QQQ, Symbol.SPY, Symbol.SCHD, Symbol.BTC],
)

DEFENSE_WEIGHTS_RATIO = {
    Symbol.USDT: 5 / 7,
    Symbol.GOLD: 2 / 7,
}

2025-05-29 01:21:17 [INFO] rebalance: [동적 리밸런싱 결과]
2025-05-29 01:21:17 [INFO] rebalance: - 총 불입액: 12,000.00만원
2025-05-29 01:21:17 [INFO] rebalance: - 최종 자산가치: 27,038.13만원
2025-05-29 01:21:17 [INFO] rebalance: - 누적 수익률: 225.32%
2025-05-29 01:21:17 [INFO] rebalance: - CAGR: 8.46%
2025-05-29 01:21:17 [INFO] rebalance: - 최대 낙폭(MDD): -12.97%
2025-05-29 01:21:17 [INFO] rebalance: - Calmar: 0.65%
2025-05-29 01:21:17 [INFO] rebalance: - 샤프지수: 1.30
```
결론
- Calmar는 마지막이 가장 안좋지만, 그 이전의 수식이 논리적이지가 않아서 Overfitting으로 추정
</details>