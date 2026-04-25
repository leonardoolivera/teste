# BACKTEST.md - AD.2

> Gate: **backtest**.

## Dataset

solusdt_1h_20250705_20251231_binance_spot (4320 barras, Binance Vision spot).

## Métricas baseline

| Métrica | Valor |
|---------|------:|
| trades | 75 |
| hit_rate | 0.4667 |
| final_equity | 9264.75 |
| max_drawdown | 0.0904 |

## Stress (ADR-0019 42+ confirmações)

- fee+10bps: 8966.53
- spread+10bps: 8966.53 (≡ fee+10)
- ratio spread+10/baseline: 0.9678

## Monte Carlo (N=1000, seed=42)

- p5: 8559.28
- p50: ~baseline

## Comparação com referência

- AC.1 (ETH 20/1.5+atr:105 OOS 2025): fe=10465, hit=64.15% (EDGE PRESERVED)
- AD.2 (SOL): fe=9264.75, hit=46.67%
