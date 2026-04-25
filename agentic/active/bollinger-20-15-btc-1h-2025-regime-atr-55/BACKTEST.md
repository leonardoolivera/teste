# BACKTEST.md - AD.1

> Gate: **backtest**.

## Dataset

btcusdt_1h_20250705_20251231_binance_spot (4320 barras, Binance Vision spot).

## Métricas baseline

| Métrica | Valor |
|---------|------:|
| trades | 54 |
| hit_rate | 0.4444 |
| final_equity | 9985.53 |
| max_drawdown | 0.0241 |

## Stress (ADR-0019 42+ confirmações)

- fee+10bps: 9769.78
- spread+10bps: 9769.78 (≡ fee+10)
- ratio spread+10/baseline: 0.9784

## Monte Carlo (N=1000, seed=42)

- p5: 9558.47
- p50: ~baseline

## Comparação com referência

- AC.1 (ETH 20/1.5+atr:105 OOS 2025): fe=10465, hit=64.15% (EDGE PRESERVED)
- AD.1 (BTC): fe=9985.53, hit=44.44%
