# BACKTEST.md - AD.3

> Gate: **backtest**.

## Dataset

ethusdt_1h_20250705_20251231_binance_spot (4320 barras, Binance Vision spot).

## Métricas baseline

| Métrica | Valor |
|---------|------:|
| trades | 107 |
| hit_rate | 0.6262 |
| final_equity | 10071.02 |
| max_drawdown | 0.0681 |

## Stress (ADR-0019 42+ confirmações)

- fee+10bps: 9643.32
- spread+10bps: 9643.32 (≡ fee+10)
- ratio spread+10/baseline: 0.9575

## Monte Carlo (N=1000, seed=42)

- p5: 9112.19
- p50: ~baseline

## Comparação com referência

- AC.1 (ETH 20/1.5+atr:105 OOS 2025): fe=10465, hit=64.15% (EDGE PRESERVED)
- AD.3 (ETH): fe=10071.02, hit=62.62%
