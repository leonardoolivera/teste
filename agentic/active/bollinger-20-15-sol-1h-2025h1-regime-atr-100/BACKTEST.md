# BACKTEST.md - AF.3

> Gate: **backtest**.

## Dataset

solusdt_1h_20250105_20250704_binance_spot (4344 barras, 2025-H1).

## Métricas baseline

| Métrica | Valor |
|---------|------:|
| trades | 86 |
| hit_rate | 0.5814 |
| final_equity | 9770.68 |
| max_drawdown | 0.0883 |

## Stress

- spread+10bps: 9427.48 (ratio 0.9649)

## Monte Carlo

- p5: 8908.24

## Comparação cross-window (SOL)

- 2024 (in-sample): hit 66.67% fe 11210
- 2025-H1 (este piloto): hit 58.14% fe 9770.68
- 2025-H2 (AD/AC): hit 46.67% fe 9264
