# BACKTEST.md - AF.2

> Gate: **backtest**.

## Dataset

ethusdt_1h_20250105_20250704_binance_spot (4344 barras, 2025-H1).

## Métricas baseline

| Métrica | Valor |
|---------|------:|
| trades | 62 |
| hit_rate | 0.6290 |
| final_equity | 10376.26 |
| max_drawdown | 0.0421 |

## Stress

- spread+10bps: 10127.76 (ratio 0.9761)

## Monte Carlo

- p5: 9788.95

## Comparação cross-window (ETH)

- 2024 (in-sample): hit 63.16% fe 10540
- 2025-H1 (este piloto): hit 62.90% fe 10376.26
- 2025-H2 (AD/AC): hit 64.15% fe 10465
