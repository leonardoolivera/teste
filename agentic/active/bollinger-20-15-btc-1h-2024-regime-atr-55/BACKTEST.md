# BACKTEST.md - AE.1

> Gate: **backtest**.

## Dataset

btcusdt_1h_20240705_20241231_binance_spot (4320 barras, 2024-H2).

## Métricas baseline

| Métrica | Valor |
|---------|------:|
| trades | 84 |
| hit_rate | 0.7262 |
| final_equity | 10474.48 |
| max_drawdown | 0.0361 |

## Stress

- spread+10bps: 10137.88 (ratio 0.9679)

## Monte Carlo

- p5: 10240.76

## Comparação in-sample vs OOS

- AE.1 2024 (BTC): fe 10474.48, hit 72.62%
- AD equivalente 2025: fe 9985 hit 44.44% FAIL
