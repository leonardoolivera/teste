# BACKTEST.md - AF.1

> Gate: **backtest**.

## Dataset

btcusdt_1h_20250105_20250704_binance_spot (4344 barras, 2025-H1).

## Métricas baseline

| Métrica | Valor |
|---------|------:|
| trades | 67 |
| hit_rate | 0.5821 |
| final_equity | 10360.46 |
| max_drawdown | 0.0258 |

## Stress

- spread+10bps: 10092.02 (ratio 0.9741)

## Monte Carlo

- p5: 9784.76

## Comparação cross-window (BTC)

- 2024 (in-sample): hit 72.62% fe 10474
- 2025-H1 (este piloto): hit 58.21% fe 10360.46
- 2025-H2 (AD/AC): hit 44.44% fe 9985
